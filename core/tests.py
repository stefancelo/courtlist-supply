from django.test import TestCase
from django.urls import reverse


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