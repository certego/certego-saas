from django.db import models
from django.db.models import Q


class ToggleableModelManager(models.Manager):
    """
    For :class:`certego_saas.ext.models.ToggleableModel`.
    """

    def enabled(self):
        return super().get_queryset().filter(enabled=True)

    def disabled(self):
        return super().get_queryset().filter(enabled=False)

    def valid_elements(self, user):
        from certego_saas.apps.organization.models import Organization

        org_query = Q(user=user) | Q(
            user__membership__organization_id=Organization.certego().pk
        )
        if user.has_membership():
            org_query |= Q(
                user__membership__organization_id=user.membership.organization_id
            )
        return self.enabled().filter(org_query)


class _AppSpecificQuerySet(models.QuerySet):
    def get_currentapp(self):
        return self.get(appname=self.model.AppChoices.CURRENTAPP)

    def filter_currentapp(self):
        return self.filter(appname=self.model.AppChoices.CURRENTAPP)


class AppSpecificModelManager(models.Manager):
    """
    For :class:`certego_saas.ext.models.AppSpecificModel`.
    """

    def get_queryset(self):
        return _AppSpecificQuerySet(self.model, using=self._db, hints=self._hints)

    def get_currentapp(self):
        return super().get_queryset().get_currentapp()

    def filter_currentapp(self):
        return super().get_queryset().filter_currentapp()
