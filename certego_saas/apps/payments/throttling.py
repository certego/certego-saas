from abc import ABCMeta, abstractmethod

from django.utils import timezone
from rest_framework.exceptions import Throttled
from rest_framework.throttling import BaseThrottle


class SubscriptionRateThrottle(BaseThrottle, metaclass=ABCMeta):
    """
    Restrict access if
    :attr:`User.stripe.monthly_submissions_limit` has been exhausted.
    """

    @abstractmethod
    def is_quota_exhausted(self, request, view) -> bool:
        raise NotImplementedError()

    def allow_request(self, request, view):
        # check if monthly quota has been exhausted
        quota_exhausted = self.is_quota_exhausted(request, view)
        if quota_exhausted:
            raise Throttled(
                detail="Monthly max submissions quota exhausted.",
                wait=self.wait(),
            )

        return True

    def wait(self):
        """
        calculates distance in seconds
        from current time to 1st of next month.
        """
        fromdate = timezone.datetime.today()
        todate = fromdate
        while todate.day != 1:
            todate += timezone.timedelta(days=1)

        delta = todate - fromdate
        return delta.total_seconds()
