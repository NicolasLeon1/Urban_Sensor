from register.models import Perfiles, User
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from register.models import Perfiles

def tiene_perfil(request, perfil_requerido):
    """
    Helper function para verificar el perfil del usuario en la request.
    Asume que request.user está poblado por el decorador @login_required.
    """
    # El decorador @login_required debe asegurar que request.user exista
    if not hasattr(request, 'user'):
        return False
    
    try:
        perfil_usuario_id = request.user.perfil.id
        perfil_requerido_value = perfil_requerido.value if isinstance(perfil_requerido, Perfiles) else perfil_requerido
        
        return perfil_usuario_id == perfil_requerido_value
    except Exception:
        # En caso de que request.user no sea el objeto User esperado
        return False

def tiene_algun_perfil(request, *perfiles):
    token = request.COOKIES.get('auth_token')
    if not token:
        messages.error(request, 'Necesita iniciar sesion para ver esta seccion.')
        return redirect('login')
    try:
        user = User.objects.filter(activo=True).get(session_token=token)
        if user.expires_at < timezone.now():
            user.session_token = None
            user.expires_at = None
            user.save()
            messages.error(request, 'Su sesion expiro, vuelva a iniciar sesion')
            return redirect('login')
        request.user = user
    except User.DoesNotExist:
        messages.error(request, 'El usuario no existe')
        return redirect('login')
    
    user = request.user
    perfil_usuario = user.perfil.id
    
    perfiles_values = [p.value if isinstance(p, Perfiles) else p for p in perfiles]
    
    return perfil_usuario in perfiles_values

def es_secpla(request):
    return tiene_perfil(request, Perfiles.SECPLA)

def es_direccion(request):
    return tiene_perfil(request, Perfiles.DIRECCION)

def es_departamento(request):
    return tiene_perfil(request, Perfiles.DEPARTAMENTO)

def es_territorial(request):
    return tiene_perfil(request, Perfiles.TERRITORIAL)

def es_cuadrilla(request):
    return tiene_perfil(request, Perfiles.CUADRILLA)