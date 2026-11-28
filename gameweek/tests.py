from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User

from .models import Comment, Fixture, Prediction, Team

FETCH = {"X-Requested-With": "fetch"}


class GameweekTests(TestCase):
    """Checks predictions (changeable until tip-off, only for the two teams) and the chat
    (public to read, logged-in to post, topics only from the current round)."""

    @classmethod
    def setUpTestData(cls):
        cls.par = Team.objects.create(name="Partizan", slug="partizan", code="PAR", city="Belgrade", country="Serbia")
        cls.rma = Team.objects.create(name="Real Madrid", slug="real-madrid", code="RMA", city="Madrid", country="Spain")
        cls.oly = Team.objects.create(name="Olympiacos", slug="olympiacos", code="OLY", city="Piraeus", country="Greece")
        now = timezone.now()
        cls.game = Fixture.objects.create(round_number=13, home_team=cls.par, away_team=cls.rma, tip_off=now + timedelta(days=2))
        cls.old_game = Fixture.objects.create(round_number=12, home_team=cls.rma, away_team=cls.oly, tip_off=now - timedelta(days=5))
        cls.fan = User.objects.create_user(username="fan", password="Test-pass-2026")

    def setUp(self):
        self.client.force_login(self.fan)

    def test_pick_can_be_changed_before_tip_off(self):
        url = reverse("gameweek:predict", args=[self.game.pk])
        self.client.post(url, {"winner": self.par.pk}, headers=FETCH)
        response = self.client.post(url, {"winner": self.rma.pk}, headers=FETCH)

        self.assertTrue(response.json()["ok"])
        self.assertEqual(Prediction.objects.get().winner, self.rma)

    def test_pick_after_tip_off_is_refused(self):
        url = reverse("gameweek:predict", args=[self.old_game.pk])
        response = self.client.post(url, {"winner": self.rma.pk}, headers=FETCH)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Prediction.objects.exists())

    def test_team_not_in_the_game_is_refused(self):
        url = reverse("gameweek:predict", args=[self.game.pk])
        response = self.client.post(url, {"winner": self.oly.pk}, headers=FETCH)

        self.assertEqual(response.status_code, 400)

    def test_visitor_can_read_the_chat_but_not_post(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("gameweek:chat")).status_code, 200)

        response = self.client.post(reverse("gameweek:chat"), {"text": "Hello"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Comment.objects.exists())

    def test_message_can_be_tagged_with_a_game_of_this_round(self):
        response = self.client.post(reverse("gameweek:chat"), {"fixture": self.game.pk, "text": "Partizan by ten!"})

        self.assertTrue(response.json()["ok"])
        self.assertEqual(Comment.objects.get().fixture, self.game)

    def test_game_from_another_round_is_refused_as_topic(self):
        response = self.client.post(reverse("gameweek:chat"), {"fixture": self.old_game.pk, "text": "Old news"})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Comment.objects.exists())