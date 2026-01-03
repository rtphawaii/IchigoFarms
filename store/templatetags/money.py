from django import template

register = template.Library()

@register.filter
def money(cents):
    """
    Convert integer cents (e.g. 2000) to a dollar string (e.g. 20.00).
    """
    try:
        return f"{int(cents) / 100:.2f}"
    except (TypeError, ValueError):
        return "0.00"
