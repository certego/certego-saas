import datetime
import logging
from typing import Tuple

from django.utils.timezone import now
from elasticsearch.helpers import bulk
from rest_framework.fields import Field

logger = logging.getLogger(__name__)

import elasticsearch


class __AbstractBISerializer:
    application: Field
    environment: Field
    timestamp: Field

    @staticmethod
    def to_elastic_dict(data, index):
        return {
            "_source": data,
            "_index": index + "-" + data["environment"] + "-" + now().strftime("%Y.%m"),
            "_op_type": "index",
        }


class __BIDocumentInterface:
    timestamp: datetime
    application: str
    environment: str

    @classmethod
    def upload(
        cls,
        client: elasticsearch.Elasticsearch,
        serializer,
        index: str = None,
        timeout: int = 30,
        max_number: int = None,
    ) -> Tuple:
        qs = cls.objects
        if index:
            qs.filter(index=index)
        docs = qs.order_by("+timestamp")
        if max_number:
            if max_number > 10000:
                return False, [
                    "max_number can't be higher than 10000 for performance reasons."
                ]
            docs = docs[:max_number]
        logger.info(f"Uploading {docs.count()} documents")
        jsons = serializer(instance=docs, many=True).data
        logger.info(f"Documents to upload: {jsons}")
        success, errors = bulk(client, jsons, request_timeout=timeout)
        logger.info("Finished Upload. Starting deletion documents")
        docs.delete()
        logger.info("Finished deleting documents")
        return success, errors

    def clean(self):
        self.kwargs = {
            key.replace("__", "."): value for key, value in self.kwargs.items()
        }

    def __repr__(self):
        return f"|{self.timestamp=}, {self.application=}, {self.environment=}"


try:
    from mongoengine import Document
    from mongoengine import fields as mongo_fields

except ImportError:
    from django.db.models import Index, JSONField, Model
    from django.db.models import fields as django_fields
    from rest_framework.fields import SerializerMethodField
    from rest_framework.serializers import ModelSerializer

    class BIDocument(__BIDocumentInterface, Model):
        index = django_fields.CharField(max_length=100)
        timestamp = django_fields.DateTimeField(auto_now_add=True)
        application = django_fields.CharField(max_length=100)
        environment = django_fields.CharField(max_length=100)
        kwargs = JSONField()

        class Meta:
            indexes = [Index(fields=["index"]), Index(fields=["timestamp"])]

    class BISerializer(__AbstractBISerializer, ModelSerializer):
        index = SerializerMethodField(method_name="get_index")

        class Meta:
            fields = [
                "application",
                "environment",
                "timestamp",
            ]

else:
    from rest_framework_mongoengine.serializers import DocumentSerializer

    class BIDocument(__BIDocumentInterface, Document):
        index = mongo_fields.StringField(required=True)
        timestamp = mongo_fields.DateTimeField(
            required=True, default=datetime.datetime.now
        )
        application = mongo_fields.StringField(required=True)
        environment = mongo_fields.StringField(required=True)
        kwargs = mongo_fields.DictField(required=False)
        meta = {"indexes": ["index", "timestamp"]}

    class BISerializer(__AbstractBISerializer, DocumentSerializer):
        class Meta:
            model = BIDocument
            fields = [
                "application",
                "environment",
                "timestamp",
            ]

        def to_representation(self, instance: BIDocument):
            data = super().to_representation(instance)
            for key, value in instance.kwargs.items():
                data[key] = value
            return self.to_elastic_dict(data, instance.index)
