import abc
import datetime
import enum
from importlib import util
import logging
from typing import List, Union, Dict, overload, Tuple, Any

from django.db.models import Model, JSONField, QuerySet
from django.db.models import fields as django_fields
from elasticsearch.helpers import bulk
from mongoengine import Document
from mongoengine import fields as mongo_fields

logger = logging.getLogger(__name__)

import elasticsearch


class __BIDocumentInterface(abc.ABC):
    index: str
    creation_date: datetime
    category:str
    count: int
    kwargs: Dict[str, str]
    objects: QuerySet

    def to_json(self) -> Dict[str, Any]:
        return {
            "timestamp" : self.creation_date,
            "bi_category": self.category,
            "count": self.count,
            **self.kwargs
        }

    def to_bulk(self) -> Dict[str, Any]:
        return {
                "_op_type": "index",
                "_index": self.index,
                "_type": "_doc",
                "_source": self.to_json(),
            }

    @classmethod
    def upload(cls, client: elasticsearch.Elasticsearch, index:str, timeout:int=30, max_number:int=None) -> Tuple:
        docs = cls.objects.filter(index=index).order_by("+time")
        if max_number:
            docs = docs[:max_number]
        jsons = map(lambda x: x.to_bulk(), docs)
        success, errors = bulk(
            client,
            jsons,
            request_timeout=timeout
        )
        docs.delete()
        return success, errors

    def clean(self):
        self.kwargs = {key.replace("__", "."): value for key, value in self.kwargs.items()}



if util.find_spec("mongoengine"):
    class BIDocument(__BIDocumentInterface, Document):
        index = mongo_fields.StringField(required=True)
        creation_date = mongo_fields.DateTimeField(required=True, default=datetime.datetime.now)
        category = mongo_fields.StringField(required=True)
        count = mongo_fields.IntField(required=True, min_value=0)
        kwargs = mongo_fields.DictField(required=False, null=True)

else:
    class BIDocument(__BIDocumentInterface, Model):
        index = django_fields.CharField(max_length=100)
        creation_date = django_fields.DateTimeField(auto_now_add=True)
        category = django_fields.CharField(max_length=100)
        count = django_fields.PositiveIntegerField()
        kwargs = JSONField()

