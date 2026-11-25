from .roles import is_courtlist_staff


def roles(request):
    """Adds is_courtlist_staff to every template, e.g. to show the Shop link only to staff."""
    return {"is_courtlist_staff": is_courtlist_staff(request.user)}