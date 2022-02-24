from rest_framework import serializers as rfs

from .models import UserFeedback

__all__ = [
    "UserFeedbackSerializer",
]


class UserFeedbackSerializer(rfs.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = rfs.ALL_FIELDS

    user = rfs.HiddenField(default=rfs.CurrentUserDefault())
    appname = rfs.HiddenField(default=UserFeedback.AppChoices.CURRENTAPP)

    def create(self, validated_data: dict) -> UserFeedback:
        """
        Create :class:`~.models.UserFeedback` model.
        """
        feedback = super().create(validated_data)
        # below function does not raise any exception
        # because we should not respond with error
        # if the slack API fails since it's an internal use-case
        feedback.send_to_slack()
        return feedback
