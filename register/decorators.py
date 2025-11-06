from django.shortcuts import redirect
from functools import wraps
from register.models import User, Perfiles
from django.utils import timezone
from django.contrib import messages

def login_required(view_func):
    @wraps(view_func)

    def wrapper(request, *args, **kwargs):
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
                response = redirect('login')
                response.delete_cookie('auth_token')
                return response
            request.user = user
        except User.DoesNotExist:
            messages.error(request, 'El usuario no existe')
            response = redirect('login')
            response.delete_cookie('auth_token')
            return response
        
        return view_func(request, *args, **kwargs)
    
    return wrapper

def check_perfil(*perfiles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
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
                    response = redirect('login')
                    response.delete_cookie('auth_token')
                    return response
                request.user = user
            except User.DoesNotExist:
                messages.error(request, 'El usuario no existe')
                response = redirect('login')
                response.delete_cookie('auth_token')
                return response
            
            perfil_usuario = user.perfil.id
            
            perfiles_permitidos_values = [p.value if isinstance(p, Perfiles) else p for p in perfiles_permitidos]
            
            if perfil_usuario not in perfiles_permitidos_values:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('dashboard_main')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def secpla_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return check_perfil(Perfiles.SECPLA)(view_func)(request, *args, **kwargs)
    return wrapper

def direccion_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return check_perfil(Perfiles.DIRECCION)(view_func)(request, *args, **kwargs)
    return wrapper

def departamento_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return check_perfil(Perfiles.DEPARTAMENTO)(view_func)(request, *args, **kwargs)
    return wrapper

def territorial_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return check_perfil(Perfiles.TERRITORIAL)(view_func)(request, *args, **kwargs)
    return wrapper

def cuadrilla_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return check_perfil(Perfiles.CUADRILLA)(view_func)(request, *args, **kwargs)
    return wrapper