"""seed_teams: loads the 20 clubs of the 2026-27 Euroleague season.

Usage:  python manage.py seed_teams

Safe to run more than once: clubs are matched by their slug and updated, never duplicated.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from gameweek.models import Team

# (name, 3-letter code, city, country) for every club in the 2026-27 Euroleague season
TEAMS = [
    ("Anadolu Efes", "EFS", "Istanbul", "Turkey"),
    ("Baskonia", "BKN", "Vitoria-Gasteiz", "Spain"),
    ("Beşiktaş", "BJK", "Istanbul", "Turkey"),
    ("Crvena Zvezda", "CZV", "Belgrade", "Serbia"),
    ("Dubai Basketball", "DUB", "Dubai", "United Arab Emirates"),
    ("FC Barcelona", "BAR", "Barcelona", "Spain"),
    ("FC Bayern Munich", "BAY", "Munich", "Germany"),
    ("Fenerbahçe", "FEN", "Istanbul", "Turkey"),
    ("Hapoel Tel Aviv", "HTA", "Tel Aviv", "Israel"),
    ("LDLC ASVEL", "ASV", "Villeurbanne", "France"),
    ("Maccabi Tel Aviv", "MTA", "Tel Aviv", "Israel"),
    ("Olimpia Milano", "MIL", "Milan", "Italy"),
    ("Olympiacos", "OLY", "Piraeus", "Greece"),
    ("Panathinaikos", "PAO", "Athens", "Greece"),
    ("Paris Basketball", "PRS", "Paris", "France"),
    ("Partizan", "PAR", "Belgrade", "Serbia"),
    ("Real Madrid", "RMA", "Madrid", "Spain"),
    ("Valencia Basket", "VAL", "Valencia", "Spain"),
    ("Virtus Bologna", "VIR", "Bologna", "Italy"),
    ("Žalgiris", "ZAL", "Kaunas", "Lithuania"),
]


class Command(BaseCommand):
    help = "Creates or updates the 20 Euroleague clubs of the 2026-27 season."

    def handle(self, *args, **options):
        for name, code, city, country in TEAMS:
            Team.objects.update_or_create(
                slug=slugify(name),
                defaults={"name": name, "code": code, "city": city, "country": country},
            )
        self.stdout.write(self.style.SUCCESS(f"{len(TEAMS)} Euroleague clubs ready."))