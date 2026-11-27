from django.test import TestCase
from django.urls import reverse

from .forms import ProfileForm
from .models import User


class RegisterTests(TestCase):
    """Checks that registering creates a fan account and logs it in."""

    def test_register_creates_and_logs_in_fan(self):
        data = {
            "username": "newfan",
            "first_name": "New",
            "last_name": "Fan",
            "email": "New@Fan.com",
            "password1": "Courtside-2026!",
            "password2": "Courtside-2026!",
        }
        response = self.client.post(reverse("accounts:register"), data)

        self.assertRedirects(response, reverse("accounts:dashboard"))
        user = User.objects.get(username="newfan")
        self.assertEqual(user.email, "new@fan.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)


class ProfileFormTests(TestCase):
    """Checks the profile form's phone rule."""

    def test_phone_without_country_code_is_rejected(self):
        user = User.objects.create_user(username="someone", email="someone@example.com")
        data = {"first_name": "Some", "last_name": "One", "email": "someone@example.com", "phone": "6912345678"}
        form = ProfileForm(data, instance=user)

        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)




class DashboardTests(TestCase):
    """Checks who can open the dashboard and what fans see on it."""

    def test_dashboard_needs_login(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}")

    def test_fan_sees_no_shop_sections(self):
        fan = User.objects.create_user(username="fan", password="Test-pass-2026")
        self.client.force_login(fan)
        response = self.client.get(reverse("accounts:dashboard"))

        self.assertContains(response, "Hi, fan")
        self.assertNotContains(response, "Recommended for you")




class LoginTests(TestCase):
    """Checks the message a deactivated account gets."""

    def test_deactivated_account_with_right_password_is_told_so(self):
        User.objects.create_user(username="gone", password="Test-pass-2026", is_active=False)
        response = self.client.post(reverse("accounts:login"), {"username": "gone", "password": "Test-pass-2026"})

        self.assertContains(response, "This account has been deactivated")

    def test_deactivated_account_with_wrong_password_gets_general_message(self):
        User.objects.create_user(username="gone", password="Test-pass-2026", is_active=False)
        response = self.client.post(reverse("accounts:login"), {"username": "gone", "password": "wrong"})

        self.assertNotContains(response, "deactivated")