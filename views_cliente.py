# app_mascotas/views_cliente.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal
import datetime
import uuid

from .models import (
    Usuario, Categoria, Tipo, Alimento, 
    Accesorio, Mascota, Carrito, ItemCarrito,
    Pedido, DetallePedido, Venta
)
from .forms import (
    RegistroForm, LoginForm, BusquedaForm, FiltroAlimentosForm
)

# ==========================================
# FUNCIONES DE AYUDA
# ==========================================
def calcular_iva(subtotal, porcentaje_iva=0.16):
    """Calcula el IVA"""
    return subtotal * Decimal(str(porcentaje_iva))

# ==========================================
# VISTAS PÚBLICAS
# ==========================================
def index_cliente(request):
    """Página de inicio para clientes"""
    alimentos_destacados = Alimento.objects.filter(destacado=True, activo=True)[:8]
    accesorios_destacados = Accesorio.objects.filter(destacado=True, activo=True)[:8]
    mascotas_disponibles = Mascota.objects.filter(estado='disponible')[:6]
    
    context = {
        'alimentos_destacados': alimentos_destacados,
        'accesorios_destacados': accesorios_destacados,
        'mascotas_disponibles': mascotas_disponibles,
        'titulo': 'Inicio - Chofys Pet\'s',
    }
    return render(request, 'cliente/index.html', context)  # ← AQUÍ

def buscar_productos(request):
    """Búsqueda de productos"""
    query = request.GET.get('q', '')
    resultados = []
    
    if query:
        # Buscar en alimentos
        alimentos = Alimento.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query),
            activo=True
        )
        
        # Buscar en accesorios
        accesorios = Accesorio.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query),
            activo=True
        )
        
        # Buscar en mascotas
        mascotas = Mascota.objects.filter(
            Q(nombre__icontains=query) |
            Q(raza__icontains=query) |
            Q(descripcion__icontains=query),
            estado='disponible'
        )
        
        # Agregar un campo para identificar tipo
        for alimento in alimentos:
            alimento.tipo_producto = 'alimento'
        for accesorio in accesorios:
            accesorio.tipo_producto = 'accesorio'
        for mascota in mascotas:
            mascota.tipo_producto = 'mascota'
        
        resultados = list(alimentos) + list(accesorios) + list(mascotas)
    
    context = {
        'query': query,
        'resultados': resultados,
        'titulo': f'Resultados para "{query}"' if query else 'Búsqueda de productos',
    }
    return render(request, 'cliente/producto/busqueda.html', context)

def lista_productos_categoria(request, categoria_id):
    """Listar productos por categoría"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    
    alimentos = Alimento.objects.filter(activo=True, categoria=categoria)
    accesorios = Accesorio.objects.filter(activo=True, categoria=categoria)
    
    context = {
        'alimentos': alimentos,
        'accesorios': accesorios,
        'categoria': categoria,
        'titulo': f'{categoria.nombre} - Chofys Pet\'s',
    }
    return render(request, 'cliente/producto/lista_categoria.html', context)


def lista_productos_categoria_tipo(request, categoria_id, tipo_id):
    """Listar productos por categoría y tipo"""
    categoria = get_object_or_404(Categoria, id=categoria_id)
    tipo = get_object_or_404(Tipo, id=tipo_id)
    
    alimentos = Alimento.objects.filter(activo=True, categoria=categoria, tipo=tipo)
    accesorios = Accesorio.objects.filter(activo=True, categoria=categoria, tipo=tipo)
    
    context = {
        'alimentos': alimentos,
        'accesorios': accesorios,
        'categoria': categoria,
        'tipo': tipo,
        'titulo': f'{categoria.nombre} - {tipo.nombre} - Chofys Pet\'s',
    }
    return render(request, 'cliente/producto/lista_categoria.html', context)
def detalle_producto(request, tipo_producto, producto_id):
    """Ver detalle de un producto"""
    if tipo_producto == 'alimento':
        producto = get_object_or_404(Alimento, id=producto_id, activo=True)
    elif tipo_producto == 'accesorio':
        producto = get_object_or_404(Accesorio, id=producto_id, activo=True)
    elif tipo_producto == 'mascota':
        producto = get_object_or_404(Mascota, id=producto_id, estado='disponible')
    else:
        messages.error(request, 'Tipo de producto no válido')
        return redirect('cliente:index_cliente')
    
    context = {
        'producto': producto,
        'tipo_producto': tipo_producto,  # ← IMPORTANTE: pasar esto
        'titulo': f'{producto.nombre} - Chofys Pet\'s',
    }
    return render(request, 'cliente/producto/detalle.html', context)

# ==========================================
# AUTENTICACIÓN
# ==========================================
def registro_cliente(request):
    """Registro de nuevo usuario"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Chofys Pet\'s')
            return redirect('cliente:index_cliente')
    else:
        form = RegistroForm()
    
    context = {
        'form': form,
        'titulo': 'Registro',
    }
    return render(request, 'cliente/usuario/registro.html', context)  # ← CORRECTO

def login_cliente(request):
    """Inicio de sesión"""
    # Si ya está autenticado, redirigir según su rol
    if request.user.is_authenticated:
        if request.user.rol in ['admin', 'empleado']:
            return redirect('administracion:inicio')
        else:
            return redirect('cliente:index_cliente')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.username}!')
                
                # Redirigir según el ROL del usuario
                if user.rol in ['admin', 'empleado']:
                    return redirect('administracion:inicio')  # ← Admin va al panel
                else:
                    return redirect('cliente:index_cliente')  # ← Cliente va a tienda
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'titulo': 'Iniciar Sesión',
    }
    return render(request, 'cliente/usuario/login.html', context)

def logout_cliente(request):
    """Cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    # Siempre redirigir al login después de logout
    return redirect('cliente:login_cliente')
# ==========================================
# PERFIL DE USUARIO
# ==========================================
@login_required
def perfil_usuario(request):
    """Ver y editar perfil de usuario"""
    if request.method == 'POST':
        # Actualizar datos del usuario
        usuario = request.user
        usuario.first_name = request.POST.get('first_name', usuario.first_name)
        usuario.last_name = request.POST.get('last_name', usuario.last_name)
        usuario.email = request.POST.get('email', usuario.email)
        usuario.telefono = request.POST.get('telefono', usuario.telefono)
        usuario.direccion = request.POST.get('direccion', usuario.direccion)
        usuario.save()
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('cliente:perfil_usuario')
    
    context = {
        'usuario': request.user,
        'titulo': 'Mi Perfil',
    }
    return render(request, 'cliente/usuario/perfil.html', context)  # ← CORRECTO

# ==========================================
# CARRITO DE COMPRAS
# ==========================================
@login_required
def ver_carrito(request):
    """Ver carrito de compras"""
    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user, 
        activo=True
    )
    
    # Obtener items del carrito
    items_carrito = carrito.items.all()
    
    # Calcular totales
    total_carrito = carrito.total() if hasattr(carrito, 'total') else 0
    iva = calcular_iva(total_carrito)
    total_con_iva = total_carrito + iva
    
    # Fecha estimada de entrega
    from datetime import datetime, timedelta
    fecha_actual = datetime.now()
    fecha_entrega = fecha_actual + timedelta(days=3)
    fecha_entrega_estimada = fecha_entrega.strftime("%d/%m/%Y")
    
    context = {
        'carrito': carrito,
        'items_carrito': items_carrito,  # Lista de objetos ItemCarrito
        'total_carrito': total_carrito,
        'iva': iva,
        'total_con_iva': total_con_iva,
        'fecha_entrega_estimada': fecha_entrega_estimada,
        'titulo': 'Mi Carrito',
    }
    return render(request, 'cliente/carrito/ver_carrito.html', context)

@login_required
def agregar_al_carrito(request):
    """Agregar producto al carrito"""
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        tipo_producto = request.POST.get('tipo_producto')
        cantidad = int(request.POST.get('cantidad', 1))
        
        if not producto_id or not tipo_producto:
            messages.error(request, 'Datos incompletos')
            return redirect('cliente:ver_carrito')
        
        carrito, created = Carrito.objects.get_or_create(
            usuario=request.user, 
            activo=True
        )
        
        try:
            if tipo_producto == 'alimento':
                producto = get_object_or_404(Alimento, id=producto_id, activo=True)
                item, created = ItemCarrito.objects.get_or_create(
                    carrito=carrito,
                    alimento=producto,
                    defaults={'cantidad': cantidad}
                )
            elif tipo_producto == 'accesorio':
                producto = get_object_or_404(Accesorio, id=producto_id, activo=True)
                item, created = ItemCarrito.objects.get_or_create(
                    carrito=carrito,
                    accesorio=producto,
                    defaults={'cantidad': cantidad}
                )
            elif tipo_producto == 'mascota':
                producto = get_object_or_404(Mascota, id=producto_id, estado='disponible')
                # Para mascotas necesitas un modelo diferente o ajustar ItemCarrito
                messages.info(request, 'Para adoptar mascotas, contacta con el vendedor')
                return redirect('cliente:detalle_producto', tipo_producto='mascota', producto_id=producto_id)
            else:
                messages.error(request, 'Tipo de producto no válido')
                return redirect('cliente:ver_carrito')
            
            if not created:
                item.cantidad += cantidad
                item.save()
            
            messages.success(request, f'¡{producto.nombre} agregado al carrito!')
        except Exception as e:
            messages.error(request, f'Error al agregar al carrito: {str(e)}')
    
    return redirect('cliente:ver_carrito')

@login_required
def actualizar_carrito(request):
    """Actualizar cantidad en carrito"""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cantidad = int(request.POST.get('cantidad', 1))
        
        try:
            item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
            
            if cantidad > 0:
                item.cantidad = cantidad
                item.save()
                messages.success(request, 'Carrito actualizado')
            else:
                item.delete()
                messages.success(request, 'Producto eliminado del carrito')
        except:
            messages.error(request, 'Error al actualizar el carrito')
    
    return redirect('cliente:ver_carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    """Eliminar producto del carrito"""
    try:
        item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
        item.delete()
        messages.success(request, 'Producto eliminado del carrito')
    except:
        messages.error(request, 'Error al eliminar del carrito')
    
    return redirect('cliente:ver_carrito')

# ==========================================
# CHECKOUT Y PEDIDOS
# ==========================================
@login_required
def checkout(request):
    """Página de checkout"""
    carrito = get_object_or_404(Carrito, usuario=request.user, activo=True)
    
    # Obtener items del carrito como lista
    items_carrito = carrito.items.all()
    
    if items_carrito.count() == 0:
        messages.error(request, 'Tu carrito está vacío')
        return redirect('cliente:ver_carrito')
    
    if request.method == 'POST':
        # Crear pedido
        try:
            pedido = Pedido.objects.create(
                usuario=request.user,
                numero_pedido=f"PED-{datetime.datetime.now().strftime('%Y%m%d')}-{Pedido.objects.count() + 1:04d}",
                subtotal=carrito.total(),
                iva=calcular_iva(carrito.total()),
                total=carrito.total() + calcular_iva(carrito.total()),
                direccion_envio=request.POST.get('direccion', ''),
                notas=request.POST.get('notas', '')
            )
            
            # Crear detalles del pedido
            for item in items_carrito:  # Usar items_carrito aquí
                producto = item.producto()
                if producto:
                    DetallePedido.objects.create(
                        pedido=pedido,
                        alimento=item.alimento,
                        accesorio=item.accesorio,
                        cantidad=item.cantidad,
                        precio_unitario=producto.precio,
                        subtotal=item.subtotal()
                    )
            
            # Desactivar carrito y crear uno nuevo
            carrito.activo = False
            carrito.save()
            
            # Redirigir a confirmación
            return redirect('cliente:confirmacion_pedido', pedido_id=pedido.id)
            
        except Exception as e:
            messages.error(request, f'Error al crear el pedido: {str(e)}')
    
    # Calcular totales
    total_carrito = carrito.total()
    iva = calcular_iva(total_carrito)
    total_con_iva = total_carrito + iva
    
    # Obtener datos del usuario para el formulario
    usuario = request.user
    direccion_default = usuario.direccion if hasattr(usuario, 'direccion') else ''
    telefono_default = usuario.telefono if hasattr(usuario, 'telefono') else ''
    
    context = {
        'carrito': carrito,
        'items_carrito': items_carrito,  # Pasar items como lista
        'total_carrito': total_carrito,
        'iva': iva,
        'total_con_iva': total_con_iva,
        'direccion_default': direccion_default,
        'telefono_default': telefono_default,
        'titulo': 'Checkout',
    }
    return render(request, 'cliente/carrito/checkout.html', context)

# En views_cliente.py, función mis_pedidos
@login_required
def mis_pedidos(request):
    """Ver historial de pedidos del usuario"""
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    # DEBUG: Ver qué datos tienen los pedidos
    for pedido in pedidos:
        print(f"Pedido ID: {pedido.id}, Número: {pedido.numero_pedido}")
        print(f"Atributos: {dir(pedido)}")
    
    context = {
        'pedidos': pedidos,
        'titulo': 'Mis Pedidos',
    }
    return render(request, 'cliente/usuario/mis_pedidos.html', context)

# En views_cliente.py, función detalle_mi_pedido
@login_required
def detalle_mi_pedido(request, pedido_id):
    """Ver detalle de un pedido del usuario"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    context = {
        'pedido': pedido,
        'titulo': f'Pedido {pedido.numero_pedido}',
    }
    return render(request, 'cliente/pedido/detalle_pedido.html', context)

@login_required
def confirmacion_pedido(request, pedido_id):
    """Página de confirmación de pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    
    context = {
        'pedido': pedido,
        'titulo': '¡Pedido Confirmado!',
    }
    return render(request, 'cliente/pedido/confirmacion.html', context)  # ← CORRECTO

# ==========================================
# BÚSQUEDA
# ==========================================
def buscar_productos(request):
    """Búsqueda de productos"""
    query = request.GET.get('q', '')
    resultados = []
    
    if query:
        # Buscar en alimentos
        alimentos = Alimento.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query),
            activo=True
        )
        
        # Buscar en accesorios
        accesorios = Accesorio.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query),
            activo=True
        )
        
        # Buscar en mascotas
        mascotas = Mascota.objects.filter(
            Q(nombre__icontains=query) |
            Q(raza__icontains=query) |
            Q(descripcion__icontains=query),
            estado='disponible'
        )
        
        resultados = list(alimentos) + list(accesorios) + list(mascotas)
    
    context = {
        'query': query,
        'resultados': resultados,
        'titulo': f'Resultados para "{query}"',
    }
    return render(request, 'cliente/producto/busqueda.html', context)

# ==========================================
# FUNCIONES PARA URLs FALTANTES (temporales)
# ==========================================
def procesar_pago(request):
    """Procesar pago (simulado) - Función temporal"""
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        try:
            pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
            messages.success(request, '¡Pago procesado exitosamente!')
            return redirect('cliente:confirmacion_pedido', pedido_id=pedido.id)
        except:
            messages.error(request, 'Error al procesar el pago')
    
    return redirect('cliente:checkout')

# ==========================================
# VISTAS ESPECÍFICAS PARA NAVBAR
# ==========================================

def vista_mascotas(request):
    """Página de mascotas - Muestra solo mascotas"""
    mascotas = Mascota.objects.filter(estado='disponible')
    
    # Filtrar por tipo si viene en GET
    tipo_id = request.GET.get('tipo')
    if tipo_id:
        tipo = get_object_or_404(Tipo, id=tipo_id)
        mascotas = mascotas.filter(tipo=tipo)
        tipos_filtrados = Tipo.objects.filter(id=tipo_id)
    else:
        tipo = None
        tipos_filtrados = Tipo.objects.all()
    
    context = {
        'mascotas': mascotas,
        'tipos': tipos_filtrados,
        'tipo_seleccionado': tipo,
        'titulo': 'Mascotas - Chofys Pet\'s',
    }
    return render(request, 'cliente/producto/mascotas.html', context)


def vista_alimentos(request):
    """Página de alimentos - Muestra solo alimentos"""
    alimentos = Alimento.objects.filter(activo=True)
    
    # Obtener categorías y tipos disponibles
    categorias = Categoria.objects.filter(alimentos__isnull=False).distinct()
    tipos = Tipo.objects.filter(alimentos__isnull=False).distinct()
    
    # Aplicar filtros si existen
    categoria_id = request.GET.get('categoria')
    tipo_id = request.GET.get('tipo')
    
    if categoria_id:
        alimentos = alimentos.filter(categoria_id=categoria_id)
    
    if tipo_id:
        alimentos = alimentos.filter(tipo_id=tipo_id)
    
    context = {
        'alimentos': alimentos,
        'categorias': categorias,
        'tipos': tipos,
        'titulo': 'Alimentos - Chofys Pet\'s',
    }
    return render(request, 'cliente/producto/alimentos.html', context)


def vista_accesorios(request):
    """Página de accesorios - Muestra solo accesorios"""
    accesorios = Accesorio.objects.filter(activo=True)
    
    # Obtener categorías y tipos disponibles
    categorias = Categoria.objects.filter(accesorios__isnull=False).distinct()
    tipos = Tipo.objects.filter(accesorios__isnull=False).distinct()
    
    # Aplicar filtros si existen
    categoria_id = request.GET.get('categoria')
    tipo_id = request.GET.get('tipo')
    
    if categoria_id:
        accesorios = accesorios.filter(categoria_id=categoria_id)
    
    if tipo_id:
        accesorios = accesorios.filter(tipo_id=tipo_id)
    
    context = {
        'accesorios': accesorios,
        'categorias': categorias,
        'tipos': tipos,
        'titulo': 'Accesorios - Chofys Pet\'s',
    }
    return render(request, 'cliente/producto/accesorios.html', context)