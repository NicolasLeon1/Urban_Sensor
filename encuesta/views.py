from register.decorators import *
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from register.models import Profile
from .models import Encuesta, Pregunta
from departamento.models import Departamento
from incidencia.models import TipoIncidencia 
@secpla_required
def main_encuesta(request):
    encuesta_listado = Encuesta.objects.order_by('-creado')
    return render(request, 'encuesta/main_encuesta.html', {'encuesta_listado': encuesta_listado})

@secpla_required
def nueva_encuesta(request):
    if request.method == 'POST':
        try:
            titulo_encuesta = request.POST.get('titulo_encuesta')
            descripcion_incidente = request.POST.get('descripcion_incidente')
            prioridad = request.POST.get('prioridad')
            id_departamento = request.POST.get('id_departamento')
            id_tipo_incidencia = request.POST.get('id_tipo_incidencia')
            
            if not all([titulo_encuesta, descripcion_incidente, id_departamento, id_tipo_incidencia]):
                messages.error(request, 'Debe completar todos los campos obligatorios')
                return redirect('nueva_encuesta')
            
            encuesta = Encuesta(
                titulo_encuesta=titulo_encuesta,
                descripcion_incidente=descripcion_incidente,
                prioridad=prioridad,
                id_departamento_id=id_departamento,
                id_tipo_incidencia_id=id_tipo_incidencia
            )
            encuesta.save()
            
            preguntas = request.POST.getlist('preguntas[]')
            for texto_pregunta in preguntas:
                if texto_pregunta.strip():
                    Pregunta.objects.create(
                        id_encuesta=encuesta,
                        texto_pregunta=texto_pregunta.strip()
                    )
            
            messages.success(request, 'Encuesta creada correctamente')
            return redirect('main_encuesta')
            
        except Exception as e:
            messages.error(request, f'Error al crear encuesta: {str(e)}')
            return redirect('nueva_encuesta')
    else:
        departamentos = Departamento.objects.filter(activo=True)
        tipo_incidencias = TipoIncidencia.objects.filter(activo=True)
        tipos_incidencia = TipoIncidencia.objects.filter(activo=True)
        return render(request, 'encuesta/nueva_encuesta.html', {
            'departamentos': departamentos,
            'tipo_incidencias': tipo_incidencias,
            'prioridades': Encuesta.PRIORIDADES
        })

@secpla_required
def ver_encuesta(request, id):
    try:
        encuesta_data = Encuesta.objects.get(pk=id)
        preguntas = Pregunta.objects.filter(id_encuesta=encuesta_data)
        
        return render(request, 'encuesta/ver_encuesta.html', {
            'encuesta_data': encuesta_data,
            'preguntas': preguntas
        })
    except Encuesta.DoesNotExist:
        messages.error(request, 'La encuesta no existe')
        return redirect('main_encuesta')

@secpla_required
def editar_encuesta(request, id):
    if request.method == 'POST':
        id_encuesta = request.POST.get('id_encuesta')
        titulo_encuesta = request.POST.get('titulo_encuesta')
        descripcion_incidente = request.POST.get('descripcion_incidente')
        prioridad = request.POST.get('prioridad')
        id_departamento = request.POST.get('id_departamento')
        id_tipo_incidencia = request.POST.get('id_tipo_incidencia')
        
        if not all([titulo_encuesta, descripcion_incidente, id_departamento, id_tipo_incidencia]):
            messages.error(request, 'Debe completar todos los campos obligatorios')
            return redirect('editar_encuesta', id=id_encuesta)
        
        try:
            encuesta = Encuesta.objects.get(pk=id_encuesta)
            
            if encuesta.activo:
                messages.error(request, 'No es posible editar una encuesta activa. Debe bloquearla primero.')
                return redirect('editar_encuesta', id=id_encuesta)
            
            encuesta.titulo_encuesta = titulo_encuesta
            encuesta.descripcion_incidente = descripcion_incidente
            encuesta.prioridad = prioridad
            encuesta.id_departamento_id = id_departamento
            encuesta.id_tipo_incidencia_id = id_tipo_incidencia
            encuesta.save()
            
            preguntas_eliminadas = request.POST.getlist('preguntas_eliminadas[]')
            for pregunta_id, valor in zip(request.POST.getlist('preguntas_existentes[]'), preguntas_eliminadas):
                if valor == '1':
                    try:
                        pregunta = Pregunta.objects.get(pk=pregunta_id.split('[')[1].split(']')[0])
                        pregunta.delete()
                    except (Pregunta.DoesNotExist, IndexError):
                        pass

            preguntas_nuevas = request.POST.getlist('preguntas_nuevas[]')
            for texto_pregunta in preguntas_nuevas:
                texto_limpio = texto_pregunta.strip()
                if texto_limpio:
                    Pregunta.objects.create(
                        id_encuesta=encuesta,
                        texto_pregunta=texto_limpio
                    )
            
            messages.success(request, 'Encuesta actualizada correctamente')
            return redirect('main_encuesta')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar encuesta: {str(e)}')
            return redirect('editar_encuesta', id=id_encuesta)
    
    else:
        try:
            encuesta_data = Encuesta.objects.get(pk=id)
            preguntas = Pregunta.objects.filter(id_encuesta=encuesta_data)
            departamentos = Departamento.objects.filter(activo=True)
            tipo_incidencias = TipoIncidencia.objects.filter(activo=True)
            
            return render(request, 'encuesta/editar_encuesta.html', {
                'encuesta_data': encuesta_data,
                'preguntas': preguntas,
                'departamentos': departamentos,
                'tipo_incidencias': tipo_incidencias,
                'prioridades': Encuesta.PRIORIDADES
            })
        except Encuesta.DoesNotExist:
            messages.error(request, 'La encuesta no existe')
            return redirect('main_encuesta')

@secpla_required
def toggle_encuesta(request, id):
    try:
        encuesta = Encuesta.objects.get(pk=id)
        encuesta.activo = not encuesta.activo
        encuesta.save()
        if encuesta.activo:
            messages.success(request, 'Encuesta activada correctamente')
        else:
            messages.success(request, 'Encuesta bloqueada correctamente')
        return redirect('main_encuesta')
    except Encuesta.DoesNotExist:
        messages.error(request, 'La encuesta no existe')
        return redirect('main_encuesta')

@secpla_required
def eliminar_encuesta(request, id):
    try:
        encuesta = Encuesta.objects.get(pk=id)
        if encuesta.activo:
            messages.error(request, 'No se puede eliminar una encuesta activa')
            return redirect('main_encuesta')
        encuesta.delete()
        messages.success(request, 'Encuesta eliminada correctamente.')
        return redirect('main_encuesta')
    except Encuesta.DoesNotExist:
        messages.error(request, 'La encuesta no existe')
        return redirect('main_encuesta')