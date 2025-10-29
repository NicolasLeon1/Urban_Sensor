from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from direccion.models import Direccion
from departamento.models import Departamento
from registration.models import Profile

# Create your views here.

@login_required
def main_departamento(request):
    try:
        profile = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    if profile.group_id == 1:
        listado_departamento = Departamento.objects.all().order_by('nombre_departamento')
        return render(request, 'departamento/main_departamento.html', {'listado_departamento': listado_departamento})
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

@login_required
def crear_departamento(request):
    try:
        profile = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    if profile.group_id == 1:
        if request.method == 'POST':
            nombre_departamento = request.POST.get('nombre_departamento')
            direccion_id = request.POST.get('direccion')
            if not all([nombre_departamento, direccion_id]):
                messages.error(request, f'El formulario debe estar completo.')
                return redirect('crear_departamento')
            try:
                direccion = Direccion.objects.filter(estado='Activo').get(pk=direccion_id)
            except Direccion.DoesNotExist:
                messages.error(request, 'Error, esa direccion no existe.')
                return redirect('crear_departamento')
            departamento = Departamento(
                nombre_departamento = nombre_departamento,
                direccion = direccion)
            departamento.save()
            messages.success(request, 'Departamento creado con exito')
            return redirect('main_departamento')
        else:
            direcciones = Direccion.objects.all().filter(estado='Activo')
            return render(request, 'departamento/crear_departamento.html', {'direcciones': direcciones})
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

@login_required
def ver_departamento(request, id):
    try:
        profile = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    if profile.group_id == 1:
        try:
            departamento_data = Departamento.objects.get(pk=id)
            return render(request, 'departamento/ver_departamento.html', {'departamento_data': departamento_data})
        except Departamento.DoesNotExist:
            messages.error(request, 'El departamento no existe')
            return redirect('main_departamento')
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

@login_required
def editar_departamento(request, id):
    try:
        profile = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    if profile.group_id == 1:
        if request.method == 'POST':
            nombre_departamento = request.POST.get('nombre_departamento')
            direccion_id = request.POST.get('direccion')
            if not all([nombre_departamento, direccion_id]):
                messages.error(request, f'El formulario debe estar completo.')
                return redirect('editar_departamento')
            try:
                direccion = Direccion.objects.filter(estado='Activo').get(pk=direccion_id)
            except Direccion.DoesNotExist:
                messages.error(request, 'Error, esa direccion no existe.')
                return redirect('editar_departamento')
            try:
                departamento = Departamento.objects.get(pk=id)
                departamento.nombre_departamento = nombre_departamento
                departamento.direccion = direccion
            except Departamento.DoesNotExist:
                messages.error(request, 'Error, ese departamento no existe.')
                return redirect('editar_departamento')
            departamento.save()
            messages.success(request, 'Departamento creado con exito')
            return redirect('main_departamento')
        else:
            direcciones = Direccion.objects.all().filter(estado='Activo')
            try:
                departamento_data = Departamento.objects.get(pk=id)
            except Departamento.DoesNotExist:
                messages.error(request, 'Error, ese departamento no existe.')
                return redirect('editar_departamento')
            return render(request, 'departamento/editar_departamento.html', {'departamento_data': departamento_data, 'direcciones': direcciones})
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

@login_required
def bloquear_departamento(request, id):
    try:
        profile = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    if profile.group_id == 1:
        try:
            departamento = Departamento.objects.get(pk=id)
            departamento.activo = False
            departamento.save()
            messages.success(request, 'Departamento bloqueado con exito')
            return redirect('main_departamento')
        except Departamento.DoesNotExist:
            messages.error(request, 'El departamento no existe')
            return redirect('main_departamento')
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

@login_required
def activar_departamento(request, id):
    try:
        profile = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    if profile.group_id == 1:
        try:
            departamento = Departamento.objects.get(pk=id)
            departamento.activo = True
            departamento.save()
            messages.success(request, 'Departamento activado con exito')
            return redirect('main_departamento')
        except Departamento.DoesNotExist:
            messages.error(request, 'El departamento no existe')
            return redirect('main_departamento')
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

@login_required
def eliminar_departamento(request, id):
    try:
        profile = Profile.objects.get(user_id = request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    if profile.group_id == 1:
        try:
            departamento = Departamento.objects.get(pk=id)
            if not departamento.activo:
                departamento.delete()
                messages.success(request, 'Departamento activado con exito')
            else:
                messages.error(request, 'El departamento debe estar bloqueado para poder eliminar.')
            return redirect('main_departamento')
        except Departamento.DoesNotExist:
            messages.error(request, 'El departamento no existe')
            return redirect('main_departamento')
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')
