import abc
import logging
import re
from typing import List, Union

import twitter as twitter_lib
from django.conf import settings
from django.db import models
from django.utils.html import strip_tags

from certego_saas.settings import certego_apps_settings

__all__ = [
    "Twitter",
]


class _TwitterInterface(metaclass=abc.ABCMeta):
    @property
    def log(self):
        return logging.getLogger(f"certego_saas.{self.__class__.__name__}")

    @abc.abstractmethod
    def post_tweet(
        self,
        msg: str,
        media: List[Union[str, models.FileField]] = None,
        header: str = None,
    ):
        pass


class _FakeTwitter(_TwitterInterface):
    def post_tweet(
        self,
        msg: str,
        media: List[Union[str, models.FileField]] = None,
        header: str = None,
    ):
        self.log.debug(f"{header if header else ''}:  {msg}")


class _Twitter(_TwitterInterface):
    """
    Twitter client.
    """

    CHARACTER_LIMIT = twitter_lib.api.CHARACTER_LIMIT
    client = twitter_lib.Api(
        consumer_key=certego_apps_settings.TWITTER_CONSUMER_KEY,
        consumer_secret=certego_apps_settings.TWITTER_CONSUMER_SECRET,
        access_token_key=certego_apps_settings.TWITTER_TOKEN_KEY,
        access_token_secret=certego_apps_settings.TWITTER_TOKEN_SECRET,
    )

    def __init__(self):
        if not self.client.VerifyCredentials():
            raise Exception("Wrong credentials")

    @staticmethod
    def __parse(msg) -> List[str]:
        return re.findall(r'href=[\'"]?([^\'" >]+)', msg)

    def post_tweet(
        self,
        msg: str,
        media: List[Union[str, models.FileField]] = None,
        header: str = None,
    ):
        """
        To post a tweet.
        """
        urls = self.__parse(msg)
        msg = strip_tags(msg)
        msg += " ".join(urls)
        # i wanna add a custom delimiter + initial message
        if header:
            msg = header + " " + msg
        size = self.CHARACTER_LIMIT - 9
        if len(msg) >= self.CHARACTER_LIMIT:
            # splitting the text in N messages
            messages = [msg[i : i + size] for i in range(0, len(msg), size)]
            # adding 0/10, 1/10 to the end of the messages
            messages = [
                msg + f" {i}/{len(messages) - 1}" for i, msg in enumerate(messages)
            ]
        else:
            messages = [msg]
        self.log.info(messages)
        result_id = self.client.PostUpdate(status=messages[0], media=media).id
        for msg in messages[1:]:
            result_id = self.client.PostUpdate(
                status=msg, in_reply_to_status_id=result_id
            ).id


#: Twitter Client
Twitter = _FakeTwitter if settings.STAGE_LOCAL or settings.STAGE_CI else _Twitter
