from django.urls import path
from . import views  # Importa tu views.py actual

app_name = 'administracion'

urlpatterns = [
    # ============ DASHBOARD ============
    path('', views.inicio_administracion, name='inicio'),
    
    # ============ USUARIOS ============
    path('usuarios/', views.ver_usuarios, name='ver_usuarios'),
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
    
    # ============ CATEGORÍAS ============
    path('categorias/', views.ver_categorias, name='ver_categorias'),
    path('categorias/agregar/', views.agregar_categoria, name='agregar_categoria'),
    path('categorias/editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # ============ TIPOS ============
    path('tipos/', views.ver_tipos, name='ver_tipos'),
    path('tipos/agregar/', views.agregar_tipo, name='agregar_tipo'),
    path('tipos/editar/<int:id>/', views.editar_tipo, name='editar_tipo'),
    path('tipos/eliminar/<int:id>/', views.eliminar_tipo, name='eliminar_tipo'),
    
    # ============ ALIMENTOS ============
    path('alimentos/', views.ver_alimentos, name='ver_alimentos'),
    path('alimentos/agregar/', views.agregar_alimento, name='agregar_alimento'),
    path('alimentos/editar/<int:id>/', views.editar_alimento, name='editar_alimento'),
    path('alimentos/eliminar/<int:id>/', views.eliminar_alimento, name='eliminar_alimento'),
    
    # ============ ACCESORIOS ============
    path('accesorios/', views.ver_accesorios, name='ver_accesorios'),
    path('accesorios/agregar/', views.agregar_accesorio, name='agregar_accesorio'),
    path('accesorios/editar/<int:id>/', views.editar_accesorio, name='editar_accesorio'),
    path('accesorios/eliminar/<int:id>/', views.eliminar_accesorio, name='eliminar_accesorio'),
    
    # ============ MASCOTAS ============
    path('mascotas/', views.ver_mascotas, name='ver_mascotas'),
    path('mascotas/agregar/', views.agregar_mascota, name='agregar_mascota'),
    path('mascotas/editar/<int:id>/', views.editar_mascota, name='editar_mascota'),
    path('mascotas/eliminar/<int:id>/', views.eliminar_mascota, name='eliminar_mascota'),
    
    # ============ PEDIDOS ============
    path('pedidos/', views.ver_pedidos_admin, name='ver_pedidos'),
path('pedidos/<int:id>/', views.detalle_pedido_admin, name='detalle_pedido'),
path('pedidos/cambiar-estado/<int:id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
# AÑADE ESTA LÍNEA ↓↓↓
path('pedidos/eliminar/<int:id>/', views.eliminar_pedido, name='eliminar_pedido'),

    # ============ VENTAS ============
    path('ventas/', views.ver_ventas, name='ver_ventas'),
    path('ventas/<int:id>/', views.detalle_venta, name='detalle_venta'),
    path('ventas/agregar/<int:pedido_id>/', views.agregar_venta, name='agregar_venta_pedido'),
    path('ventas/agregar/', views.agregar_venta, name='agregar_venta'),
    
    # ============ REPORTES ============
    path('reportes/', views.reportes, name='reportes'),
]