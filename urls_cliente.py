# app_mascotas/urls_cliente.py
from django.urls import path
from . import views_cliente

app_name = 'cliente'

urlpatterns = [
    # ============ PÁGINA DE INICIO ============
    path('', views_cliente.index_cliente, name='index_cliente'),
    
    # ============ NAVBAR PRINCIPAL ============
    path('mascotas/', views_cliente.vista_mascotas, name='vista_mascotas'),
    path('alimentos/', views_cliente.vista_alimentos, name='vista_alimentos'),
    path('accesorios/', views_cliente.vista_accesorios, name='vista_accesorios'),
    
    # ============ RUTAS POR CATEGORÍA ============
    path('categoria/<int:categoria_id>/', views_cliente.lista_productos_categoria, name='lista_categoria'),
    path('categoria/<int:categoria_id>/tipo/<int:tipo_id>/', views_cliente.lista_productos_categoria_tipo, name='lista_categoria_tipo'),
    
    # ============ DETALLE DE PRODUCTOS ============
    path('producto/<str:tipo_producto>/<int:producto_id>/', views_cliente.detalle_producto, name='detalle_producto'),
    
    # ============ BÚSQUEDA ============
    path('buscar/', views_cliente.buscar_productos, name='buscar_productos'),
    
    # ============ CARRITO DE COMPRAS ============
    path('carrito/', views_cliente.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/', views_cliente.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/', views_cliente.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views_cliente.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views_cliente.checkout, name='checkout'),
    
    # ============ AUTENTICACIÓN ============
    path('login/', views_cliente.login_cliente, name='login_cliente'),
    path('registro/', views_cliente.registro_cliente, name='registro_cliente'),
    path('logout/', views_cliente.logout_cliente, name='logout_cliente'),
    
    # ============ USUARIO AUTENTICADO ============
    path('perfil/', views_cliente.perfil_usuario, name='perfil_usuario'),
    path('mis-pedidos/', views_cliente.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<int:pedido_id>/', views_cliente.detalle_mi_pedido, name='detalle_mi_pedido'),
    path('confirmacion/<int:pedido_id>/', views_cliente.confirmacion_pedido, name='confirmacion_pedido'),
    
    # ============ PAGO ============
    path('procesar-pago/', views_cliente.procesar_pago, name='procesar_pago'),
]