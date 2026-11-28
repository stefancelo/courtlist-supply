from django.urls import path

from . import views

app_name = "gameweek"

urlpatterns = [
    path("", views.gameweek, name="index"),
    path("<int:pk>/predict/", views.predict, name="predict"),
    path("chat/", views.chat, name="chat"),
]