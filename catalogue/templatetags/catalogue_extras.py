from django import template

register = template.Library()


@register.filter
def star_icons(value):
    """Turns an average rating into the five Bootstrap icon names to show, to the nearest half star.
    3.6 -> ["star-fill", "star-fill", "star-fill", "star-half", "star"]"""
    rounded = round((value or 0) * 2) / 2
    icons = []
    for position in range(1, 6):
        if rounded >= position:
            icons.append("star-fill")
        elif rounded >= position - 0.5:
            icons.append("star-half")
        else:
            icons.append("star")
    return icons