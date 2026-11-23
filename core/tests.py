from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage


class HomePageTests(TestCase):
    """Checks that the home page loads and uses the shared layout."""

    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")
        self.assertTemplateUsed(response, "base.html")

    def test_about_page_shows_team_initials(self):
        response = self.client.get(reverse("core:about"))
        self.assertContains(response, "Stefan Lazarevic")
        self.assertContains(response, ">SL<")

    

class ContactPageTests(TestCase):
    """Checks that valid messages are saved and invalid ones are rejected."""

    def test_valid_message_is_saved_and_redirects(self):
        data = {
            "name": "Stefan",
            "email": "stefan@example.com",
            "subject": "Shot clock",
            "message": "The shot clock in hall B needs a new horn.",
        }
        response = self.client.post(reverse("core:contact"), data)

        self.assertRedirects(response, reverse("core:contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_short_message_is_rejected(self):
        data = {"name": "S", "email": "not-an-email", "subject": "Hi", "message": "Short"}
        response = self.client.post(reverse("core:contact"), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(response, "Enter at least 10 characters.")