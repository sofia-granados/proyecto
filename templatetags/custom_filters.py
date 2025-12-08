# app_mascotas/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica value por arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        try:
            return value * arg
        except:
            return 0

@register.filter
def sum_subtotal(detalles):
    """Suma los subtotales de los detalles"""
    try:
        return sum(detalle.subtotal for detalle in detalles)
    except:
        return 0

@register.filter
def add(value, arg):
    """Suma value y arg"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        try:
            return value + arg
        except:
            return value

@register.filter
def multiply_then_add(value, arg1, arg2):
    """Multiplica value por arg1 y luego suma arg2"""
    try:
        return (float(value) * float(arg1)) + float(arg2)
    except:
        return value

@register.filter
def calculate_iva(value):
    """Calcula el IVA (16%) de un valor"""
    try:
        return float(value) * 0.16
    except:
        return 0