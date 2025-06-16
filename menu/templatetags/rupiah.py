# app_name/templatetags/rupiah.py
from django import template

register = template.Library()

@register.filter
def rupiah(value):
    try:
        value = float(value)
        return "Rp {:,.2f}".format(value).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return value