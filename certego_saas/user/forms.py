from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class UserCreateForm(UserCreationForm):
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
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True
