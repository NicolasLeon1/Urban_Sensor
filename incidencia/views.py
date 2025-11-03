from register.decorators import *
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import TipoIncidencia
from direccion.models import Direccion
from departamento.models import Departamento

@secpla_required
def main_incidencia(request):
    incidencia_listado = TipoIncidencia.objects.select_related('id_direccion', 'id_departamento').order_by('id')
    return render(request, 'incidencia/main_incidencia.html', {'incidencia_listado': incidencia_listado})

@secpla_required
def nueva_incidencia(request):
    if request.method == 'POST':
        nombre_incidencia = request.POST.get('nombre_incidencia')
        id_direccion = request.POST.get('id_direccion')
        id_departamento = request.POST.get('id_departamento')
        
        if not all([nombre_incidencia, id_direccion, id_departamento]):
            messages.error(request, 'Debe completar todos los campos obligatorios')
            return redirect('nueva_incidencia')
        
        try:
            TipoIncidencia.objects.create(
                nombre_incidencia=nombre_incidencia,
                id_direccion_id=id_direccion,
                id_departamento_id=id_departamento
            )
            messages.success(request, 'Tipo de incidencia creado correctamente')
            return redirect('main_incidencia')
        except Exception as e:
            messages.error(request, f'Error al crear tipo de incidencia: {str(e)}')
            return redirect('nueva_incidencia')
    else:
        direcciones = Direccion.objects.filter(activo=True)
        departamentos = Departamento.objects.filter(activo=True)
        return render(request, 'incidencia/nueva_incidencia.html', {
            'direcciones': direcciones,
            'departamentos': departamentos
        })

@secpla_required
def ver_incidencia(request, id):
    try:
        incidencia_data = TipoIncidencia.objects.select_related('id_direccion', 'id_departamento').get(pk=id)
        return render(request, 'incidencia/ver_incidencia.html', {'incidencia_data': incidencia_data})
    except TipoIncidencia.DoesNotExist:
        messages.error(request, 'El tipo de incidencia no existe')
        return redirect('main_incidencia')

@secpla_required
def editar_incidencia(request, id):
    if request.method == 'POST':
        nombre_incidencia = request.POST.get('nombre_incidencia')
        id_direccion = request.POST.get('id_direccion')
        id_departamento = request.POST.get('id_departamento')
        
        if not all([nombre_incidencia, id_direccion, id_departamento]):
            messages.error(request, 'Debe completar todos los campos obligatorios')
            return redirect('editar_incidencia', id=id)
        
        try:
            incidencia = TipoIncidencia.objects.get(pk=id)
            if incidencia.activo:
                messages.error(request, 'No es posible editar un tipo de incidencia activo. Debe bloquearlo primero.')
                return redirect('editar_incidencia', id=id)
            
            incidencia.nombre_incidencia = nombre_incidencia
            incidencia.id_direccion_id = id_direccion
            incidencia.id_departamento_id = id_departamento
            incidencia.save()
            messages.success(request, 'Tipo de incidencia actualizado correctamente')
            return redirect('main_incidencia')
        except Exception as e:
            messages.error(request, f'Error al actualizar tipo de incidencia: {str(e)}')
            return redirect('editar_incidencia', id=id)
    else:
        try:
            incidencia_data = TipoIncidencia.objects.get(pk=id)
            direcciones = Direccion.objects.filter(activo=True)
            departamentos = Departamento.objects.filter(activo=True)
            return render(request, 'incidencia/editar_incidencia.html', {
                'incidencia_data': incidencia_data,
                'direcciones': direcciones,
                'departamentos': departamentos
            })
        except TipoIncidencia.DoesNotExist:
            messages.error(request, 'El tipo de incidencia no existe')
            return redirect('main_incidencia')

@secpla_required
def toggle_incidencia(request, id):
    try:
        incidencia = TipoIncidencia.objects.get(pk=id)
        incidencia.activo = not incidencia.activo
        incidencia.save()
        status = 'activado' if incidencia.activo else 'bloqueado'
        messages.success(request, f'Tipo de incidencia {status} correctamente')
        return redirect('main_incidencia')
    except TipoIncidencia.DoesNotExist:
        messages.error(request, 'El tipo de incidencia no existe')
        return redirect('main_incidencia')