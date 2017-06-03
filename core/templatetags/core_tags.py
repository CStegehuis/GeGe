from django import template
from core.models import *

register = template.Library()

@register.inclusion_tag('core/tags/categories.html', takes_context=True)
def categories(context):
    return {
        'categories': BlogCategory.objects.all(),
        'request': context['request'],
    }

@register.inclusion_tag('core/tags/reeksen.html', takes_context=True)
def reeksen(context):
    return {
        'reeksen': BlogReeks.objects.all(),
        'request': context['request'],
    }