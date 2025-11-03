from register.models import Perfiles, User
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

def tiene_perfil(request, perfil):
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
    
    perfil_value = perfil.value if isinstance(perfil, Perfiles) else perfil
    
    return perfil_usuario == perfil_value

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