"""seed_users: creates the CourtList staff group and the three demo accounts
(admin, staff member, fan) listed in the submission's links file.

Usage:  python manage.py seed_users

The password comes from the DEMO_PASSWORD environment variable (.env),
so it is never written in the code. Safe to run more than once.
"""

import os

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from accounts.roles import STAFF_GROUP
from gameweek.models import Team

DEMO_USERS = [
    {"username": "demo_admin", "first_name": "Elena", "last_name": "Papadopoulou", "role": "admin", "club": None},
    {"username": "demo_staff", "first_name": "Nikos", "last_name": "Georgiou", "role": "staff", "club": "panathinaikos"},
    {"username": "demo_fan", "first_name": "Marko", "last_name": "Jovanovic", "role": "fan", "club": "partizan"},
]


class Command(BaseCommand):
    help = "Creates the CourtList staff group and the demo admin, staff and fan accounts."

    def handle(self, *args, **options):
        password = os.environ.get("DEMO_PASSWORD")
        if not password:
            raise CommandError("Set DEMO_PASSWORD in .env before running this command.")

        staff_group, _ = Group.objects.get_or_create(name=STAFF_GROUP)

        for data in DEMO_USERS:
            user, _ = User.objects.get_or_create(username=data["username"])
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.email = f"{data['username']}@courtlist.com"
            user.club = Team.objects.filter(slug=data["club"]).first() if data["club"] else None

            # Only the admin gets full rights and access to the Django admin
            is_admin = data["role"] == "admin"
            user.is_superuser = is_admin
            user.is_staff = is_admin

            user.set_password(password)
            user.save()

            if data["role"] == "staff":
                user.groups.add(staff_group)
            else:
                user.groups.remove(staff_group)

        self.stdout.write(self.style.SUCCESS("Staff group and 3 demo accounts ready."))