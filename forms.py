# app_mascotas/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Usuario, Categoria, Tipo, Alimento, 
    Accesorio, Mascota, Pedido, Venta
)

# ==========================================
# FORMULARIOS DE AUTENTICACIÓN
# ==========================================
class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    telefono = forms.CharField(max_length=15, required=False)
    direccion = forms.CharField(widget=forms.Textarea, required=False)
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 
                 'first_name', 'last_name', 'telefono', 
                 'direccion', 'fecha_nacimiento']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'

class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

# ==========================================
# FORMULARIOS DE CATÁLOGO
# ==========================================
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class TipoForm(forms.ModelForm):
    class Meta:
        model = Tipo
        fields = ['nombre', 'descripcion', 'icono']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

# ==========================================
# FORMULARIOS DE PRODUCTOS
# ==========================================
class AlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimento
        fields = [
            'nombre', 'categoria', 'tipo', 'descripcion',
            'precio', 'precio_original', 'stock', 'imagen',
            'destacado', 'activo'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
            'precio_original': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['destacado', 'activo']:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'

class AccesorioForm(forms.ModelForm):
    class Meta:
        model = Accesorio
        fields = [
            'nombre', 'categoria', 'tipo', 'descripcion',
            'precio', 'precio_original', 'stock', 'imagen',
            'destacado', 'activo'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
            'precio_original': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['destacado', 'activo']:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'

# ==========================================
# FORMULARIOS DE MASCOTAS
# ==========================================
class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = [
            'nombre', 'tipo', 'raza', 'edad',
            'descripcion', 'precio', 'imagen', 'estado'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'edad': forms.NumberInput(attrs={'min': '1'}),
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

# ==========================================
# FORMULARIOS DE USUARIOS (ADMIN)
# ==========================================
class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Contraseña (dejar en blanco para no cambiar)"
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'telefono', 'direccion', 'fecha_nacimiento',
            'rol', 'avatar', 'is_active'
        ]
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['is_active']:
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

# ==========================================
# FORMULARIOS DE PEDIDOS Y VENTAS
# ==========================================
class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado', 'direccion_envio', 'notas']
        widgets = {
            'direccion_envio': forms.Textarea(attrs={'rows': 3}),
            'notas': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['metodo_pago', 'referencia_pago', 'vendedor']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        # Filtrar solo usuarios con rol admin o empleado
        self.fields['vendedor'].queryset = Usuario.objects.filter(
            rol__in=['admin', 'empleado']
        )

# ==========================================
# FORMULARIOS DE BÚSQUEDA Y FILTROS
# ==========================================
class BusquedaForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Buscar...'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['query'].widget.attrs.update({'class': 'form-control'})

class FiltroAlimentosForm(forms.Form):
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Todas las categorías"
    )
    tipo = forms.ModelChoiceField(
        queryset=Tipo.objects.all(),
        required=False,
        empty_label="Todos los tipos"
    )
    min_precio = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Mínimo', 'step': '0.01'})
    )
    max_precio = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Máximo', 'step': '0.01'})
    )
    destacados = forms.BooleanField(required=False, label="Solo destacados")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'destacados':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'