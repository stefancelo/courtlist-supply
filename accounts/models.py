from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """A CourtList user: Django's built-in user plus their club and phone number."""

    class PhonePrefix(models.TextChoices):
        BOSNIA = "+387", "Bosnia and Herzegovina (+387)"
        CROATIA = "+385", "Croatia (+385)"
        CYPRUS = "+357", "Cyprus (+357)"
        FRANCE = "+33", "France (+33)"
        GERMANY = "+49", "Germany (+49)"
        GREECE = "+30", "Greece (+30)"
        ISRAEL = "+972", "Israel (+972)"
        ITALY = "+39", "Italy (+39)"
        LITHUANIA = "+370", "Lithuania (+370)"
        MONTENEGRO = "+382", "Montenegro (+382)"
        NORTH_MACEDONIA = "+389", "North Macedonia (+389)"
        SERBIA = "+381", "Serbia (+381)"
        SLOVENIA = "+386", "Slovenia (+386)"
        SPAIN = "+34", "Spain (+34)"
        TURKEY = "+90", "Turkey (+90)"
        UAE = "+971", "United Arab Emirates (+971)"
        UK = "+44", "United Kingdom (+44)"
        USA = "+1", "United States / Canada (+1)"

    club = models.ForeignKey(
        "gameweek.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    phone_prefix = models.CharField("country code", max_length=5, choices=PhonePrefix.choices, blank=True)
    phone = models.CharField(
        "phone number",
        max_length=14,
        blank=True,
        validators=[
            RegexValidator(r"^\d{6,14}$", "Enter 6 to 14 digits, without spaces or the country code."),
        ],
    )

    def __str__(self):
        return self.username