from register.decorators import *
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Encuesta, Pregunta, ArchivoSolicitud
from departamento.models import Departamento
from incidencia.models import TipoIncidencia, SolicitudIncidencia, RespuestaSolicitud
from django.db import transaction

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

@territorial_required
def listar_encuestas_responder(request):
    encuestas_activas = Encuesta.objects.filter(activo=True).select_related(
        'id_tipo_incidencia', 
        'id_departamento'
    ).order_by('titulo_encuesta')
    
    return render(request, 'encuesta/listar_encuestas_responder.html', {
        'encuestas_listado': encuestas_activas
    })

@territorial_required
@transaction.atomic
def responder_encuesta(request, id_encuesta):
    try:
        encuesta = Encuesta.objects.prefetch_related('pregunta_set').get(pk=id_encuesta, activo=True)
    except Encuesta.DoesNotExist:
        messages.error(request, 'La encuesta seleccionada no existe o no está activa.')
        return redirect('listar_encuestas_responder')

    if request.method == 'POST':
        try:
            tipo_incidencia = encuesta.id_tipo_incidencia
            ubicacion = request.POST.get('ubicacion')
            
            solicitud = SolicitudIncidencia.objects.create(
                encuesta_base=encuesta,
                creado_por=request.user,
                estado='abierta',
                ubicacion=ubicacion,
                direccion_asignada=tipo_incidencia.id_direccion,
                departamento_asignado=tipo_incidencia.id_departamento
            )
            
            preguntas = encuesta.pregunta_set.all()
            respuestas_a_crear = []
            
            for pregunta in preguntas:
                respuesta_texto = request.POST.get(f'pregunta_{pregunta.id}')
                
                if not respuesta_texto or not respuesta_texto.strip():
                    raise ValueError(f"La pregunta '{pregunta.texto_pregunta}' es obligatoria.")
                
                respuestas_a_crear.append(
                    RespuestaSolicitud(
                        solicitud=solicitud,
                        pregunta=pregunta,
                        respuesta_texto=respuesta_texto.strip()
                    )
                )
            
            RespuestaSolicitud.objects.bulk_create(respuestas_a_crear)
            
            archivos = request.FILES.getlist('archivos')
            if archivos:
                archivos_guardados = []
                
                for archivo in archivos:
                    if archivo.size > 20 * 1024 * 1024:
                        messages.warning(request, f'El archivo {archivo.name} es demasiado grande (máximo 20MB)')
                        continue
                    
                    if not archivo.content_type.startswith(('image/', 'video/')):
                        messages.warning(request, f'Solo se permiten imágenes y videos: {archivo.name}')
                        continue
                    
                    extensiones_permitidas = [
                        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
                        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.mkv'
                    ]
                    nombre_archivo = archivo.name.lower()
                    if not any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                        messages.warning(request, f'Formato no permitido: {archivo.name}')
                        continue
                    
                    archivo_adjunto = ArchivoSolicitud(
                        solicitud=solicitud,
                        archivo=archivo,
                        nombre_original=archivo.name,
                        tipo_contenido=archivo.content_type,
                        tamaño=archivo.size
                    )
                    archivo_adjunto.save()
                    archivos_guardados.append(archivo_adjunto)
                
                if archivos_guardados:
                    messages.success(request, f'Se adjuntaron {len(archivos_guardados)} archivo(s) a la incidencia.')
            
            messages.success(request, f'Incidencia "{encuesta.titulo_encuesta}" creada correctamente.')
            return redirect('dashboard_territorial')

        except ValueError as e:
            messages.error(request, str(e))
            return redirect('responder_encuesta', id_encuesta=id_encuesta)
        except Exception as e:
            messages.error(request, f'Error al guardar la incidencia: {str(e)}')
            return redirect('responder_encuesta', id_encuesta=id_encuesta)

    else:
        preguntas = encuesta.pregunta_set.all()
        return render(request, 'encuesta/responder_encuesta.html', {
            'encuesta_data': encuesta,
            'preguntas': preguntas
        })

@check_perfil(Perfiles.TERRITORIAL, Perfiles.DEPARTAMENTO, Perfiles.CUADRILLA)
def ver_encuesta_respondida(request, id):
    try:
        solicitud = SolicitudIncidencia.objects.get(id=id)
    except:
        messages.error(request, 'La solicitud no existe.')
        return redirect('ver_encuesta_respondida')
    
    encuesta_data = solicitud.encuesta_base
    
    preguntas = Pregunta.objects.filter(id_encuesta=encuesta_data.id)
    
    preguntas_con_respuestas = []
    for pregunta in preguntas:
        try:
            respuesta = RespuestaSolicitud.objects.get(
                solicitud=solicitud, 
                pregunta=pregunta
            )
            preguntas_con_respuestas.append({
                'pregunta': pregunta,
                'respuesta': respuesta
            })
        except RespuestaSolicitud.DoesNotExist:
            preguntas_con_respuestas.append({
                'pregunta': pregunta,
                'respuesta': None
            })
    
    archivos_adjuntos = ArchivoSolicitud.objects.filter(solicitud=solicitud, tipo='evidencia')
    archivos_resolucion = ArchivoSolicitud.objects.filter(solicitud=solicitud, tipo='resolucion')
    
    context = {
        'encuesta_data': encuesta_data,
        'preguntas_con_respuestas': preguntas_con_respuestas,
        'archivos_adjuntos': archivos_adjuntos,
        'archivos_resolucion': archivos_resolucion,
        'solicitud': solicitud,
    }
    
    return render(request, 'encuesta/ver_encuesta_respondida.html', context)

@territorial_required
def editar_encuesta_respondida(request, id):
    try:
        solicitud = SolicitudIncidencia.objects.get(id=id)
    except SolicitudIncidencia.DoesNotExist:
        messages.error(request, 'La solicitud no existe.')
        return redirect('listar_encuestas_responder')
    
    if solicitud.creado_por != request.user:
        messages.error(request, 'No tiene permisos para editar esta incidencia.')
        return redirect('ver_encuesta_respondida', id=id)
    
    if solicitud.estado not in ['abierta', 'rechazada']:
        messages.error(request, 'No se puede editar una incidencia que ya ha sido cerrada.')
        return redirect('ver_encuesta_respondida', id=id)
    
    encuesta_data = solicitud.encuesta_base
    
    if request.method == 'POST':
        try:
            ubicacion = request.POST.get('ubicacion')
            if not ubicacion or not ubicacion.strip():
                raise ValueError("La ubicación es obligatoria.")
            
            solicitud.ubicacion = ubicacion.strip()
            
            preguntas = encuesta_data.pregunta_set.all()
            for pregunta in preguntas:
                respuesta_texto = request.POST.get(f'pregunta_{pregunta.id}')
                
                if not respuesta_texto or not respuesta_texto.strip():
                    raise ValueError(f"La pregunta '{pregunta.texto_pregunta}' es obligatoria.")
                
                # Buscar la respuesta existente o crear una nueva
                respuesta, created = RespuestaSolicitud.objects.get_or_create(
                    solicitud=solicitud,
                    pregunta=pregunta,
                    defaults={'respuesta_texto': respuesta_texto.strip()}
                )
                
                if not created:
                    respuesta.respuesta_texto = respuesta_texto.strip()
                    respuesta.save()
            
            archivos_a_eliminar = request.POST.getlist('eliminar_archivos')
            if archivos_a_eliminar:
                archivos_eliminados = ArchivoSolicitud.objects.filter(
                    id__in=archivos_a_eliminar,
                    solicitud=solicitud
                )
                count_eliminados = archivos_eliminados.count()
                archivos_eliminados.delete()
                if count_eliminados > 0:
                    messages.success(request, f'Se eliminaron {count_eliminados} archivo(s).')
            
            nuevos_archivos = request.FILES.getlist('archivos')
            if nuevos_archivos:
                archivos_guardados = []
                
                for archivo in nuevos_archivos:
                    if archivo.size > 20 * 1024 * 1024:
                        messages.warning(request, f'El archivo {archivo.name} es demasiado grande (máximo 20MB)')
                        continue
                    
                    if not archivo.content_type.startswith(('image/', 'video/')):
                        messages.warning(request, f'Solo se permiten imágenes y videos: {archivo.name}')
                        continue
                    
                    extensiones_permitidas = [
                        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
                        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.mpg', '.mkv'
                    ]
                    nombre_archivo = archivo.name.lower()
                    if not any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                        messages.warning(request, f'Formato no permitido: {archivo.name}')
                        continue
                    
                    archivo_adjunto = ArchivoSolicitud(
                        solicitud=solicitud,
                        archivo=archivo,
                        nombre_original=archivo.name,
                        tipo_contenido=archivo.content_type,
                        tamaño=archivo.size
                    )
                    archivo_adjunto.save()
                    archivos_guardados.append(archivo_adjunto)
                
                if archivos_guardados:
                    messages.success(request, f'Se agregaron {len(archivos_guardados)} nuevo(s) archivo(s).')
            
            
            if solicitud.estado == 'rechazada':
                solicitud.estado = 'abierta'
            solicitud.save()

            messages.success(request, f'Incidencia "{encuesta_data.titulo_encuesta}" actualizada correctamente.')
            return redirect('ver_encuesta_respondida', id=id)

        except ValueError as e:
            messages.error(request, str(e))
            return cargar_datos_edicion(request, solicitud, encuesta_data)
        except Exception as e:
            messages.error(request, f'Error al actualizar la incidencia: {str(e)}')
            return cargar_datos_edicion(request, solicitud, encuesta_data)

    else:
        return cargar_datos_edicion(request, solicitud, encuesta_data)


def cargar_datos_edicion(request, solicitud, encuesta_data):
    """
    Función auxiliar para cargar los datos existentes para edición
    """
    preguntas = Pregunta.objects.filter(id_encuesta=encuesta_data.id)
    
    preguntas_con_respuestas = []
    for pregunta in preguntas:
        try:
            respuesta = RespuestaSolicitud.objects.get(
                solicitud=solicitud, 
                pregunta=pregunta
            )
            preguntas_con_respuestas.append({
                'pregunta': pregunta,
                'respuesta': respuesta
            })
        except RespuestaSolicitud.DoesNotExist:
            preguntas_con_respuestas.append({
                'pregunta': pregunta,
                'respuesta': None
            })
    
    archivos_adjuntos = ArchivoSolicitud.objects.filter(solicitud=solicitud)
    
    context = {
        'encuesta_data': encuesta_data,
        'preguntas_con_respuestas': preguntas_con_respuestas,
        'archivos_adjuntos': archivos_adjuntos,
        'solicitud': solicitud,
    }
    
    return render(request, 'encuesta/editar_encuesta_respondida.html', context)