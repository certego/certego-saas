import logging

from django.conf import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from certego_saas.settings import certego_apps_settings

__all__ = [
    "Slack",
]
logger = logging.getLogger(__name__)


class _Slack:
    def create_msg(self, title: str, body: str, urgent: bool) -> str:
        msg = f"*{title.title()}*\n{body}"
        if urgent:
            msg = msg.upper()
        if hasattr(settings, "STAGE") and isinstance(settings.STAGE, str):
            msg = f"`{settings.STAGE.upper()} INSTANCE`:\n{msg}"
        return msg

    def send_message(
        self, title: str, body: str = "", urgent: bool = False, channel=None
    ):
        msg = self.create_msg(title, body, urgent)
        logger.info(f"Slack Message: {msg}")


if settings.DEBUG or certego_apps_settings.TESTING:

    Slack = _Slack

else:

    class Slack(_Slack):

        token = certego_apps_settings.SLACK_TOKEN
        channel = certego_apps_settings.SLACK_CHANNEL

        client = WebClient(token=token)

        def send_message(
            self, title: str, body: str = "", urgent: bool = False, channel=None
        ):
            super().send_message(title, body, urgent, channel)
            if channel is None:
                channel = self.channel
            message = self.create_msg(title, body, urgent)
            try:
                return self.client.chat_postMessage(
                    channel=channel, text=message, mrkdwn=True
                )
            except SlackApiError as e:
                logger.exception(e)
                raise e
