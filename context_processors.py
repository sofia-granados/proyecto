# app_mascotas/context_processors.py
from django.conf import settings
from .models import Carrito, Usuario  # Importar tus modelos

def carrito_context(request):
    """Context processor para información del carrito - USANDO MODELOS"""
    print(f"🔍 DEBUG context_processor: Ejecutándose...")
    print(f"🔍 DEBUG: User: {request.user}")
    print(f"🔍 DEBUG: Autenticado: {request.user.is_authenticated}")
    
    # Inicializar valores por defecto
    context = {
        'carrito_total_items': 0,
        'carrito_subtotal': 0,
        'carrito_iva': 0,
        'carrito_total': 0,
        'IVA_PORCENTAJE': getattr(settings, 'IVA_PORCENTAJE', 0.16),
        'usuario_autenticado': False,
        'usuario_nombre': '',
        'usuario_correo': '',
    }
    
    # Si el usuario está autenticado
    if request.user.is_authenticated:
        print(f"🔍 DEBUG: Usuario autenticado detectado")
        
        try:
            # Obtener usuario
            usuario = request.user
            
            # Intentar obtener nombre y correo del modelo Usuario
            if hasattr(usuario, 'first_name') and usuario.first_name:
                usuario_nombre = usuario.first_name
                if hasattr(usuario, 'last_name') and usuario.last_name:
                    usuario_nombre += " " + usuario.last_name
            else:
                usuario_nombre = usuario.username
                
            usuario_correo = usuario.email if hasattr(usuario, 'email') else ''
            
            print(f"🔍 DEBUG: Nombre: {usuario_nombre}, Correo: {usuario_correo}")
            
            # Obtener carrito del usuario
            try:
                carrito = Carrito.objects.filter(usuario=usuario, activo=True).first()
                
                if carrito:
                    # Calcular total de items usando el método del modelo
                    total_items = carrito.cantidad_items()
                    subtotal = float(carrito.total())
                    iva = subtotal * getattr(settings, 'IVA_PORCENTAJE', 0.16)
                    total = subtotal + iva
                    
                    print(f"🔍 DEBUG: Carrito encontrado - Items: {total_items}, Subtotal: {subtotal}")
                    
                    context.update({
                        'carrito_total_items': total_items,
                        'carrito_subtotal': round(subtotal, 2),
                        'carrito_iva': round(iva, 2),
                        'carrito_total': round(total, 2),
                        'usuario_autenticado': True,
                        'usuario_nombre': usuario_nombre,
                        'usuario_correo': usuario_correo,
                    })
                else:
                    print(f"🔍 DEBUG: Usuario no tiene carrito activo")
                    context.update({
                        'usuario_autenticado': True,
                        'usuario_nombre': usuario_nombre,
                        'usuario_correo': usuario_correo,
                    })
                    
            except Exception as e:
                print(f"🔍 DEBUG: Error al obtener carrito: {e}")
                context.update({
                    'usuario_autenticado': True,
                    'usuario_nombre': usuario_nombre,
                    'usuario_correo': usuario_correo,
                })
                
        except AttributeError as e:
            print(f"🔍 DEBUG: AttributeError: {e}")
            context.update({
                'usuario_autenticado': True,
                'usuario_nombre': request.user.username,
                'usuario_correo': request.user.email if hasattr(request.user, 'email') else '',
            })
    else:
        print(f"🔍 DEBUG: Usuario NO autenticado")
        # Para usuarios no autenticados, podrías usar sesiones si quieres
        carrito = request.session.get('carrito', {})
        if carrito:
            total_items = sum(item.get('cantidad', 0) for item in carrito.values())
            context['carrito_total_items'] = total_items
    
    print(f"🔍 DEBUG: Contexto final: {context}")
    return context