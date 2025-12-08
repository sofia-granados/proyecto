# app_mascotas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum
from decimal import Decimal
import datetime
import uuid

from .models import (
    Usuario, Categoria, Tipo, Alimento, 
    Accesorio, Mascota, Carrito, ItemCarrito,
    Pedido, DetallePedido, Venta
)
from .forms import (
    RegistroForm, LoginForm, CategoriaForm, TipoForm,
    AlimentoForm, AccesorioForm, MascotaForm, 
    UsuarioForm, PedidoForm, VentaForm, BusquedaForm, FiltroAlimentosForm
)

# ==========================================
# FUNCIONES DE AYUDA
# ==========================================
def es_administrador(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and (user.is_superuser or user.rol == 'admin')

def es_empleado(user):
    """Verifica si el usuario es empleado o administrador"""
    return user.is_authenticated and user.rol in ['admin', 'empleado']

def calcular_iva(subtotal, porcentaje_iva=0.16):
    """Calcula el IVA"""
    return subtotal * Decimal(str(porcentaje_iva))

# ==========================================
# VISTAS PÚBLICAS (CLIENTE)
# ==========================================
def inicio(request):
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
    return render(request, 'cliente/inicio.html', context)

def ver_productos(request):
    """Ver todos los productos"""
    alimentos = Alimento.objects.filter(activo=True)
    accesorios = Accesorio.objects.filter(activo=True)
    
    # Filtros
    form = FiltroAlimentosForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('categoria'):
            alimentos = alimentos.filter(categoria=form.cleaned_data['categoria'])
            accesorios = accesorios.filter(categoria=form.cleaned_data['categoria'])
        if form.cleaned_data.get('tipo'):
            alimentos = alimentos.filter(tipo=form.cleaned_data['tipo'])
            accesorios = accesorios.filter(tipo=form.cleaned_data['tipo'])
        if form.cleaned_data.get('min_precio'):
            alimentos = alimentos.filter(precio__gte=form.cleaned_data['min_precio'])
            accesorios = accesorios.filter(precio__gte=form.cleaned_data['min_precio'])
        if form.cleaned_data.get('max_precio'):
            alimentos = alimentos.filter(precio__lte=form.cleaned_data['max_precio'])
            accesorios = accesorios.filter(precio__lte=form.cleaned_data['max_precio'])
        if form.cleaned_data.get('destacados'):
            alimentos = alimentos.filter(destacado=True)
            accesorios = accesorios.filter(destacado=True)
    
    context = {
        'alimentos': alimentos,
        'accesorios': accesorios,
        'form': form,
        'titulo': 'Productos - Chofys Pet\'s',
    }
    return render(request, 'cliente/productos.html', context)

def detalle_producto(request, producto_id, tipo):
    """Ver detalle de un producto"""
    if tipo == 'alimento':
        producto = get_object_or_404(Alimento, id=producto_id, activo=True)
        template = 'cliente/detalle_alimento.html'
    elif tipo == 'accesorio':
        producto = get_object_or_404(Accesorio, id=producto_id, activo=True)
        template = 'cliente/detalle_accesorio.html'
    else:
        producto = get_object_or_404(Mascota, id=producto_id, estado='disponible')
        template = 'cliente/detalle_mascota.html'
    
    context = {
        'producto': producto,
        'tipo': tipo,
        'titulo': f'{producto.nombre} - Chofys Pet\'s',
    }
    return render(request, template, context)

# ==========================================
# AUTENTICACIÓN
# ==========================================
def registro(request):
    """Registro de nuevo usuario"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Chofys Pet\'s')
            return redirect('inicio')
    else:
        form = RegistroForm()
    
    context = {
        'form': form,
        'titulo': 'Registro',
    }
    return render(request, 'cliente/registro.html', context)

def login_view(request):
    """Inicio de sesión"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.username}!')
                return redirect('inicio')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'titulo': 'Iniciar Sesión',
    }
    return render(request, 'cliente/login.html', context)

def logout_view(request):
    """Cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('inicio')

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
    
    context = {
        'carrito': carrito,
        'titulo': 'Mi Carrito',
    }
    return render(request, 'cliente/carrito.html', context)

@login_required
def agregar_al_carrito(request, producto_id, tipo):
    """Agregar producto al carrito"""
    carrito, created = Carrito.objects.get_or_create(
        usuario=request.user, 
        activo=True
    )
    
    if tipo == 'alimento':
        producto = get_object_or_404(Alimento, id=producto_id, activo=True)
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            alimento=producto,
            defaults={'cantidad': 1}
        )
    else:  # accesorio
        producto = get_object_or_404(Accesorio, id=producto_id, activo=True)
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            accesorio=producto,
            defaults={'cantidad': 1}
        )
    
    if not created:
        item.cantidad += 1
        item.save()
    
    messages.success(request, f'¡{producto.nombre} agregado al carrito!')
    return redirect('ver_carrito')

@login_required
def actualizar_carrito(request, item_id):
    """Actualizar cantidad en carrito"""
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad > 0:
            item.cantidad = cantidad
            item.save()
            messages.success(request, 'Carrito actualizado')
        else:
            item.delete()
            messages.success(request, 'Producto eliminado del carrito')
    
    return redirect('ver_carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    """Eliminar producto del carrito"""
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    item.delete()
    messages.success(request, 'Producto eliminado del carrito')
    return redirect('ver_carrito')

# ==========================================
# PEDIDOS
# ==========================================
@login_required
def realizar_pedido(request):
    """Realizar pedido desde el carrito"""
    carrito = get_object_or_404(Carrito, usuario=request.user, activo=True)
    
    if carrito.items.count() == 0:
        messages.error(request, 'Tu carrito está vacío')
        return redirect('ver_carrito')
    
    if request.method == 'POST':
        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            numero_pedido=f"PED-{uuid.uuid4().hex[:8].upper()}",
            subtotal=carrito.total(),
            iva=calcular_iva(carrito.total()),
            total=carrito.total() + calcular_iva(carrito.total()),
            direccion_envio=request.POST.get('direccion', ''),
            notas=request.POST.get('notas', '')
        )
        
        # Crear detalles del pedido
        for item in carrito.items.all():
            DetallePedido.objects.create(
                pedido=pedido,
                alimento=item.alimento,
                accesorio=item.accesorio,
                cantidad=item.cantidad,
                precio_unitario=item.producto().precio,
                subtotal=item.subtotal()
            )
        
        # Desactivar carrito
        carrito.activo = False
        carrito.save()
        
        messages.success(request, f'¡Pedido realizado exitosamente! Número: {pedido.numero_pedido}')
        return redirect('ver_pedidos')
    
    context = {
        'carrito': carrito,
        'iva_porcentaje': 0.16,
        'iva': calcular_iva(carrito.total()),
        'total_con_iva': carrito.total() + calcular_iva(carrito.total()),
        'titulo': 'Realizar Pedido',
    }
    return render(request, 'cliente/realizar_pedido.html', context)

@login_required
def ver_pedidos(request):
    """Ver historial de pedidos del usuario"""
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos,
        'titulo': 'Mis Pedidos',
    }
    return render(request, 'cliente/pedidos.html', context)

# ==========================================
# VISTAS DE ADMINISTRACIÓN
# ==========================================
@login_required
@user_passes_test(es_administrador)
def inicio_administracion(request):
    """Inicio del panel de administración"""
    # Estadísticas
    total_ventas = Venta.objects.count()
    total_pedidos = Pedido.objects.count()
    total_productos = Alimento.objects.count() + Accesorio.objects.count()
    total_usuarios = Usuario.objects.count()
    
    # Pedidos recientes
    pedidos_recientes = Pedido.objects.order_by('-fecha_pedido')[:5]
    
    context = {
        'total_ventas': total_ventas,
        'total_pedidos': total_pedidos,
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
        'pedidos_recientes': pedidos_recientes,
        'titulo': 'Panel de Administración',
    }
    return render(request, 'administracion/inicio.html', context)

# ==========================================
# CRUD ALIMENTOS
# ==========================================
@login_required
@user_passes_test(es_empleado)
def ver_alimentos(request):
    """Ver lista de alimentos"""
    alimentos = Alimento.objects.all().order_by('-fecha_creacion')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        alimentos = alimentos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )
    
    context = {
        'alimentos': alimentos,
        'titulo': 'Lista de Alimentos',
    }
    return render(request, 'administracion/alimentos/ver_alimentos.html', context)

@login_required
@user_passes_test(es_empleado)
def agregar_alimento(request):
    """Agregar nuevo alimento"""
    if request.method == 'POST':
        form = AlimentoForm(request.POST, request.FILES)
        if form.is_valid():
            alimento = form.save()
            messages.success(request, f'Alimento "{alimento.nombre}" agregado correctamente')
            return redirect('administracion:ver_alimentos')
    else:
        form = AlimentoForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Alimento',
    }
    return render(request, 'administracion/alimentos/agregar_alimento.html', context)

@login_required
@user_passes_test(es_empleado)
def editar_alimento(request, id):
    """Editar alimento existente"""
    alimento = get_object_or_404(Alimento, id=id)
    
    if request.method == 'POST':
        form = AlimentoForm(request.POST, request.FILES, instance=alimento)
        if form.is_valid():
            form.save()
            messages.success(request, f'Alimento "{alimento.nombre}" actualizado correctamente')
            return redirect('administracion:ver_alimentos')
    else:
        form = AlimentoForm(instance=alimento)
    
    context = {
        'form': form,
        'alimento': alimento,
        'titulo': f'Editar {alimento.nombre}',
    }
    return render(request, 'administracion/alimentos/editar_alimento.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_alimento(request, id):
    """Eliminar alimento"""
    alimento = get_object_or_404(Alimento, id=id)
    
    if request.method == 'POST':
        nombre = alimento.nombre
        alimento.delete()
        messages.success(request, f'Alimento "{nombre}" eliminado correctamente')
        return redirect('administracion:ver_alimentos')
    
    context = {
        'alimento': alimento,
        'titulo': f'Eliminar {alimento.nombre}',
    }
    return render(request, 'administracion/alimentos/eliminar_alimento.html', context)

# ==========================================
# CRUD ACCESORIOS (similar a alimentos)
# ==========================================
@login_required
@user_passes_test(es_empleado)
def ver_accesorios(request):
    """Ver lista de accesorios"""
    accesorios = Accesorio.objects.all().order_by('-fecha_creacion')
    context = {
        'accesorios': accesorios,
        'titulo': 'Lista de Accesorios',
    }
    return render(request, 'administracion/accesorios/ver_accesorios.html', context)

@login_required
@user_passes_test(es_empleado)
def agregar_accesorio(request):
    """Agregar nuevo accesorio"""
    if request.method == 'POST':
        form = AccesorioForm(request.POST, request.FILES)
        if form.is_valid():
            accesorio = form.save()
            messages.success(request, f'Accesorio "{accesorio.nombre}" agregado correctamente')
            return redirect('administracion:ver_accesorios')
    else:
        form = AccesorioForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Accesorio',
    }
    return render(request, 'administracion/accesorios/agregar_accesorio.html', context)

@login_required
@user_passes_test(es_empleado)
def editar_accesorio(request, id):
    """Editar accesorio existente"""
    accesorio = get_object_or_404(Accesorio, id=id)
    
    if request.method == 'POST':
        form = AccesorioForm(request.POST, request.FILES, instance=accesorio)
        if form.is_valid():
            form.save()
            messages.success(request, f'Accesorio "{accesorio.nombre}" actualizado correctamente')
            return redirect('administracion:ver_accesorios')
    else:
        form = AccesorioForm(instance=accesorio)
    
    context = {
        'form': form,
        'accesorio': accesorio,
        'titulo': f'Editar {accesorio.nombre}',
    }
    return render(request, 'administracion/accesorios/editar_accesorio.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_accesorio(request, id):
    """Eliminar accesorio"""
    accesorio = get_object_or_404(Accesorio, id=id)
    
    if request.method == 'POST':
        nombre = accesorio.nombre
        accesorio.delete()
        messages.success(request, f'Accesorio "{nombre}" eliminado correctamente')
        return redirect('administracion:ver_accesorios')
    
    context = {
        'accesorio': accesorio,
        'titulo': f'Eliminar {accesorio.nombre}',
    }
    return render(request, 'administracion/accesorios/eliminar_accesorio.html', context)

# ==========================================
# CRUD MASCOTAS
# ==========================================
@login_required
@user_passes_test(es_empleado)
def ver_mascotas(request):
    """Ver lista de mascotas"""
    mascotas = Mascota.objects.all().order_by('-fecha_creacion')
    context = {
        'mascotas': mascotas,
        'titulo': 'Lista de Mascotas',
    }
    return render(request, 'administracion/mascotas/ver_mascotas.html', context)

@login_required
@user_passes_test(es_empleado)
def agregar_mascota(request):
    """Agregar nueva mascota"""
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save()
            messages.success(request, f'Mascota "{mascota.nombre}" agregada correctamente')
            return redirect('administracion:ver_mascotas')
    else:
        form = MascotaForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Mascota',
    }
    return render(request, 'administracion/mascotas/agregar_mascota.html', context)

@login_required
@user_passes_test(es_empleado)
def editar_mascota(request, id):
    """Editar mascota existente"""
    mascota = get_object_or_404(Mascota, id=id)
    
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mascota "{mascota.nombre}" actualizada correctamente')
            return redirect('administracion:ver_mascotas')
    else:
        form = MascotaForm(instance=mascota)
    
    context = {
        'form': form,
        'mascota': mascota,
        'titulo': f'Editar {mascota.nombre}',
    }
    return render(request, 'administracion/mascotas/editar_mascota.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_mascota(request, id):
    """Eliminar mascota"""
    mascota = get_object_or_404(Mascota, id=id)
    
    if request.method == 'POST':
        nombre = mascota.nombre
        mascota.delete()
        messages.success(request, f'Mascota "{nombre}" eliminada correctamente')
        return redirect('administracion:ver_mascotas')
    
    context = {
        'mascota': mascota,
        'titulo': f'Eliminar {mascota.nombre}',
    }
    return render(request, 'administracion/mascotas/eliminar_mascota.html', context)

# ==========================================
# CRUD CATEGORÍAS
# ==========================================
@login_required
@user_passes_test(es_empleado)
def ver_categorias(request):
    """Ver lista de categorías"""
    categorias = Categoria.objects.all().order_by('nombre')
    context = {
        'categorias': categorias,
        'titulo': 'Lista de Categorías',
    }
    return render(request, 'administracion/categoria/ver_categorias.html', context)

@login_required
@user_passes_test(es_empleado)
def agregar_categoria(request):
    """Agregar nueva categoría"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" agregada correctamente')
            return redirect('administracion:ver_categorias')
    else:
        form = CategoriaForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Categoría',
    }
    return render(request, 'administracion/categoria/agregar_categoria.html', context)

@login_required
@user_passes_test(es_empleado)
def editar_categoria(request, id):
    """Editar categoría existente"""
    categoria = get_object_or_404(Categoria, id=id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada correctamente')
            return redirect('administracion:ver_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria,
        'titulo': f'Editar {categoria.nombre}',
    }
    return render(request, 'administracion/categoria/editar_categoria.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_categoria(request, id):
    """Eliminar categoría"""
    categoria = get_object_or_404(Categoria, id=id)
    
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría "{nombre}" eliminada correctamente')
        return redirect('administracion:ver_categorias')
    
    context = {
        'categoria': categoria,
        'titulo': f'Eliminar {categoria.nombre}',
    }
    return render(request, 'administracion/categoria/eliminar_categoria.html', context)

# ==========================================
# CRUD TIPOS
# ==========================================
@login_required
@user_passes_test(es_empleado)
def ver_tipos(request):
    """Ver lista de tipos"""
    tipos = Tipo.objects.all().order_by('nombre')
    context = {
        'tipos': tipos,
        'titulo': 'Lista de Tipos',
    }
    return render(request, 'administracion/tipo/ver_tipos.html', context)

@login_required
@user_passes_test(es_empleado)
def agregar_tipo(request):
    """Agregar nuevo tipo"""
    if request.method == 'POST':
        form = TipoForm(request.POST)
        if form.is_valid():
            tipo = form.save()
            messages.success(request, f'Tipo "{tipo.nombre}" agregado correctamente')
            return redirect('administracion:ver_tipos')
    else:
        form = TipoForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Tipo',
    }
    return render(request, 'administracion/tipo/agregar_tipo.html', context)

@login_required
@user_passes_test(es_empleado)
def editar_tipo(request, id):
    """Editar tipo existente"""
    tipo = get_object_or_404(Tipo, id=id)
    
    if request.method == 'POST':
        form = TipoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo "{tipo.nombre}" actualizado correctamente')
            return redirect('administracion:ver_tipos')
    else:
        form = TipoForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'titulo': f'Editar {tipo.nombre}',
    }
    return render(request, 'administracion/tipo/editar_tipo.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_tipo(request, id):
    """Eliminar tipo"""
    tipo = get_object_or_404(Tipo, id=id)
    
    if request.method == 'POST':
        nombre = tipo.nombre
        tipo.delete()
        messages.success(request, f'Tipo "{nombre}" eliminado correctamente')
        return redirect('administracion:ver_tipos')
    
    context = {
        'tipo': tipo,
        'titulo': f'Eliminar {tipo.nombre}',
    }
    return render(request, 'administracion/tipo/eliminar_tipo.html', context)

# ==========================================
# CRUD USUARIOS (solo admin)
# ==========================================
@login_required
@user_passes_test(es_administrador)
def ver_usuarios(request):
    """Ver lista de usuarios"""
    usuarios = Usuario.objects.all().order_by('-date_joined')
    context = {
        'usuarios': usuarios,
        'titulo': 'Lista de Usuarios',
    }
    return render(request, 'administracion/usuarios/ver_usuarios.html', context)

@login_required
@user_passes_test(es_administrador)
def agregar_usuario(request):
    """Agregar nuevo usuario (admin)"""
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario "{usuario.username}" agregado correctamente')
            return redirect('administracion:ver_usuarios')
    else:
        form = UsuarioForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Usuario',
    }
    return render(request, 'administracion/usuarios/agregar_usuario.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_usuario(request, id):
    """Editar usuario existente"""
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario.username}" actualizado correctamente')
            return redirect('administracion:ver_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'titulo': f'Editar {usuario.username}',
    }
    return render(request, 'administracion/usuarios/editar_usuario.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_usuario(request, id):
    """Eliminar usuario"""
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{username}" eliminado correctamente')
        return redirect('administracion:ver_usuarios')
    
    context = {
        'usuario': usuario,
        'titulo': f'Eliminar {usuario.username}',
    }
    return render(request, 'administracion/usuarios/eliminar_usuario.html', context)

# ==========================================
# PEDIDOS (admin)
# ==========================================
@login_required
@user_passes_test(es_empleado)
def ver_pedidos_admin(request):
    """Ver todos los pedidos (admin)"""
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    
    # Filtrar por estado
    estado = request.GET.get('estado')
    if estado:
        pedidos = pedidos.filter(estado=estado)
    
    context = {
        'pedidos': pedidos,
        'titulo': 'Pedidos',
    }
    return render(request, 'administracion/pedidos/ver_pedidos.html', context)

@login_required
@user_passes_test(es_empleado)
def detalle_pedido_admin(request, id):
    """Ver detalle de pedido (admin)"""
    pedido = get_object_or_404(Pedido, id=id)
    
    context = {
        'pedido': pedido,
        'titulo': f'Pedido {pedido.numero_pedido}',
    }
    return render(request, 'administracion/pedidos/detalle_pedido.html', context)

@login_required
@user_passes_test(es_empleado)
def cambiar_estado_pedido(request, id):
    """Cambiar estado de pedido"""
    pedido = get_object_or_404(Pedido, id=id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES).keys():
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido {pedido.numero_pedido} actualizado a {nuevo_estado}')
    
    return redirect('administracion:detalle_pedido', id=id)

# ==========================================
# VENTAS (admin)
# ==========================================
@login_required
@user_passes_test(es_empleado)
def ver_ventas(request):
    """Ver todas las ventas"""
    ventas = Venta.objects.all().order_by('-fecha_venta')
    
    # Filtrar por fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio:
        ventas = ventas.filter(fecha_venta__date__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha_venta__date__lte=fecha_fin)
    
    context = {
        'ventas': ventas,
        'titulo': 'Ventas',
    }
    return render(request, 'administracion/ventas/ver_ventas.html', context)

@login_required
@user_passes_test(es_empleado)
def detalle_venta(request, id):
    """Ver detalle de venta"""
    venta = get_object_or_404(Venta, id=id)
    
    context = {
        'venta': venta,
        'titulo': f'Venta #{venta.id}',
    }
    return render(request, 'administracion/ventas/detalle_venta.html', context)

@login_required
@user_passes_test(es_empleado)
def agregar_venta(request, pedido_id=None):
    """Agregar venta manualmente"""
    if pedido_id:
        pedido = get_object_or_404(Pedido, id=pedido_id)
    else:
        pedido = None
    
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            if pedido:
                venta.pedido = pedido
            venta.save()
            messages.success(request, f'Venta registrada exitosamente')
            return redirect('administracion:ver_ventas')
    else:
        initial = {'pedido': pedido} if pedido else {}
        form = VentaForm(initial=initial)
    
    context = {
        'form': form,
        'pedido': pedido,
        'titulo': 'Registrar Venta',
    }
    return render(request, 'administracion/ventas/agregar_venta.html', context)

# ==========================================
# REPORTES
# ==========================================
@login_required
@user_passes_test(es_administrador)
def reportes(request):
    """Página de reportes"""
    # Estadísticas generales
    total_ventas_mes = Venta.objects.filter(
        fecha_venta__month=datetime.datetime.now().month
    ).count()
    
    productos_mas_vendidos = Alimento.objects.filter(
        detallepedido__isnull=False
    ).annotate(
        total_vendido=Sum('detallepedido__cantidad')
    ).order_by('-total_vendido')[:10]
    
    context = {
        'total_ventas_mes': total_ventas_mes,
        'productos_mas_vendidos': productos_mas_vendidos,
        'titulo': 'Reportes',
    }
    return render(request, 'administracion/reportes.html', context)

# ==========================================
# VISTAS PARA URLs CLIENTE (compatibilidad)
# ==========================================
# Estas funciones son para mantener compatibilidad con tu urls_cliente.py
# Puedes eliminarlas si no las necesitas

def lista_productos_categoria(request, categoria_id, tipo_id=None):
    """Compatibilidad con URL antigua"""
    if tipo_id:
        return redirect('cliente:lista_categoria_tipo', categoria_id=categoria_id, tipo_id=tipo_id)
    else:
        return redirect('cliente:lista_categoria', categoria_id=categoria_id)

def eliminar_pedido(request, id):
    """Eliminar pedido (admin)"""
    pedido = get_object_or_404(Pedido, id=id)
    if request.method == 'POST':
        numero = pedido.numero_pedido
        pedido.delete()
        messages.success(request, f'Pedido {numero} eliminado')
        return redirect('administracion:ver_pedidos')
    return render(request, 'administracion/pedidos/eliminar_pedido.html', {'pedido': pedido})

def eliminar_venta(request, id):
    """Eliminar venta (admin)"""
    venta = get_object_or_404(Venta, id=id)
    if request.method == 'POST':
        venta.delete()
        messages.success(request, 'Venta eliminada')
        return redirect('administracion:ver_ventas')
    return render(request, 'administracion/ventas/eliminar_venta.html', {'venta': venta})

# ==========================================
# ERROR HANDLERS
# ==========================================
def pagina_no_encontrada(request, exception):
    """Página 404 personalizada"""
    return render(request, '404.html', status=404)

def error_servidor(request):
    """Página 500 personalizada"""
    return render(request, '500.html', status=500)

# ==========================================
# ALIAS PARA MANTENER COMPATIBILIDAD
# ==========================================
# Estos alias permiten que tus URLs existentes sigan funcionando
detalle_pedido = detalle_pedido_admin