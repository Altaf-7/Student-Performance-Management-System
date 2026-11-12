from django import template
from django.core.exceptions import FieldDoesNotExist
import re

register = template.Library()

@register.filter(name='getattr')
def getattr_filter(obj, args):
    """
    Try to get an attribute from an object.
    Supports relational fields using '__' e.g., 'department__name'
    """
    try:
        if '__' in args:
            parts = args.split('__')
            val = obj
            for part in parts:
                val = getattr(val, part)
            return val
        
        return getattr(obj, args)
    except AttributeError:
        return None
