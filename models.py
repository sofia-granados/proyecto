# app_mascotas/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# ==========================================
# MODELO DE USUARIO PERSONALIZADO
# ==========================================
class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
    ]
    
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='cliente')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"

# ==========================================
# MODELOS CATALOGO
# ==========================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.IntegerField(default=0)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
    
    def __str__(self):
        return self.nombre

class Tipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.CharField(max_length=50, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

# ==========================================
# MODELOS DE PRODUCTOS
# ==========================================
class Alimento(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='alimentos')
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE, related_name='alimentos')
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_original = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='alimentos/', blank=True, null=True)
    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Alimento"
        verbose_name_plural = "Alimentos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def tiene_descuento(self):
        return self.precio_original and self.precio < self.precio_original
    
    def porcentaje_descuento(self):
        if self.tiene_descuento():
            return int(((self.precio_original - self.precio) / self.precio_original) * 100)
        return 0

class Accesorio(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='accesorios')
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE, related_name='accesorios')
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_original = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='accesorios/', blank=True, null=True)
    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

# ==========================================
# MODELOS DE MASCOTAS
# ==========================================
class Mascota(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservado', 'Reservado'),
        ('vendido', 'Vendido'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE, related_name='mascotas')
    raza = models.CharField(max_length=100)
    edad = models.IntegerField()  # En meses
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='mascotas/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.raza}"

# ==========================================
# MODELOS DE VENTAS
# ==========================================
class Carrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carrito')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    def total(self):
        total = 0
        for item in self.items.all():
            total += item.subtotal()
        return total
    
    def cantidad_items(self):
        return self.items.count()

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE, null=True, blank=True)
    accesorio = models.ForeignKey(Accesorio, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    def subtotal(self):
        if self.alimento:
            return self.alimento.precio * self.cantidad
        elif self.accesorio:
            return self.accesorio.precio * self.cantidad
        return 0
    
    def producto(self):
        return self.alimento or self.accesorio

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    numero_pedido = models.CharField(max_length=20, unique=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    iva = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_envio = models.TextField()
    notas = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Pedido {self.numero_pedido} - {self.usuario.username}"
    
    def generar_numero_pedido(self):
        import uuid
        return f"PED-{uuid.uuid4().hex[:8].upper()}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE, null=True, blank=True)
    accesorio = models.ForeignKey(Accesorio, on_delete=models.CASCADE, null=True, blank=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        producto = self.alimento or self.accesorio or self.mascota
        return f"{producto} x{self.cantidad}"

class Venta(models.Model):
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]
    
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='venta')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    referencia_pago = models.CharField(max_length=100, blank=True, null=True)
    vendedor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='ventas_realizadas')
    
    def __str__(self):
        return f"Venta {self.id} - {self.pedido.numero_pedido}"