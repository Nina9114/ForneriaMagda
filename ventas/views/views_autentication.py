from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from ..funciones.formularios import RegistrationForms, LoginForm

# ================================================================
# =                    VISTA: LANDING PAGE                       =
# ================================================================
# 
# Esta es la página principal que verán los visitantes cuando
# accedan a la raíz del sitio ("/").
# 
# PERSONALIZACIÓN:
# - Puedes pasar datos adicionales en el contexto si necesitas
#   mostrar información dinámica (ej: productos destacados)
# - Por ahora es una página estática con el template landing.html

def home(request):
    """
    Vista para la landing page principal del sitio.
    
    Esta página muestra:
    - Hero section con imagen/video de fondo
    - Sección "Sobre Nosotros" con la historia de La Forneria Emporio
    - Footer con información de contacto, horarios y redes sociales
    
    Args:
        request: HttpRequest de Django
    
    Returns:
        HttpResponse: Renderiza el template landing.html
    """
    contexto = {
        # Contexto vacío - toda la información está en el template
    }
    
    return render(request, 'landing.html', contexto)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            entrada = form.cleaned_data['username']   # puede ser correo o username
            password = form.cleaned_data['password']

            # Si es correo, buscar el usuario y obtener su username
            if '@' in entrada:
                try:
                    usuario_obj = User.objects.get(email=entrada.lower())
                    username_para_auth = usuario_obj.username
                except User.DoesNotExist:
                    form.add_error('username', 'Este correo no está registrado.')
                    return render(request, 'login.html', {'form': form})
            else:
                username_para_auth = entrada

            # Autenticar con username y password
            user = authenticate(request, username=username_para_auth, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')

            form.add_error(None, 'Usuario o contraseña incorrectos.')
            return render(request, 'login.html', {'form': form})

        # Form inválido: re-render con errores
        return render(request, 'login.html', {'form': form})

    # GET: mostrar formulario vacío
    form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    
    if request.method == 'POST':
        form = RegistrationForms(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            user = User.objects.create_user(username=username, email=email, password=password)

            messages.success(request, "Cuenta creada con exito")
            return redirect('login')

    else:
        form = RegistrationForms()

    return render(request, 'registro.html', {'form': form})   


def dashboard_view(request):
    """
    Vista del dashboard principal.
    
    Genera alertas automáticamente al cargar el dashboard para:
    - Productos por vencer
    - Stock bajo
    - Facturas vencidas o por vencer
    """
    from ventas.models import Alertas
    
    # Generar alertas automáticamente al cargar el dashboard
    try:
        Alertas.generar_alertas_automaticas()
    except Exception as e:
        # Si falla la generación de alertas, no bloquear la carga del dashboard
        import logging
        logger = logging.getLogger('ventas')
        logger.error(f'Error al generar alertas automáticas en dashboard: {str(e)}', exc_info=True)
    
    return render(request, 'dashboard.html')

def proximamente_view(request, feature=None):
    titulo = "En construcción" if not feature else f"{feature.replace('-', ' ').title()} en construcción"
    contexto = {
        "title": titulo,
        "message": "Estamos trabajando en esta sección. Pronto estará disponible.",
        "primary_action_url": "/",
        "primary_action_text": "Volver al inicio",
        "secondary_action_text": "Ir al dashboard",
    }
    return render(request, "proximamente.html", contexto)

def recuperar_contrasena_view(request):
    """
    Vista provisional para recuperar contraseña.
    Muestra una página informativa indicando que la funcionalidad
    estará disponible próximamente.
    """
    return render(request, 'recuperar_contrasena.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('login')

# NUEVO: gestión de usuarios (solo superusuario)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from ..funciones.formularios import AdminUserEditForm

def _es_superusuario(u):
    return u.is_superuser

@login_required
@user_passes_test(_es_superusuario)
def usuarios_list_view(request):
    usuarios = User.objects.all().order_by('-is_superuser', '-is_staff', 'username')
    return render(request, 'usuarios_list.html', {'usuarios': usuarios})

@login_required
@user_passes_test(_es_superusuario)
def usuario_editar_view(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()
            nueva = form.cleaned_data.get('password')
            if nueva:
                usuario.set_password(nueva)
                usuario.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('usuarios_list')
    else:
        form = AdminUserEditForm(instance=usuario)
    return render(request, 'usuario_editar.html', {'form': form, 'usuario': usuario})

@login_required
@user_passes_test(_es_superusuario)
def usuario_eliminar_view(request, user_id):
    usuario = get_object_or_404(User, pk=user_id)
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario mientras estás conectado.")
        return redirect('usuarios_list')
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, "Usuario eliminado.")
        return redirect('usuarios_list')
    return render(request, 'confirmar_eliminar_usuario.html', {'usuario': usuario})
    
