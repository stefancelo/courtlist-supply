from django.db import models


class Team(models.Model):
    """A Euroleague club. Used as a user's club and, later, in the gameweek fixtures."""

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    city = models.CharField(max_length=60)
    country = models.CharField(max_length=60)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name