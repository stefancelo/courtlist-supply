from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from core.forms import BootstrapFormMixin

from .models import User


def email_is_taken(email, exclude_user=None):
    """True if another account already uses this email (capital letters ignored).
    exclude_user lets someone keep their own email when editing their profile."""
    users = User.objects.filter(email__iexact=email)
    if exclude_user is not None:
        users = users.exclude(pk=exclude_user.pk)
    return users.exists()


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    """Sign-up form for fans. Django's UserCreationForm checks the username and the
    two passwords; this form adds a required name, a unique email and an optional club."""

    email = forms.EmailField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "club"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["club"].label = "Club you support (optional)"
        self.fields["club"].empty_label = "No club chosen"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if email_is_taken(email):
            raise forms.ValidationError("An account with this email already exists.")
        return email


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    """Lets a logged-in user update their own details.
    The username and role are not in the list, so nobody can change their own access."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "club", "phone_prefix", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["club"].empty_label = "No club chosen"
        # The country code sits inside the phone box, so it gets a hidden label instead of a visible one
        self.fields["phone_prefix"].widget.attrs.update({"class": "form-select phone-prefix", "aria-label": "Country code"})

    def clean(self):
        """A phone number needs its country code, and a country code needs a number."""
        cleaned = super().clean()
        if bool(cleaned.get("phone")) != bool(cleaned.get("phone_prefix")):
            self.add_error("phone", "Enter both the country code and the number, or leave both empty.")
        return cleaned

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if email and email_is_taken(email, exclude_user=self.instance):
            raise forms.ValidationError("Another account already uses this email.")
        return email


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    """Django's login form (username and password check) with the site's Bootstrap styling."""