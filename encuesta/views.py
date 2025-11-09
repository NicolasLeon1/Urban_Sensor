from register.decorators import *
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import JsonResponse
from register.models import Profile
from .models import Encuesta, Pregunta
from departamento.models import Departamento
from incidencia.models import TipoIncidencia 

# --- IMPORTS AÑADIDOS ---
from register.decorators import territorial_required
# Usar la importación de string para romper el ciclo en las VISTAS también es una buena práctica
from incidencia.models import SolicitudIncidencia, RespuestaSolicitud 
from django.db import transaction # Para asegurar que la solicitud y sus respuestas se creen juntas

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
            
            preguntas_a_eliminar = request.POST.getlist('eliminar_preguntas')
            
            for pregunta_id in preguntas_a_eliminar:
                try:
                    pregunta = Pregunta.objects.get(pk=pregunta_id, id_encuesta=encuesta)
                    pregunta.delete()
                except Pregunta.DoesNotExist:
                    pass
            
            for key, texto_pregunta in request.POST.items():
                if key.startswith('preguntas_existentes['):
                    pregunta_id = key.split('[')[1].split(']')[0]
                    texto_limpio = texto_pregunta.strip()
                    
                    if pregunta_id not in preguntas_a_eliminar and texto_limpio:
                        try:
                            pregunta = Pregunta.objects.get(pk=pregunta_id, id_encuesta=encuesta)
                            pregunta.texto_pregunta = texto_limpio
                            pregunta.save()
                        except Pregunta.DoesNotExist:
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
                'preguntas_existentes': preguntas,
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

# --- NUEVAS VISTAS PARA PERFIL TERRITORIAL ---

@territorial_required
def listar_encuestas_responder(request):
    """
    Muestra al usuario Territorial la lista de Encuestas (plantillas)
    activas que puede utilizar para crear una nueva Solicitud de Incidencia.
    (Requerimiento: Territorial ... eligiendo la encuesta adecuada)
    """
    encuestas_activas = Encuesta.objects.filter(activo=True).select_related(
        'id_tipo_incidencia', 
        'id_departamento'
    ).order_by('titulo_encuesta')
    
    return render(request, 'encuesta/listar_encuestas_responder.html', {
        'encuestas_listado': encuestas_activas
    })

@territorial_required
@transaction.atomic # Si falla el guardado de una respuesta, se anula la solicitud
def responder_encuesta(request, id_encuesta):
    """
    Permite al usuario Territorial rellenar las preguntas de una Encuesta
    para crear una nueva SolicitudIncidencia.
    (Requerimiento: Territorial ... crea incidencias)
    """
    try:
        # Optimizar consulta cargando preguntas relacionadas
        encuesta = Encuesta.objects.prefetch_related('pregunta_set').get(pk=id_encuesta, activo=True)
    except Encuesta.DoesNotExist:
        messages.error(request, 'La encuesta seleccionada no existe o no está activa.')
        return redirect('listar_encuestas_responder')

    if request.method == 'POST':
        try:
            # 1. Crear la SolicitudIncidencia (el "ticket")
            tipo_incidencia = encuesta.id_tipo_incidencia

            ubicacion = request.POST.get('ubicacion')
            
            solicitud = SolicitudIncidencia.objects.create(
                encuesta_base=encuesta,
                creado_por=request.user, # request.user es inyectado por @territorial_required
                estado='abierta',
                # Se copia la asignación desde la plantilla de encuesta
                ubicacion=ubicacion,
                direccion_asignada=tipo_incidencia.id_direccion,
                departamento_asignado=tipo_incidencia.id_departamento
            )
            
            # 2. Recorrer las preguntas de la plantilla y guardar las respuestas
            preguntas = encuesta.pregunta_set.all()
            respuestas_a_crear = []
            
            for pregunta in preguntas:
                # El 'name' del input en el HTML debe ser "pregunta_[id_pregunta]"
                respuesta_texto = request.POST.get(f'pregunta_{pregunta.id}')
                
                if not respuesta_texto or not respuesta_texto.strip():
                    # Validación simple: asumimos que todas las preguntas son obligatorias
                    raise ValueError(f"La pregunta '{pregunta.texto_pregunta}' es obligatoria.")
                
                respuestas_a_crear.append(
                    RespuestaSolicitud(
                        solicitud=solicitud,
                        pregunta=pregunta,
                        respuesta_texto=respuesta_texto.strip()
                    )
                )
            
            # 3. Guardar todas las respuestas en la base de datos
            RespuestaSolicitud.objects.bulk_create(respuestas_a_crear)
            
            messages.success(request, f'Incidencia "{encuesta.titulo_encuesta}" creada correctamente.')
            # Redirigir al dashboard del territorial para ver su nueva incidencia
            return redirect('dashboard_territorial') 

        except ValueError as e:
            messages.error(request, str(e))
            # Si hay un error (ej. pregunta vacía), volver a la misma página
            return redirect('responder_encuesta', id_encuesta=id_encuesta)
        except Exception as e:
            messages.error(request, f'Error al guardar la incidencia: {str(e)}')
            return redirect('responder_encuesta', id_encuesta=id_encuesta)

    else:
        # Método GET: Mostrar el formulario con las preguntas
        preguntas = encuesta.pregunta_set.all()
        return render(request, 'encuesta/responder_encuesta.html', {
            'encuesta_data': encuesta,
            'preguntas': preguntas
        })