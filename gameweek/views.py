from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import CommentForm
from .models import Comment, Fixture, Prediction

def current_round():
    """The round of the next game to start, or of the latest game if every game has started."""
    fixture = (
        Fixture.objects.filter(tip_off__gte=timezone.now()).order_by("tip_off").first()
        or Fixture.objects.order_by("-tip_off").first()
    )
    return fixture.round_number if fixture else None


def with_votes(fixtures):
    """Adds each fixture's prediction counts (counted by the database) and comment count."""
    return fixtures.select_related("home_team", "away_team").annotate(
        home_votes=Count("predictions", filter=Q(predictions__winner=F("home_team")), distinct=True),
        away_votes=Count("predictions", filter=Q(predictions__winner=F("away_team")), distinct=True),
    )


def add_vote_split(fixture):
    """Turns a fixture's vote counts into whole percentages for the vote bar."""
    fixture.total_votes = fixture.home_votes + fixture.away_votes
    fixture.home_percent = round(100 * fixture.home_votes / fixture.total_votes) if fixture.total_votes else 50
    fixture.away_percent = 100 - fixture.home_percent
    return fixture

def round_messages(round_number, after=0):
    """The round's chat messages, oldest first, optionally only those newer than message id `after`."""
    return Comment.objects.filter(round_number=round_number, pk__gt=after).select_related(
        "user__club", "fixture__home_team", "fixture__away_team"
    )


def save_message(form, user, round_number):
    """Saves a valid chat form as the given user's message in the given round."""
    message = form.save(commit=False)
    message.user = user
    message.round_number = round_number
    message.save()

def gameweek(request):
    """This round's fixtures with prediction results, the user's own picks, the countdown
    to the next tip-off and the round's discussion. Everyone can read; predicting and
    posting need an account (comments are posted to this same page)."""
    round_number = current_round()
    form = CommentForm(round_number=round_number)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        form = CommentForm(request.POST, round_number=round_number)
        if form.is_valid() and round_number is not None:
            save_message(form, request.user, round_number)
            return redirect(reverse("gameweek:index") + "#discussion")
    fixtures = [add_vote_split(fixture) for fixture in with_votes(Fixture.objects.filter(round_number=round_number))]

    if request.user.is_authenticated:
        picks = dict(
            Prediction.objects.filter(user=request.user, fixture__round_number=round_number)
            .values_list("fixture_id", "winner_id")
        )
        for fixture in fixtures:
            fixture.my_pick = picks.get(fixture.pk)

    next_fixture = next((fixture for fixture in fixtures if not fixture.has_started), None)
    context = {
        "round_number": round_number,
        "fixtures": fixtures,
        "next_fixture": next_fixture,
        "comments": round_messages(round_number),
        "form": form,
    }
    return render(request, "gameweek/gameweek.html", context)



def parse_id(value):
    """Turns a posted id into a whole number; anything else becomes None."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@login_required
@require_POST
def predict(request, pk):
    """Saves the user's pick for a fixture (new or changed). Called by fetch, it answers
    with the refreshed vote bar as HTML; without JavaScript it redirects back.
    Picks are refused from tip-off and for any team not playing in the game."""
    fixture = get_object_or_404(Fixture, pk=pk)
    is_fetch = request.headers.get("X-Requested-With") == "fetch"
    team_id = parse_id(request.POST.get("winner"))

    if fixture.has_started:
        error = "Predictions for this game are closed."
    elif team_id not in (fixture.home_team_id, fixture.away_team_id):
        error = "Pick one of the two teams in this game."
    else:
        error = None

    if error:
        if is_fetch:
            return JsonResponse({"ok": False, "message": error}, status=400)
        messages.error(request, error)
        return redirect("gameweek:index")

    Prediction.objects.update_or_create(user=request.user, fixture=fixture, defaults={"winner_id": team_id})

    if is_fetch:
        updated = add_vote_split(with_votes(Fixture.objects.filter(pk=fixture.pk)).get())
        bar_html = render_to_string("gameweek/partials/vote_bar.html", {"fixture": updated})
        return JsonResponse({"ok": True, "bar_html": bar_html})
    messages.success(request, "Your prediction is saved.")
    return redirect("gameweek:index")




@require_http_methods(["GET", "POST"])
def chat(request):
    """The live chat's data, as JSON.
    GET (polled every few seconds by chat.js): the messages newer than ?after=<id>.
    POST (logged-in users): saves a message, then returns the new messages, the sender's included.
    Each message comes as ready-made HTML from the same partial the page uses."""
    round_number = current_round()
    after = parse_id(request.GET.get("after")) or 0

    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"ok": False, "message": "Log in to send messages."}, status=403)
        form = CommentForm(request.POST, round_number=round_number)
        if not form.is_valid():
            error = " ".join(str(message) for errors in form.errors.values() for message in errors)
            return JsonResponse({"ok": False, "message": error}, status=400)
        save_message(form, request.user, round_number)

    new_messages = [
        {
            "id": message.pk,
            "html": render_to_string("gameweek/partials/chat_message.html", {"comment": message}, request=request),
        }
        for message in round_messages(round_number, after)
    ]
    return JsonResponse({"ok": True, "messages": new_messages})