# app_mascotas/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Categoria, Tipo, Alimento, 
    Accesorio, Mascota, Pedido, Venta,
    Carrito, ItemCarrito, DetallePedido
)

# ==========================================
# ADMIN PERSONALIZADO PARA USUARIO
# ==========================================
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento', 'avatar')}),
        ('Dirección', {'fields': ('direccion',)}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'rol'),
        }),
    )

# ==========================================
# ADMIN PARA CATEGORÍAS Y TIPOS
# ==========================================
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

class TipoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

# ==========================================
# ADMIN PARA PRODUCTOS
# ==========================================
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'tipo', 'precio', 'stock', 'destacado', 'activo')
    list_filter = ('categoria', 'tipo', 'destacado', 'activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'destacado', 'activo')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'tipo', 'descripcion')
        }),
        ('Precios y Stock', {
            'fields': ('precio', 'precio_original', 'stock')
        }),
        ('Imagen y Estado', {
            'fields': ('imagen', 'destacado', 'activo')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

class AccesorioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'tipo', 'precio', 'stock', 'destacado', 'activo')
    list_filter = ('categoria', 'tipo', 'destacado', 'activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'destacado', 'activo')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion',)

# ==========================================
# ADMIN PARA MASCOTAS
# ==========================================
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'tipo', 'raza', 'edad', 'precio', 'estado')
    list_filter = ('tipo', 'estado', 'fecha_creacion')
    search_fields = ('nombre', 'raza', 'descripcion')
    list_editable = ('precio', 'estado')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion',)

# ==========================================
# ADMIN PARA CARRITO
# ==========================================
class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ('fecha_agregado', 'subtotal')
    fields = ('alimento', 'accesorio', 'cantidad', 'subtotal')

class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_creacion', 'total', 'activo')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('usuario__username',)
    inlines = [ItemCarritoInline]
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'total')

    def total(self, obj):
        return obj.total()
    total.short_description = 'Total'

# ==========================================
# ADMIN PARA PEDIDOS
# ==========================================
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('precio_unitario', 'subtotal')
    fields = ('alimento', 'accesorio', 'mascota', 'cantidad', 'precio_unitario', 'subtotal')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'usuario', 'fecha_pedido', 'estado', 'total')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('numero_pedido', 'usuario__username', 'direccion_envio')
    list_editable = ('estado',)
    ordering = ('-fecha_pedido',)
    inlines = [DetallePedidoInline]
    readonly_fields = ('numero_pedido', 'fecha_pedido', 'subtotal', 'iva', 'total')
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'usuario', 'fecha_pedido')
        }),
        ('Detalles del Envío', {
            'fields': ('direccion_envio', 'notas')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Totales', {
            'fields': ('subtotal', 'iva', 'total'),
            'classes': ('collapse',)
        }),
    )

# ==========================================
# ADMIN PARA VENTAS
# ==========================================
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'fecha_venta', 'metodo_pago', 'vendedor')
    list_filter = ('metodo_pago', 'fecha_venta')
    search_fields = ('pedido__numero_pedido', 'vendedor__username', 'referencia_pago')
    ordering = ('-fecha_venta',)
    readonly_fields = ('fecha_venta',)

# ==========================================
# REGISTRO DE MODELOS EN EL ADMIN
# ==========================================
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Tipo, TipoAdmin)
admin.site.register(Alimento, AlimentoAdmin)
admin.site.register(Accesorio, AccesorioAdmin)
admin.site.register(Mascota, MascotaAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Venta, VentaAdmin)

# Los siguientes se registran sin admin personalizado (opcional)
admin.site.register(ItemCarrito)
admin.site.register(DetallePedido)

# ==========================================
# CONFIGURACIÓN DEL SITIO ADMIN
# ==========================================
admin.site.site_header = "Administración de Chofys Pet's"
admin.site.site_title = "Chofys Pet's Admin"
admin.site.index_title = "Panel de Administración"