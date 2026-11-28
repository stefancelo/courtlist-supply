from django.contrib import admin

from .models import Comment, Fixture, Prediction, Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "country"]
    search_fields = ["name", "city"]
    prepopulated_fields = {"slug": ["name"]}



@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ["__str__", "round_number", "tip_off", "home_score", "away_score"]
    list_filter = ["round_number"]
    list_editable = ["home_score", "away_score"]


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ["user", "fixture", "winner", "updated_at"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["user", "round_number", "created_at"]
    search_fields = ["text", "user__username"]