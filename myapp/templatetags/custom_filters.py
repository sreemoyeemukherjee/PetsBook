# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()


@register.filter(name='split_tags')
def split_tags(tags_string):
    return tags_string.split(';')[:-1]
