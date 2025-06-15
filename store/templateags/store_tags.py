from django import template
from store.models import Category

register = template.Library()

@register.inclusion_tag('base.html')
def category_list():
    return {'categories': Category.objects.all()}
