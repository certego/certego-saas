from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserCreateForm(UserCreationForm):
    """
    Extending django's ``UserCreationForm`` to add required fields
    as given in the ``User.REQUIRED_FIELDS``.
    """

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(UserCreateForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        for field_name in User.REQUIRED_FIELDS:
            self.fields[field_name].required = True
