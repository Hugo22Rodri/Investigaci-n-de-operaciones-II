from django import template

register = template.Library()

@register.filter
def get_item(lst, i):
    try:
        return lst[i]
    except:
        return None

@register.filter
def index(lst, i):
    try:
        return lst[i]
    except:
        return None

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def format_sub(value, arg):
    """Return a string like 'a - b = c' where a=value and b=arg.

    If either is not numeric, returns empty string.
    """
    try:
        a = int(value)
        b = int(arg)
        return f"{a} - {b} = {a - b}"
    except (ValueError, TypeError):
        return ''