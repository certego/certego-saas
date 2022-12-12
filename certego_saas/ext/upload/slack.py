import abc
import logging
from typing import Type, Union

from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from certego_saas.settings import certego_apps_settings

__all__ = [
    "Slack",
]


class _SlackInterface(metaclass=abc.ABCMeta):


    @property
    def log(self):
        return logging.getLogger(f"certego_saas.{self.__class__.__name__}")

    @abc.abstractmethod
    def send_message(
        self, title: str, body: str = "", urgent: bool = False, channel=None
    ):
        pass

if settings.DEBUG or certego_apps_settings.TESTING:
    class Slack(_SlackInterface):
        def send_message(
            self, title: str, body: str = "", urgent: bool = False, channel=None
        ):
            self.log.info(f"{title}\n{body}")

else:
    class Slack(_SlackInterface):
        """
        Slack client.
        """

        token = certego_apps_settings.SLACK_TOKEN
        channel = certego_apps_settings.SLACK_CHANNEL

        client = WebClient(token=token)

        def send_message(
            self, title: str, body: str = "", urgent: bool = False, channel=None
        ):
            """
            To send message to a channel.
            """
            if channel is None:
                channel = self.channel
            message = f"*{title.title()}*\n{body}"
            if urgent:
                message = message.upper()
            message = f"`{settings.STAGE.upper()} INSTANCE`:\n{message}"
            try:
                return self.client.chat_postMessage(
                    channel=channel, text=message, mrkdwn=True
                )
            except SlackApiError as e:
                self.log.exception(e)
                raise e