# app_mascotas/context_processors.py
from django.conf import settings

def carrito_context(request):
    """Context processor para información del carrito - CON DEBUG"""
    print(f"🔍 DEBUG context_processor: Ejecutándose...")
    print(f"🔍 DEBUG: User: {request.user}")
    print(f"🔍 DEBUG: Autenticado: {request.user.is_authenticated}")
    
    carrito = request.session.get('carrito', {})
    print(f"🔍 DEBUG: Carrito items: {len(carrito)}")
    
    # Calcular total de items
    total_items = 0
    subtotal = 0
    
    for item in carrito.values():
        cantidad = item.get('cantidad', 0)
        precio = item.get('precio', 0)
        total_items += cantidad
        subtotal += precio * cantidad
    
    # Calcular IVA y total
    iva = subtotal * getattr(settings, 'IVA_PORCENTAJE', 0.16)
    total = subtotal + iva
    
    # Información del usuario
    usuario_autenticado = request.user.is_authenticated
    
    if usuario_autenticado:
        print(f"🔍 DEBUG: Usuario autenticado detectado")
        try:
            usuario_nombre = request.user.nombre
            usuario_correo = request.user.correo
            print(f"🔍 DEBUG: Nombre: {usuario_nombre}, Correo: {usuario_correo}")
        except AttributeError as e:
            print(f"🔍 DEBUG: AttributeError: {e}")
            usuario_nombre = request.user.username
            usuario_correo = request.user.email if hasattr(request.user, 'email') else ''
            print(f"🔍 DEBUG: Usando username: {usuario_nombre}")
    else:
        print(f"🔍 DEBUG: Usuario NO autenticado")
        usuario_nombre = ''
        usuario_correo = ''
    
    result = {
        'carrito_total_items': total_items,
        'carrito_subtotal': round(subtotal, 2),
        'carrito_iva': round(iva, 2),
        'carrito_total': round(total, 2),
        'IVA_PORCENTAJE': getattr(settings, 'IVA_PORCENTAJE', 0.16),
        'usuario_autenticado': usuario_autenticado,
        'usuario_nombre': usuario_nombre,
        'usuario_correo': usuario_correo,
    }
    
    print(f"🔍 DEBUG: Resultado context: {result}")
    return result