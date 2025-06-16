# menu/templatetags/custom_tags.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def slice_list(value, n):
    """
    Membagi list menjadi potongan dengan panjang n untuk tampilan kolom vertikal
    """
    n = int(n)
    return [value[i:i + n] for i in range(0, len(value), n)]