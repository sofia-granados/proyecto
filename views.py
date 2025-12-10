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
    return user.is_authenticated and user.rol == 'admin'

def es_empleado(user):
    """Verifica si el usuario es empleado o administrador"""
    return user.is_authenticated and user.rol in ['admin', 'empleado']

def calcular_iva(subtotal, porcentaje_iva=0.16):
    """Calcula el IVA"""
    return subtotal * Decimal(str(porcentaje_iva))

# ==========================================
# VISTAS DE ADMINISTRACIÓN (las que necesitan tus URLs)
# ==========================================
@login_required
@user_passes_test(es_administrador)
def inicio_administracion(request):
    """Inicio del panel de administración"""
    # Estadísticas
    total_usuarios = Usuario.objects.count()
    total_productos = Alimento.objects.count() + Accesorio.objects.count()
    total_mascotas = Mascota.objects.count()
    total_pedidos = Pedido.objects.count()
    
    context = {
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'total_mascotas': total_mascotas,
        'total_pedidos': total_pedidos,
        'titulo': 'Panel de Administración',
    }
    return render(request, 'administracion/inicio.html', context)

# ============ USUARIOS ============
@login_required
@user_passes_test(es_administrador)
def ver_usuarios(request):
    """Ver lista de usuarios"""
    usuarios = Usuario.objects.all().order_by('-date_joined')
    context = {
        'usuarios': usuarios,
        'titulo': 'Usuarios - Administración',
    }
    return render(request, 'administracion/usuarios/ver_usuarios.html', context)

@login_required
@user_passes_test(es_administrador)
def agregar_usuario(request):
    """Agregar nuevo usuario"""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado correctamente')
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
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente')
            return redirect('administracion:ver_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'titulo': 'Editar Usuario',
    }
    return render(request, 'administracion/usuarios/editar_usuario.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_usuario(request, id):
    """Eliminar usuario"""
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente')
        return redirect('administracion:ver_usuarios')
    
    context = {
        'usuario': usuario,
        'titulo': 'Eliminar Usuario',
    }
    return render(request, 'administracion/usuarios/eliminar_usuario.html', context)

# ============ CATEGORÍAS ============
@login_required
@user_passes_test(es_administrador)
def ver_categorias(request):
    """Ver lista de categorías"""
    categorias = Categoria.objects.all().order_by('nombre')
    context = {
        'categorias': categorias,
        'titulo': 'Categorías - Administración',
    }
    return render(request, 'administracion/categoria/ver_categorias.html', context)

@login_required
@user_passes_test(es_administrador)
def agregar_categoria(request):
    """Agregar nueva categoría"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada correctamente')
            return redirect('administracion:ver_categorias')
    else:
        form = CategoriaForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Categoría',
    }
    return render(request, 'administracion/categoria/agregar_categoria.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_categoria(request, id):
    """Editar categoría existente"""
    categoria = get_object_or_404(Categoria, id=id)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada correctamente')
            return redirect('administracion:ver_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria,
        'titulo': 'Editar Categoría',
    }
    return render(request, 'administracion/categoria/editar_categoria.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_categoria(request, id):
    """Eliminar categoría"""
    categoria = get_object_or_404(Categoria, id=id)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente')
        return redirect('administracion:ver_categorias')
    
    context = {
        'categoria': categoria,
        'titulo': 'Eliminar Categoría',
    }
    return render(request, 'administracion/categoria/eliminar_categoria.html', context)

# ============ TIPOS ============
@login_required
@user_passes_test(es_administrador)
def ver_tipos(request):
    """Ver lista de tipos"""
    tipos = Tipo.objects.all().order_by('nombre')
    context = {
        'tipos': tipos,
        'titulo': 'Tipos - Administración',
    }
    return render(request, 'administracion/tipo/ver_tipos.html', context)

@login_required
@user_passes_test(es_administrador)
def agregar_tipo(request):
    """Agregar nuevo tipo"""
    if request.method == 'POST':
        form = TipoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo creado correctamente')
            return redirect('administracion:ver_tipos')
    else:
        form = TipoForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Tipo',
    }
    return render(request, 'administracion/tipo/agregar_tipo.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_tipo(request, id):
    """Editar tipo existente"""
    tipo = get_object_or_404(Tipo, id=id)
    
    if request.method == 'POST':
        form = TipoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo actualizado correctamente')
            return redirect('administracion:ver_tipos')
    else:
        form = TipoForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'titulo': 'Editar Tipo',
    }
    return render(request, 'administracion/tipo/editar_tipo.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_tipo(request, id):
    """Eliminar tipo"""
    tipo = get_object_or_404(Tipo, id=id)
    
    if request.method == 'POST':
        tipo.delete()
        messages.success(request, 'Tipo eliminado correctamente')
        return redirect('administracion:ver_tipos')
    
    context = {
        'tipo': tipo,
        'titulo': 'Eliminar Tipo',
    }
    return render(request, 'administracion/tipo/eliminar_tipo.html', context)

# ============ ALIMENTOS ============
@login_required
@user_passes_test(es_administrador)
def ver_alimentos(request):
    categorias = Categoria.objects.all()
    alimentos = Alimento.objects.all()
    categoria_seleccionada = None
    tipo_seleccionado = None
    
    if 'categoria' in request.GET:
        categoria_id = request.GET['categoria']
        if categoria_id:
            alimentos = alimentos.filter(categoria_id=categoria_id)
            categoria_seleccionada = Categoria.objects.get(id=categoria_id)
    
    if 'tipo' in request.GET:
        tipo_id = request.GET['tipo']
        if tipo_id:
            alimentos = alimentos.filter(tipo_id=tipo_id)
            tipo_seleccionado = Tipo.objects.get(id=tipo_id)
    
    context = {
        'alimentos': alimentos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,  # Objeto completo
        'tipo_seleccionado': tipo_seleccionado,  # Objeto completo
    }
    return render(request, 'administracion/alimentos/ver_alimentos.html', context)

@login_required
@user_passes_test(es_administrador)
def agregar_alimento(request):
    """Agregar nuevo alimento"""
    # Obtener categorías y tipos de la base de datos
    categorias = Categoria.objects.all()
    tipos = Tipo.objects.all()
    
    if request.method == 'POST':
        form = AlimentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alimento creado correctamente')
            return redirect('administracion:ver_alimentos')
    else:
        form = AlimentoForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Alimento',
        'categorias': categorias,  # Pasar categorías al template
        'tipos': tipos,           # Pasar tipos al template
    }
    return render(request, 'administracion/alimentos/agregar_alimento.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_alimento(request, id):
    """Editar alimento existente"""
    alimento = get_object_or_404(Alimento, id=id)
    
    if request.method == 'POST':
        form = AlimentoForm(request.POST, request.FILES, instance=alimento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Alimento actualizado correctamente')
            return redirect('administracion:ver_alimentos')
    else:
        form = AlimentoForm(instance=alimento)
    
    context = {
        'form': form,
        'alimento': alimento,
        'titulo': 'Editar Alimento',
    }
    return render(request, 'administracion/alimentos/editar_alimento.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_alimento(request, id):
    """Eliminar alimento"""
    alimento = get_object_or_404(Alimento, id=id)
    
    if request.method == 'POST':
        alimento.delete()
        messages.success(request, 'Alimento eliminado correctamente')
        return redirect('administracion:ver_alimentos')
    
    context = {
        'alimento': alimento,
        'titulo': 'Eliminar Alimento',
    }
    return render(request, 'administracion/alimentos/eliminar_alimento.html', context)

# ============ ACCESORIOS ============
@login_required
@user_passes_test(es_administrador)
def ver_accesorios(request):
    """Ver lista de accesorios"""
    accesorios = Accesorio.objects.all().order_by('-fecha_creacion')
    context = {
        'accesorios': accesorios,
        'titulo': 'Accesorios - Administración',
    }
    return render(request, 'administracion/accesorio/ver_accesorios.html', context)

@login_required
@user_passes_test(es_administrador)
def agregar_accesorio(request):
    """Agregar nuevo accesorio"""
    if request.method == 'POST':
        form = AccesorioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Accesorio creado correctamente')
            return redirect('administracion:ver_accesorios')
    else:
        form = AccesorioForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Accesorio',
    }
    return render(request, 'administracion/accesorio/agregar_accesorio.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_accesorio(request, id):
    """Editar accesorio existente"""
    accesorio = get_object_or_404(Accesorio, id=id)
    
    if request.method == 'POST':
        form = AccesorioForm(request.POST, request.FILES, instance=accesorio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Accesorio actualizado correctamente')
            return redirect('administracion:ver_accesorios')
    else:
        form = AccesorioForm(instance=accesorio)
    
    context = {
        'form': form,
        'accesorio': accesorio,
        'titulo': 'Editar Accesorio',
    }
    return render(request, 'administracion/accesorio/editar_accesorio.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_accesorio(request, id):
    """Eliminar accesorio"""
    accesorio = get_object_or_404(Accesorio, id=id)
    
    if request.method == 'POST':
        accesorio.delete()
        messages.success(request, 'Accesorio eliminado correctamente')
        return redirect('administracion:ver_accesorios')
    
    context = {
        'accesorio': accesorio,
        'titulo': 'Eliminar Accesorio',
    }
    return render(request, 'administracion/accesorio/eliminar_accesorio.html', context)

# ============ MASCOTAS ============
@login_required
@user_passes_test(es_administrador)
def ver_mascotas(request):
    """Ver lista de mascotas"""
    mascotas = Mascota.objects.all().order_by('-fecha_creacion')
    context = {
        'mascotas': mascotas,
        'titulo': 'Mascotas - Administración',
    }
    return render(request, 'administracion/mascota/ver_mascotas.html', context)

@login_required
@user_passes_test(es_administrador)
def agregar_mascota(request):
    """Agregar nueva mascota"""
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mascota creada correctamente')
            return redirect('administracion:ver_mascotas')
    else:
        form = MascotaForm()
    
    context = {
        'form': form,
        'titulo': 'Agregar Mascota',
    }
    return render(request, 'administracion/mascota/agregar_mascota.html', context)

@login_required
@user_passes_test(es_administrador)
def editar_mascota(request, id):
    """Editar mascota existente"""
    mascota = get_object_or_404(Mascota, id=id)
    
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mascota actualizada correctamente')
            return redirect('administracion:ver_mascotas')
    else:
        form = MascotaForm(instance=mascota)
    
    context = {
        'form': form,
        'mascota': mascota,
        'titulo': 'Editar Mascota',
    }
    return render(request, 'administracion/mascota/editar_mascota.html', context)

@login_required
@user_passes_test(es_administrador)
def eliminar_mascota(request, id):
    """Eliminar mascota"""
    mascota = get_object_or_404(Mascota, id=id)
    
    if request.method == 'POST':
        mascota.delete()
        messages.success(request, 'Mascota eliminada correctamente')
        return redirect('administracion:ver_mascotas')
    
    context = {
        'mascota': mascota,
        'titulo': 'Eliminar Mascota',
    }
    return render(request, 'administracion/mascota/eliminar_mascota.html', context)

# ============ PEDIDOS ============
@login_required
@user_passes_test(es_administrador)
def ver_pedidos_admin(request):
    """Ver todos los pedidos"""
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    context = {
        'pedidos': pedidos,
        'titulo': 'Pedidos - Administración',
    }
    return render(request, 'administracion/pedido/ver_pedidos.html', context)

@login_required
@user_passes_test(es_administrador)
def detalle_pedido_admin(request, id):
    """Ver detalle de pedido"""
    pedido = get_object_or_404(Pedido, id=id)
    context = {
        'pedido': pedido,
        'titulo': f'Pedido {pedido.numero_pedido}',
    }
    return render(request, 'administracion/pedido/detalle_pedido.html', context)

@login_required
@user_passes_test(es_administrador)
def cambiar_estado_pedido(request, id):
    """Cambiar estado de pedido"""
    pedido = get_object_or_404(Pedido, id=id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES).keys():
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido actualizado')
    
    return redirect('administracion:detalle_pedido', id=id)

@login_required
@user_passes_test(es_administrador)
def eliminar_pedido(request, id):
    """Eliminar pedido"""
    pedido = get_object_or_404(Pedido, id=id)
    
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, 'Pedido eliminado correctamente')
        return redirect('administracion:ver_pedidos')
    
    context = {
        'pedido': pedido,
        'titulo': 'Eliminar Pedido',
    }
    return render(request, 'administracion/pedido/eliminar_pedido.html', context)

# ============ VENTAS ============
@login_required
@user_passes_test(es_administrador)
def ver_ventas(request):
    """Ver todas las ventas"""
    ventas = Venta.objects.all().order_by('-fecha_venta')
    context = {
        'ventas': ventas,
        'titulo': 'Ventas - Administración',
    }
    return render(request, 'administracion/venta/ver_ventas.html', context)

@login_required
@user_passes_test(es_administrador)
def detalle_venta(request, id):
    """Ver detalle de venta"""
    venta = get_object_or_404(Venta, id=id)
    context = {
        'venta': venta,
        'titulo': f'Venta #{venta.id}',
    }
    return render(request, 'administracion/venta/detalle_venta.html', context)

@login_required
@user_passes_test(es_administrador)
def agregar_venta(request, pedido_id=None):
    """Agregar venta manualmente"""
    pedido = None
    if pedido_id:
        pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            if pedido:
                venta.pedido = pedido
            venta.save()
            messages.success(request, 'Venta registrada correctamente')
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

# ============ REPORTES ============
@login_required
@user_passes_test(es_administrador)
def reportes(request):
    """Página de reportes"""
    context = {
        'titulo': 'Reportes - Administración',
    }
    return render(request, 'administracion/reportes.html', context)

# ==========================================
# VISTAS DEL CLIENTE (las mueve a otro archivo)
# ==========================================
# NOTA: Estas funciones deberían estar en views_cliente.py
# Por ahora las dejo vacías para que no haya errores

def index_cliente(request):
    """Página de inicio para clientes"""
    # Esta función está en views_cliente.py
    pass

def lista_productos_categoria(request, categoria_id, tipo_id=None):
    """Listar productos por categoría"""
    # Esta función está en views_cliente.py
    pass

def detalle_producto(request, tipo_producto, producto_id):
    """Ver detalle de un producto"""
    # Esta función está en views_cliente.py
    pass

# ... y todas las otras funciones del cliente