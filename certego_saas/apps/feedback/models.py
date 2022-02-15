from django.conf import settings
from django.db import models

from certego_saas.ext.models import AppSpecificModel, TimestampedModel
from certego_saas.ext.upload import Slack

__all__ = [
    "UserFeedback",
]


class UserFeedback(TimestampedModel, AppSpecificModel):
    class Meta:
        verbose_name_plural = "User Feedbacks"

    FEEDBACK_CATEGORIES = [
        ("BUG_REPORT", "BUG_REPORT"),
        ("FEATURE_REQUEST", "FEATURE_REQUEST"),
        ("OTHER", "OTHER"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="feedbacks",
    )
    category = models.CharField(max_length=32, choices=FEEDBACK_CATEGORIES)
    message = models.TextField(null=False, blank=False)

    def send_to_slack(self):
        slack = Slack()
        try:
            slack.send_message(
                title=f"[{self.appname}] New Feedback by {self.user.username}",
                body=f"Category: *{self.category}*"
                + "\n"
                + "Message:"
                + "\n"
                + f"> {self.message}",
            )
        except Slack.SlackApiError as exc:
            slack.log.error(
                f"Slack message failed for feedback(#{self.pk}) with error: {str(exc)}"
            )
