from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from register.decorators import login_required
from .models import User, Profile, Perfiles
from departamento.models import Departamento
from direccion.models import Direccion
from register.utils import *
import hashlib

# Create your views here.

@login_required
def first_session(request):
    user = request.user
    if not user.first_session:
        return redirect('to_dashboard')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        username = request.POST.get('username')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if user.username != username:
            if not User.is_username_valid(username):
                messages.error(request, 'El username ya existe.')
                return redirect('first_session')
        
        if user.email != email:
            if not User.is_email_valid(email):
                messages.error(request, 'El email ya existe.')
                return redirect('first_session')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('first_session')
        
        is_valid, errors = User.validar_contraseña(password1, username, nombre, apellido)
        if not is_valid:
            for error in errors:
                messages.error(request, error)
            return redirect('first_session')
        user.nombre = nombre
        user.apellido = apellido
        user.username = username
        user.telefono = telefono
        user.email = email
        user.set_password(password1)
        user.first_session = False
        user.save()
        messages.success(request, 'Usuario confirmado con exito')
        return redirect('to_dashboard')
    user_data = request.user
    return render(request, 'register/first_session.html', {'usuario_data': user_data})

def login_view(request):
    token = request.COOKIES.get('auth_token')
    if token:
        try:
            user = User.objects.get(session_token=token)
            return render(request, 'register/logged.html', {'user_data': user})
        except User.DoesNotExist:
            response = redirect('login')
            response.delete_cookie('auth_token')
            return response

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'El nombre de usuario no existe.')
            return redirect('login')
        
        if not user.activo:
            messages.error(request, 'Su usuario se encuentra bloqueado, contacte con administracion')
            return redirect('login')
        
        if not user.check_password(password):
            messages.error(request, 'La contraseña es incorrecta')
            return redirect('login')
        
        token = User.generate_token()
        expires_at = timezone.now() + timedelta(days=30)

        user.session_token = token
        user.expires_at = expires_at
        user.save()

        response = redirect('first_session') if user.first_session  else redirect('to_dashboard')
        response.set_cookie('auth_token', token, max_age=30*24*60*60)
        return response
    
    return render(request, 'register/login.html')

@login_required
def logout(request):
    user = request.user
    user.session_token = None
    user.expires_at = None
    user.save()
    response = redirect('login')
    response.delete_cookie('auth_token')
    messages.success(request, 'Has cerrado sesión correctamente.')
    
    return response