from django import template

register = template.Library()

@register.filter
def add_days_simple(value, days):
    """Versión simple para usar con {% now %}"""
    from datetime import datetime, timedelta
    return datetime.now() + timedelta(days=int(days))

@register.filter
def sum_subtotal(detalles):
    """Suma los subtotales de los detalles"""
    try:
        return sum(detalle.subtotal for detalle in detalles)
    except (AttributeError, TypeError):
        return 0

@register.filter
def sum_attr(queryset, attr):
    """Suma un atributo de un queryset"""
    try:
        return sum(getattr(obj, attr, 0) for obj in queryset)
    except (AttributeError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiplica value * arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
    # En custom_filters.py, agrega:
from django.db import models

@register.filter
def get_model_name(obj):
    """Obtener el nombre del modelo en minúsculas"""
    if hasattr(obj, '_meta'):
        return obj._meta.model_name  # Esto devuelve 'alimento', 'accesorio', 'mascota'
    elif isinstance(obj, models.Model):
        return obj.__class__.__name__.lower()
    return ''

@register.filter 
def get_model_type(obj):
    """Versión alternativa que detecta el tipo por clase"""
    if hasattr(obj, 'id_alimentos'):
        return 'alimento'
    elif hasattr(obj, 'id_accesorio'):
        return 'accesorio'
    elif hasattr(obj, 'id_mascotas'):
        return 'mascota'
    return ''

@register.filter
def get_id(obj):
    """Obtener el ID correcto según el tipo de modelo"""
    if hasattr(obj, 'id_alimentos'):
        return obj.id_alimentos
    elif hasattr(obj, 'id_accesorio'):
        return obj.id_accesorio
    elif hasattr(obj, 'id_mascotas'):
        return obj.id_mascotas
    elif hasattr(obj, 'id'):
        return obj.id
    return 0

# Mantén los otros filtros que ya tienes
@register.filter
def add_days_simple(value, days):
    """Versión simple para usar con {% now %}"""
    from datetime import datetime, timedelta
    return datetime.now() + timedelta(days=int(days))

@register.filter
def sum_subtotal(detalles):
    try:
        return sum(detalle.subtotal for detalle in detalles)
    except:
        return 0

@register.filter
def sum_attr(queryset, attr):
    """Suma un atributo de un queryset"""
    return sum(getattr(obj, attr, 0) for obj in queryset)

@register.filter
def multiply(value, arg):
    """Multiplica value * arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
 @register.filter
def sum_attr(queryset, attr):
    """Suma un atributo de un queryset"""
    try:
        return sum(getattr(obj, attr, 0) for obj in queryset)
    except (TypeError, ValueError, AttributeError):
        return 0

@register.filter 
def first(queryset):
    """Obtener el primer elemento de un queryset"""
    try:
        return queryset.first()
    except:
        return None   