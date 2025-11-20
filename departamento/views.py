from django.shortcuts import render, redirect
from django.contrib import messages
from register.decorators import *
from direccion.models import Direccion
from departamento.models import Departamento
from register.models import Profile

# Create your views here.

@secpla_required
def main_departamento(request):
    listado_departamento = Departamento.objects.all().order_by('nombre_departamento')
    return render(request, 'departamento/main_departamento.html', {'listado_departamento': listado_departamento})

@secpla_required
def crear_departamento(request):
    if request.method == 'POST':
        nombre_departamento = request.POST.get('nombre_departamento')
        direccion_id = request.POST.get('direccion')
        if not all([nombre_departamento, direccion_id]):
            messages.error(request, f'El formulario debe estar completo.')
            return redirect('crear_departamento')
        try:
            direccion = Direccion.objects.filter(activo=True).get(pk=direccion_id)
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
        direcciones = Direccion.objects.all().filter(activo=True)
        return render(request, 'departamento/crear_departamento.html', {'direcciones': direcciones})

@secpla_required
def ver_departamento(request, id):
    try:
        departamento_data = Departamento.objects.get(pk=id)
        return render(request, 'departamento/ver_departamento.html', {'departamento_data': departamento_data})
    except Departamento.DoesNotExist:
        messages.error(request, 'El departamento no existe')
        return redirect('main_departamento')

@secpla_required
def editar_departamento(request, id):
    if request.method == 'POST':
        nombre_departamento = request.POST.get('nombre_departamento')
        direccion_id = request.POST.get('direccion')
        if not all([nombre_departamento, direccion_id]):
            messages.error(request, f'El formulario debe estar completo.')
            return redirect('editar_departamento')
        try:
            direccion = Direccion.objects.filter(activo=True).get(pk=direccion_id)
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
        direcciones = Direccion.objects.all().filter(activo=True)
        try:
            departamento_data = Departamento.objects.get(pk=id)
        except Departamento.DoesNotExist:
            messages.error(request, 'Error, ese departamento no existe.')
            return redirect('editar_departamento')
        return render(request, 'departamento/editar_departamento.html', {'departamento_data': departamento_data, 'direcciones': direcciones})

@secpla_required
def bloquear_departamento(request, id):
    try:
        departamento = Departamento.objects.get(pk=id)
        departamento.activo = False
        departamento.save()
        messages.success(request, 'Departamento bloqueado con exito')
        return redirect('main_departamento')
    except Departamento.DoesNotExist:
        messages.error(request, 'El departamento no existe')
        return redirect('main_departamento')

@secpla_required
def activar_departamento(request, id):
    try:
        departamento = Departamento.objects.get(pk=id)
        departamento.activo = True
        departamento.save()
        messages.success(request, 'Departamento activado con exito')
        return redirect('main_departamento')
    except Departamento.DoesNotExist:
        messages.error(request, 'El departamento no existe')
        return redirect('main_departamento')

@secpla_required
def eliminar_departamento(request, id):
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
