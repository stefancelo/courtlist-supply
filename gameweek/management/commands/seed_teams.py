"""seed_teams: loads the 20 clubs of the 2026-27 Euroleague season.

Usage:  python manage.py seed_teams

Safe to run more than once: clubs are matched by their slug and updated, never duplicated.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from gameweek.models import Team

# (name, city, country) for every club in the 2026-27 Euroleague season
TEAMS = [
    ("Anadolu Efes", "Istanbul", "Turkey"),
    ("Baskonia", "Vitoria-Gasteiz", "Spain"),
    ("Beşiktaş", "Istanbul", "Turkey"),
    ("Crvena Zvezda", "Belgrade", "Serbia"),
    ("Dubai Basketball", "Dubai", "United Arab Emirates"),
    ("FC Barcelona", "Barcelona", "Spain"),
    ("FC Bayern Munich", "Munich", "Germany"),
    ("Fenerbahçe", "Istanbul", "Turkey"),
    ("Hapoel Tel Aviv", "Tel Aviv", "Israel"),
    ("LDLC ASVEL", "Villeurbanne", "France"),
    ("Maccabi Tel Aviv", "Tel Aviv", "Israel"),
    ("Olimpia Milano", "Milan", "Italy"),
    ("Olympiacos", "Piraeus", "Greece"),
    ("Panathinaikos", "Athens", "Greece"),
    ("Paris Basketball", "Paris", "France"),
    ("Partizan", "Belgrade", "Serbia"),
    ("Real Madrid", "Madrid", "Spain"),
    ("Valencia Basket", "Valencia", "Spain"),
    ("Virtus Bologna", "Bologna", "Italy"),
    ("Žalgiris", "Kaunas", "Lithuania"),
]


class Command(BaseCommand):
    help = "Creates or updates the 20 Euroleague clubs of the 2026-27 season."

    def handle(self, *args, **options):
        for name, city, country in TEAMS:
            Team.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "city": city, "country": country},
            )
        self.stdout.write(self.style.SUCCESS(f"{len(TEAMS)} Euroleague clubs ready."))