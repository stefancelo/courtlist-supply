from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import redirect, render

from catalogue.models import Item
from catalogue.recommender import recommend_for

from .roles import is_courtlist_staff

from .forms import ProfileForm, RegisterForm


def register(request):
    """Sign-up page for fans. A new account is logged in straight away."""
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CourtList, {user.first_name}!")
            return redirect("accounts:dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    """Shows and updates the logged-in user's own details. The form always edits
    request.user, so nobody can open or change another person's profile."""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})


@login_required
def dashboard(request):
    """The logged-in user's personal page. Everyone sees their predictions and latest chat
    messages; staff also see recommendations, recently viewed items, orders and ratings."""
    user = request.user
    context = {
        "predictions": user.predictions.select_related(
            "fixture__home_team", "fixture__away_team", "winner"
        ).order_by("-fixture__tip_off")[:10],
        "chat_messages": user.comments.select_related(
            "fixture__home_team", "fixture__away_team"
        ).order_by("-created_at")[:5],
    }

    if is_courtlist_staff(user):
        context |= {
            "recommendations": recommend_for(user),
            "recent_items": (
                Item.objects.filter(views__user=user, is_active=True)
                .annotate(last_viewed=Max("views__viewed_at"))
                .order_by("-last_viewed")[:4]
            ),
            "orders": user.orders.prefetch_related("lines")[:3],
            "ratings": user.ratings.select_related("item")[:5],
        }

    return render(request, "accounts/dashboard.html", context)