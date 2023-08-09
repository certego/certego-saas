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

logger = logging.getLogger(__name__)


class _Twitter:
    @staticmethod
    def __get_urls(msg) -> List[str]:
        return re.findall(r'href=[\'"]?([^\'" >]+)', msg)

    def create_messages(
        self, msg: str, header: Union[None, str], max_char: int
    ) -> List[str]:
        urls = self.__get_urls(msg)
        msg = strip_tags(msg)
        msg += " ".join(urls)
        # i wanna add a custom delimiter + initial message
        if header:
            msg = header + " " + msg
        size = max_char - 9
        if len(msg) >= max_char:
            # splitting the text in N messages
            messages = [msg[i : i + size] for i in range(0, len(msg), size)]
            # adding 0/10, 1/10 to the end of the messages
            messages = [
                msg + f" {i}/{len(messages) - 1}" for i, msg in enumerate(messages)
            ]
        else:
            messages = [msg]
        return messages

    def post_tweet(
        self,
        msg: str,
        media: List[Union[str, models.FileField]] = None,
        header: str = None,
    ):
        for i, message in enumerate(self.create_messages(msg, header, max_char=50)):
            logger.info(f"Tweet {i}: {message}")


if settings.DEBUG or certego_apps_settings.TESTING:
    Twitter = _Twitter

else:

    class Twitter(_Twitter):
        CHARACTER_LIMIT = twitter_lib.api.CHARACTER_LIMIT
        client = twitter_lib.Api(
            consumer_key=certego_apps_settings.TWITTER_CONSUMER_KEY,
            consumer_secret=certego_apps_settings.TWITTER_CONSUMER_SECRET,
            access_token_key=certego_apps_settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=certego_apps_settings.TWITTER_ACCESS_TOKEN_SECRET,
        )

        def __init__(self):
            if not self.client.VerifyCredentials():
                raise Exception("Wrong credentials")

        def post_tweet(
            self,
            msg: str,
            media: List[Union[str, models.FileField]] = None,
            header: str = None,
        ):
            super().post_tweet(msg, media, header)
            messages = self.create_messages(msg, header, self.CHARACTER_LIMIT)
            result_id = self.client.PostUpdate(status=messages[0], media=media).id
            for msg in messages[1:]:
                result_id = self.client.PostUpdate(
                    status=msg, in_reply_to_status_id=result_id
                ).id
