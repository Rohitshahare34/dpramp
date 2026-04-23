from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Parses a string and splits it by the argument."""
    return [item.strip() for item in value.split(arg) if item.strip()]

@register.filter(name='strip')
def strip(value):
    """Strips whitespace from a string."""
    return value.strip()
