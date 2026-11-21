from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """A CourtList Supply user: Django's built-in user plus club details."""

    club = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.username
