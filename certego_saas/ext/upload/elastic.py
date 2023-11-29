import datetime
import logging
from typing import Any, Dict, Tuple

from elasticsearch.helpers import bulk

logger = logging.getLogger(__name__)

import elasticsearch


class __BIDocumentInterface:
    index: str
    creation_date: datetime
    category: str
    count: int
    kwargs: Dict[str, str]

    def to_json(self) -> Dict[str, Any]:
        res = {
            "timestamp": self.creation_date,
            "bi_category": self.category,
            "count": self.count,
            **self.kwargs,
        }
        logger.debug(f"Json document: {res}")
        return res

    def to_bulk(self) -> Dict[str, Any]:
        return {
            "_op_type": "index",
            "_index": self.index,
            "_type": "_doc",
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
        docs = qs.order_by("+creation_date")
        if max_number:
            docs = docs[:max_number]
        num_docs = docs.count()
        logger.info(f"Uploading {num_docs} documents")
        jsons = map(lambda x: x.to_bulk(), docs)
        success, errors = bulk(client, jsons, request_timeout=timeout)
        logger.info(f"Finished Upload. Deleting {num_docs} documents")
        for doc in docs.iterator():
            doc.delete()
        logger.info(f"Finished deleting {num_docs} documents")
        return success, errors

    def clean(self):
        self.kwargs = {
            key.replace("__", "."): value for key, value in self.kwargs.items()
        }

    def __repr__(self):
        return f"|{self.index=}, {self.category=}, {self.count=}, {self.kwargs=}"


try:
    from mongoengine import Document
    from mongoengine import fields as mongo_fields

except ImportError:
    from django.db.models import Index, JSONField, Model
    from django.db.models import fields as django_fields

    class BIDocument(__BIDocumentInterface, Model):
        index = django_fields.CharField(max_length=100)
        creation_date = django_fields.DateTimeField(auto_now_add=True)
        category = django_fields.CharField(max_length=100)
        count = django_fields.PositiveIntegerField()
        kwargs = JSONField()

        class Meta:
            indexes = [Index(fields=["index"]), Index(fields=["creation_date"])]

else:

    class BIDocument(__BIDocumentInterface, Document):
        index = mongo_fields.StringField(required=True)
        creation_date = mongo_fields.DateTimeField(
            required=True, default=datetime.datetime.now
        )
        category = mongo_fields.StringField(required=True)
        count = mongo_fields.IntField(required=True, min_value=0)
        kwargs = mongo_fields.DictField(required=False)
        meta = {"indexes": ["index", "creation_date"]}
