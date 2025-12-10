# app_mascotas/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class RoleRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si el usuario está autenticado y está en la raíz '/'
        if request.user.is_authenticated and request.path == '/':
            # Si es admin/empleado y no está en admin, redirigir
            if request.user.rol in ['admin', 'empleado']:
                return redirect('administracion:inicio')
        
        return response