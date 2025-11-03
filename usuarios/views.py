from register.decorators import *
from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from register.models import User, Perfiles, Profile
from departamento.models import Departamento
from direccion.models import Direccion
import string
import secrets

# Vista principal - Listar usuarios
@secpla_required
def main_usuario(request):
    usuario_listado = User.objects.order_by('nombre')
    return render(request, 'usuarios/main_usuario.html', {'usuario_listado': usuario_listado})

@secpla_required
def nuevo_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        username = request.POST.get('username')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        perfil_seleccionado = request.POST.get('perfil')
        
        if nombre == '' or apellido == '' or email == '' or telefono == '' or perfil_seleccionado == '':
            messages.error(request, 'Debe completar todos los campos')
            return redirect('nuevo_usuario')

        if not User.is_email_valid(email):
            messages.error(request, 'El email ya está registrado')
            return redirect('nuevo_usuario')
        
        if not User.is_username_valid(username):
            messages.error(request, 'El username ya está registrado')
            return redirect('nuevo_usuario')
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'El email no es valido')
            return redirect('nuevo_usuario')

        try:
            perfil = Profile.objects.get(pk=perfil_seleccionado)
            user = User(
                username=username,
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=telefono,
                perfil=perfil
            )
            if perfil_seleccionado == Perfiles.DEPARTAMENTO:
                departamento_id = request.POST.get('departamento_especifico')
                try:
                    departamento = Departamento.objects.filter(activo=True).get(pk=departamento_id)
                    user.departamento = departamento
                except Departamento.DoesNotExist:
                    messages.error(request, 'Departamento no existe')
                    return redirect('nuevo_usuario')
            elif perfil_seleccionado == Perfiles.DIRECCION:
                direccion_id = request.POST.get('direccion_especifica')
                try:
                    direccion = Direccion.objects.filter(activo=True).get(pk=direccion_id)
                    user.direccion = direccion
                except Direccion.DoesNotExist:
                    messages.error(request, 'Departamento no existe')
                    return redirect('nuevo_usuario')
            
            
            characters = string.ascii_letters + string.digits + string.punctuation
            temporary_password = ''.join(secrets.choice(characters) for _ in range(8))

            send_mail(
                subject="Se ha creado su usuario en la municipalidad!",
                message=f"Se ha creado un nuevo usuario con la siguiente informacion:\nUsername:{username}\nContraseña Temporal:{temporary_password}\nAl momento de iniciar sesion, se le pedira confirmar sus datos.",
                from_email='urban_sensor@municipalidad.cl',
                recipient_list=[email],
                fail_silently=False
            )

            user.set_password(temporary_password)
            user.save()
            messages.success(request, 'Usuario creado correctamente')
            return redirect('main_usuario')
            
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return redirect('nuevo_usuario')
    else:
        perfiles_listado = Profile.objects.all()
        direccion_listado = Direccion.objects.filter(activo=True)
        departamento_listado = Departamento.objects.filter(activo=True)
        context = {
            'perfiles_listado': perfiles_listado,
            'direccion_listado': direccion_listado,
            'departamento_listado': departamento_listado
        }
        return render(request, 'usuarios/nuevo_usuario.html', context)

@login_required
@secpla_required
def editar_usuario(request, id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        username = request.POST.get('username')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        perfil_seleccionado = request.POST.get('perfil')
        
        if nombre == '' or apellido == '' or email == '' or telefono == '' or perfil_seleccionado == '':
            messages.error(request, 'Debe completar todos los campos')
            return redirect('editar_usuario', id)
        
        try:
            perfil = Profile.objects.get(pk=perfil_seleccionado)
            user = User.objects.get(pk=id)

            if not User.is_email_valid(email) and user.email != email:
                messages.error(request, 'El email ya está registrado')
                return redirect('editar_usuario', id)
            
            if not User.is_username_valid(username) and user.username != username:
                messages.error(request, 'El username ya está registrado')
                return redirect('editar_usuario', id)
            
            user.username = username
            user.nombre = nombre
            user.apellido = apellido
            user.email = email
            user.telefono = telefono
            user.perfil = perfil
            if perfil_seleccionado == Perfiles.DEPARTAMENTO:
                departamento_id = request.POST.get('departamento_especifico')
                try:
                    departamento = Departamento.objects.filter(activo=True).get(pk=departamento_id)
                    user.departamento = departamento
                except Departamento.DoesNotExist:
                    messages.error(request, 'Departamento no existe')
                    return redirect('editar_usuario', id)
            elif perfil_seleccionado == Perfiles.DIRECCION:
                direccion_id = request.POST.get('direccion_especifica')
                try:
                    direccion = Direccion.objects.filter(activo=True).get(pk=direccion_id)
                    user.direccion = direccion
                except Direccion.DoesNotExist:
                    messages.error(request, 'Departamento no existe')
                    return redirect('editar_usuario', id)
            user.set_password('zzz')
            user.save()
            messages.success(request, 'Usuario creado correctamente')
            return redirect('main_usuario')
            
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return redirect('editar_usuario', id)
    else:
        try:
            usuario_data = User.objects.get(pk=id)
        except User.DoesNotExist:
            messages.error(request, 'Error el usuario no existe.')
        perfiles_listado = Profile.objects.all()
        direccion_listado = Direccion.objects.filter(activo=True)
        departamento_listado = Departamento.objects.filter(activo=True)
        context = {
            'usuario_data': usuario_data,
            'perfiles_listado': perfiles_listado,
            'direccion_listado': direccion_listado,
            'departamento_listado': departamento_listado
        }
        return render(request, 'usuarios/editar_usuario.html', context)

@secpla_required
def ver_usuario(request, id):
    try:
        usuario_data = User.objects.get(pk=id)
    except User.DoesNotExist:
        messages.error(request, 'Error el usuario no existe.')
    return render(request, 'usuarios/ver_usuario.html', {'usuario_data': usuario_data})

@secpla_required
def toggle_usuario(request, id):
    try:
        usuario_data = User.objects.get(pk=id)
        usuario_data.activo = not usuario_data.activo
        if usuario_data.activo:
            messages.success(request, 'Usuario activado con exito')
        else:
            messages.success(request, 'Usuario bloqueado con exito')
        usuario_data.save()
        return redirect('main_usuario')
    except User.DoesNotExist:
        messages.error(request, 'Error el usuario no existe.')
    return render(request, 'usuarios/ver_usuario.html', {'usuario_data': usuario_data})

@secpla_required
def eliminar_usuario(request, id):
    try:
        usuario_data = User.objects.get(pk=id)
        if usuario_data.activo:
            messages.error(request, 'Error el usuario debe estar bloqueado para poder borrarlo.')
            return redirect('main_usuario')
        usuario_data.delete()
        messages.success(request, 'Usuario eliminado con exito')
        return redirect('main_usuario')
    except User.DoesNotExist:
        messages.error(request, 'Error el usuario no existe.')
    return render(request, 'usuarios/ver_usuario.html', {'usuario_data': usuario_data})
