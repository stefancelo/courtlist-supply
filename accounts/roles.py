"""Role checks for CourtList. The one place that decides who counts as staff,
so views and templates never repeat the rule."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

# Name of the group the admin adds employees to
STAFF_GROUP = "CourtList staff"


def is_courtlist_staff(user):
    """True for admins (superusers) and members of the CourtList staff group."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name=STAFF_GROUP).exists()


def staff_required(view):
    """Protects a view so only CourtList staff and admins can open it.
    Visitors are sent to the login page; logged-in fans get "403 Forbidden"."""

    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_courtlist_staff(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper