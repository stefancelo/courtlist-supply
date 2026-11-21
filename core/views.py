from django.shortcuts import render

# The four supply areas shown on the home page, written once as data
FEATURES = [
    {
        "icon": "bi-dribbble",
        "title": "Game equipment",
        "text": "Official-size balls, shot clocks and scoreboard parts for every game night.",
    },
    {
        "icon": "bi-bucket",
        "title": "Court care",
        "text": "Floor tape, dust mops and towels to keep the court safe and game-ready.",
    },
    {
        "icon": "bi-bandaid",
        "title": "Medical",
        "text": "First aid kits, ice packs and recovery gear for the medical staff.",
    },
    {
        "icon": "bi-person-badge",
        "title": "Staff apparel",
        "text": "Polos and jackets in your club colours for the whole operations team.",
    },
]


def home(request):
    """Home page: introduces CourtList Supply and what it sells."""
    return render(request, "core/home.html", {"features": FEATURES})