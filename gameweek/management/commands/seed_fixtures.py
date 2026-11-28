"""seed_fixtures: creates one Euroleague round: the 20 clubs paired into 10 games on the
next Thursday and Friday, plus a few demo predictions and comments so the Gameweek page
isn't empty.

Usage:  python manage.py seed_fixtures                 (round 13)
        python manage.py seed_fixtures --round 14

Running it again replaces that round, so its games always lie in the coming days.
"""

import random
from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from gameweek.models import Comment, Fixture, Prediction, Team

# (days after Thursday, local tip-off time): five games on Thursday, five on Friday
TIP_OFFS = [
    (0, time(19, 45)), (0, time(20, 0)), (0, time(20, 30)), (0, time(21, 0)), (0, time(21, 15)),
    (1, time(19, 45)), (1, time(20, 0)), (1, time(20, 30)), (1, time(21, 0)), (1, time(21, 15)),
]

DEMO_USERS = ["demo_fan", "demo_staff", "staff_olympiacos", "staff_real_madrid", "staff_zalgiris"]

# (game number in the round, or None for General, message)
DEMO_COMMENTS = [
    (None, "Big round this week, who's everyone backing?"),
    (1, "Home court will decide this one."),
    (1, "No chance, their guards have been on fire lately."),
    (None, "Whoever wins the rebounding battles wins the round."),
    (3, "Can't wait for this one, it should be close until the last minute."),
]


def next_thursday():
    """The next Thursday after today (a week ahead if today is Thursday)."""
    today = timezone.localdate()
    days_ahead = (3 - today.weekday()) % 7 or 7  # Monday is 0, Thursday is 3
    return today + timedelta(days=days_ahead)


class Command(BaseCommand):
    help = "Creates one round of 10 fixtures on the next Thursday and Friday, with demo predictions and comments."

    def add_arguments(self, parser):
        parser.add_argument("--round", type=int, default=13, dest="round_number")

    @transaction.atomic
    def handle(self, *args, **options):
        round_number = options["round_number"]
        teams = list(Team.objects.order_by("name"))
        if len(teams) < 2:
            raise CommandError("Run seed_teams first: there are no clubs.")

        rng = random.Random(round_number)
        rng.shuffle(teams)
        Fixture.objects.filter(round_number=round_number).delete()
        Comment.objects.filter(round_number=round_number).delete()

        thursday = next_thursday()
        pairs = zip(teams[0::2], teams[1::2])
        fixtures = []
        for (home, away), (day_offset, at) in zip(pairs, TIP_OFFS):
            tip_off = timezone.make_aware(datetime.combine(thursday + timedelta(days=day_offset), at))
            fixtures.append(
                Fixture.objects.create(round_number=round_number, home_team=home, away_team=away, tip_off=tip_off)
            )

        voters = list(User.objects.filter(username__in=DEMO_USERS))
        predictions = 0
        for fixture in fixtures:
            for person in voters:
                if rng.random() < 0.7:
                    winner = rng.choice([fixture.home_team, fixture.away_team])
                    Prediction.objects.create(user=person, fixture=fixture, winner=winner)
                    predictions += 1

        comments = 0
        if voters:
            for game, text in DEMO_COMMENTS:
                fixture = fixtures[game] if game is not None else None
                Comment.objects.create(round_number=round_number, fixture=fixture, user=rng.choice(voters), text=text)
                comments += 1

        friday = thursday + timedelta(days=1)
        self.stdout.write(
            self.style.SUCCESS(
                f"Round {round_number}: {len(fixtures)} games on {thursday:%d %b} and {friday:%d %b}, "
                f"with {predictions} predictions and {comments} comments."
            )
        )