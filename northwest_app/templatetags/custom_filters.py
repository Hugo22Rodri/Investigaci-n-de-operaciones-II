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


@register.filter
def cell_class(cell):
    """Devuelve clases CSS para una celda de la matriz usada en plantillas Vogel.

    - Si la celda fue operada en un paso, devuelve clases para resaltarla.
    - Si es ficticia, añade estilo en cursiva/tono claro.
    - Si la celda tiene allocation == 0, añade una clase ligera.
    """
    try:
        classes = []
        if not isinstance(cell, dict):
            return ''
        if cell.get('step_operated'):
            classes.append('table-success')
            classes.append('vogel-step-cell')
        if cell.get('is_fictitious'):
            classes.append('fst-italic')
            classes.append('text-muted')
        if cell.get('allocation') == 0:
            classes.append('table-secondary')
        return ' '.join(classes)
    except Exception:
        return ''

