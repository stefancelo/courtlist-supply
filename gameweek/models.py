from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Team(models.Model):
    """A Euroleague club. Used as a user's club and, later, in the gameweek fixtures."""

    name = models.CharField(max_length=60, unique=True)
    code = models.CharField(max_length=3, default="", blank=True)
    slug = models.SlugField(max_length=60, unique=True)
    city = models.CharField(max_length=60)
    country = models.CharField(max_length=60)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Fixture(models.Model):
    """One game of a round: a home team against an away team, with its tip-off time.
    The scores stay empty until the game has been played."""

    round_number = models.PositiveSmallIntegerField()
    home_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="home_fixtures")
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="away_fixtures")
    tip_off = models.DateTimeField()
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["tip_off"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(home_team=models.F("away_team")),
                name="home_and_away_teams_differ",
            ),
        ]

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"

    @property
    def short_label(self):
        """'PAR vs RMA', using the clubs' 3-letter codes (or full names if a code is missing)."""
        return f"{self.home_team.code or self.home_team.name} vs {self.away_team.code or self.away_team.name}"

    @property
    def has_started(self):
        """True from tip-off onwards: predictions are then closed."""
        return timezone.now() >= self.tip_off


class Prediction(models.Model):
    """A user's pick for the winner of one fixture. One per user per fixture,
    and it can be changed until tip-off."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="predictions")
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE, related_name="predictions")
    winner = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "fixture"], name="one_prediction_per_user_per_fixture"),
        ]

    def __str__(self):
        return f"{self.user} picks {self.winner} in {self.fixture}"

    @property
    def outcome(self):
        """'correct' or 'wrong' once both scores are entered, or '' while the game hasn't been played."""
        fixture = self.fixture
        if fixture.home_score is None or fixture.away_score is None:
            return ""
        actual_winner = fixture.home_team_id if fixture.home_score > fixture.away_score else fixture.away_team_id
        return "correct" if self.winner_id == actual_winner else "wrong"


class Comment(models.Model):
    """A message in a round's discussion, shown under that round's predictions.
    Only logged-in users can post; only admins can delete."""

    round_number = models.PositiveSmallIntegerField()
    fixture = models.ForeignKey(
        Fixture,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} on round {self.round_number}"