from django.shortcuts import render


def home(request):
    """Home page: introduces CourtList Supply and what it sells."""
    return render(request, "core/home.html")