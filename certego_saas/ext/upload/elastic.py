import datetime
import logging
from typing import Any, Dict, Tuple

from django.utils.timezone import now
from elasticsearch.helpers import bulk

logger = logging.getLogger(__name__)

import elasticsearch


class __BIDocumentInterface:
    index: str
    timestamp: datetime
    application: str
    environment: str

    kwargs: Dict[str, str]

    def to_json(self) -> Dict[str, Any]:
        res = {
            "timestamp": self.timestamp,
            "application": self.application,
            "environment": self.environment,
            **self.kwargs,
        }
        logger.debug(f"Json document: {res}")
        return res

    def to_bulk(self) -> Dict[str, Any]:
        return {
            "_op_type": "index",
            "_index": self.index + "-" + now().strftime("%Y.%m"),
            "_source": self.to_json(),
        }

    @classmethod
    def upload(
        cls,
        client: elasticsearch.Elasticsearch,
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
        jsons = map(lambda x: x.to_bulk(), docs)
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
        return f"|{self.index=}, {self.application=}, {self.environment=}, {self.kwargs=}"


try:
    from mongoengine import Document
    from mongoengine import fields as mongo_fields

except ImportError:
    from django.db.models import Index, JSONField, Model
    from django.db.models import fields as django_fields

    class BIDocument(__BIDocumentInterface, Model):
        index = django_fields.CharField(max_length=100)
        timestamp = django_fields.DateTimeField(auto_now_add=True)
        application = django_fields.CharField(max_length=100)
        environment = django_fields.CharField(max_length=100)
        kwargs = JSONField()

        class Meta:
            indexes = [Index(fields=["index"]), Index(fields=["timestamp"])]

else:

    class BIDocument(__BIDocumentInterface, Document):
        index = mongo_fields.StringField(required=True)
        timestamp = mongo_fields.DateTimeField(
            required=True, default=datetime.datetime.now
        )
        application = mongo_fields.StringField(required=True)
        environment = mongo_fields.StringField(required=True)
        kwargs = mongo_fields.DictField(required=False)
        meta = {"indexes": ["index", "timestamp"]}
