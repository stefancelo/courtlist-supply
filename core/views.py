from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm

# The four areas of the site, shown as cards on the home page
FEATURES = [
    {
        "icon": "bi-trophy",
        "title": "Gameweek predictions",
        "text": "Pick the winner of every Euroleague game this week and see how other fans voted.",
    },
    {
        "icon": "bi-chat-dots",
        "title": "Fan discussion",
        "text": "Talk matchups and tactics with other fans in each game's discussion.",
    },
    {
        "icon": "bi-kanban",
        "title": "Staff tasks",
        "text": "CourtList staff plan every matchday job on a task list and a Kanban board.",
    },
    {
        "icon": "bi-bag",
        "title": "CourtList Supply",
        "text": "Staff order game equipment, medical supplies and apparel from our own shop.",
    },
]

# What the site offers, listed on the About page
ABOUT_FEATURES = [
    "Weekly game predictions with live vote results",
    "A discussion box for every game, open to registered fans",
    "Staff task list and drag-and-drop Kanban board",
    "Staff-only supply shop with search, filters and ratings",
    "Personal recommendations and order history",
    "Admin panel and sales analytics",
    "Dark mode that remembers your choice",
]

TEAM = [
    {"name": "Stefan Lazarevic", "role": "Developer & Founder", "bio": "Built CourtList from the first sketch to the live site."},
    {"name": "Dante Exum", "role": "Operations Manager", "bio": "Defines matchday workflows and what the task board tracks."},
    {"name": "Ilija Srdanovic", "role": "Planning Manager", "bio": "Coordinates officials and makes sure crews are confirmed on time."},
    {"name": "Kostas Sloukas", "role": "Media Coordinator", "bio": "Runs the fan side: predictions, discussion and game-week content."},
]

# Steps of the build, shown in the About page carousel
MILESTONES = [
    {"icon": "bi-lightbulb", "title": "1. Built around the Euroleague", "text": "The 20 clubs of the 2026-27 season are the base for every fixture, prediction and user profile."},
    {"icon": "bi-layout-text-window", "title": "2. Shared templates", "text": "One base template with blocks and small partials, so no page repeats the layout."},
    {"icon": "bi-database", "title": "3. Database models", "text": "Teams, fixtures, predictions, comments, tasks, items, orders and ratings, all linked together."},
    {"icon": "bi-shield-lock", "title": "4. Roles and security", "text": "Visitors, fans, staff and admins each see exactly what they are allowed to."},
    {"icon": "bi-graph-up", "title": "5. Shop and analytics", "text": "A staff supply shop with recommendations, and an admin dashboard built from real data."},
]


def get_initials(name):
    """'Stefan Lazarevic' -> 'SL'"""
    return "".join(part[0] for part in name.split())[:2].upper()


def home(request):
    """Home page: introduces CourtList and its four areas."""
    return render(request, "core/home.html", {"features": FEATURES})


def about(request):
    """About page: what CourtList offers, the team, and how it was built."""
    team = [dict(member, initials=get_initials(member["name"])) for member in TEAM]
    context = {"features": ABOUT_FEATURES, "team": team, "milestones": MILESTONES}
    return render(request, "core/about.html", context)



def contact(request):
    """Contact page. GET shows an empty form; POST checks it, saves the message
    and redirects back with a confirmation (Post/Redirect/Get)."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save()
            messages.success(
                request,
                f"Thanks, {message.name}. We received your message and will reply to {message.email}.",
            )
            return redirect("core:contact")
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"form": form})