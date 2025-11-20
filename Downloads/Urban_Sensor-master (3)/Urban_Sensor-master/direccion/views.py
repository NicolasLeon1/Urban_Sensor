from django.shortcuts import render, redirect, get_object_or_404
from .models import Direccion
from django.contrib import messages
from .models import Direccion
from register.decorators import *
from register.models import Profile

@secpla_required
def main_direccion(request):
    direcciones_listado = Direccion.objects.all().order_by('nombre_direccion')
    return render(request, 'direccion/main_direccion.html', {'direcciones_listado': direcciones_listado})

@secpla_required
def nueva_direccion(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_direccion')
        if not nombre:
            messages.error(request, 'El nombre no puede estar vacío.')
            return redirect('nueva_direccion')
        direccion = Direccion(nombre_direccion=nombre)
        direccion.save()
        messages.success(request, 'Dirección creada correctamente.')
        return redirect('main_direccion')
    else:
        return render(request, 'direccion/nueva_direccion.html')

@secpla_required
def editar_direccion(request, id):
    try:
        direccion = Direccion.objects.get(pk=id)
    except Direccion.DoesNotExist:
        messages.error(request, 'La direccion no existe')
        return redirect('main_direccion')
    if request.method == 'POST':
        nombre = request.POST.get('nombre_direccion')
        if not nombre:
            messages.error(request, 'El nombre no puede estar vacío.')
            return redirect('editar_direccion', id)
        
        direccion.nombre_direccion = nombre
        direccion.save()
        messages.success(request, 'Dirección actualizada correctamente.')
        return redirect('main_direccion')
    else:
        return render(request, 'direccion/editar_direccion.html', {'direccion_data': direccion})
    
@secpla_required
def toggle_direccion(request, id):
    try:
        direccion = Direccion.objects.get(pk=id)
        direccion.activo = not direccion.activo
        if direccion.activo:
            messages.success(request, f'La dirección "{direccion.nombre_direccion}" ha sido desbloqueada.')
        else:
            messages.success(request, f'La dirección "{direccion.nombre_direccion}" ha sido bloqueada.')
        direccion.save()
        return redirect('main_direccion')
    except Direccion.DoesNotExist:
        messages.error(request, 'La direccion no existe')
        return redirect('main_direccion')

@secpla_required
def eliminar_direccion(request, id):
    try:
        direccion = Direccion.objects.get(pk=id)
        if direccion.activo:
            messages.error(request, 'La dirección debe estar bloqueada para poder eliminarla.')
            return redirect('main_direccion')
        direccion.delete()
        messages.success(request, 'Direccion eliminada con exito.')
        return redirect('main_direccion')
    except Direccion.DoesNotExist:
        messages.error(request, 'La direccion no existe')
        return redirect('main_direccion')

@secpla_required
def ver_direccion(request, id):
    try:
        direccion_data = Direccion.objects.get(pk=id)
        return render(request, 'direccion/ver_direccion.html', {'direccion_data': direccion_data})
    except Direccion.DoesNotExist:
        messages.error(request, 'La direccion no existe')
        return redirect('main_direccion')
    