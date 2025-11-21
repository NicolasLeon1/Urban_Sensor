from register.decorators import *
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import TipoIncidencia, SolicitudIncidencia, RespuestaSolicitud
from encuesta.models import ArchivoSolicitud, Pregunta
from direccion.models import Direccion
from departamento.models import Departamento
from register.models import User, Perfiles


@secpla_required
def main_incidencia(request):
    incidencia_listado = TipoIncidencia.objects.select_related('id_direccion', 'id_departamento').order_by('id')
    return render(request, 'incidencia/main_incidencia.html', {'incidencia_listado': incidencia_listado})


@secpla_required
def nueva_incidencia(request):
    if request.method == 'POST':
        nombre_incidencia = (request.POST.get('nombre_incidencia') or '').strip()
        id_direccion = request.POST.get('id_direccion') or None
        id_departamento = request.POST.get('id_departamento') or None

        # ==== VALIDACIONES SOLO PARA INCIDENCIA ====
        motivos_rechazo = []

        if len(nombre_incidencia) < 8:
            motivos_rechazo.append('El nombre de la incidencia debe tener mínimo 8 caracteres.')

        if not id_direccion:
            motivos_rechazo.append('No se seleccionó Dirección.')

        if not id_departamento:
            motivos_rechazo.append('No se seleccionó Departamento.')

        # Si hay errores → INCIDENCIA RECHAZADA
        if motivos_rechazo:
            estado_final = 'rechazada'
            descripcion_rechazo = "\n".join(motivos_rechazo)
        else:
            estado_final = 'abierta'  # estado "activo"
            descripcion_rechazo = None
        # ============================================

        try:
            incidencia = TipoIncidencia.objects.create(
                nombre_incidencia=nombre_incidencia,
                id_direccion_id=id_direccion,
                id_departamento_id=id_departamento,
                activo=True
            )

            # Mensaje visual sobre el resultado
            if estado_final == 'rechazada':
                    motivo = descripcion_rechazo if descripcion_rechazo else "Incidencia no válida"
                    messages.error(request, f'Incidencia rechazada: {motivo}')
            else:
                messages.success(request, 'Tipo de incidencia creado correctamente.')


            return redirect('main_incidencia')

        except Exception as e:
            messages.error(request, f'Error al crear incidencia: {str(e)}')
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
    incidencia = get_object_or_404(TipoIncidencia, pk=id)

    # 🚫 Bloquear edición si está rechazada
    # Si el nombre tiene menos de 8 caracteres o no tiene dirección o departamento -> NO se puede editar
    if len(incidencia.nombre_incidencia) < 8 or not incidencia.id_direccion or not incidencia.id_departamento:
        messages.error(request, "Esta incidencia fue rechazada automáticamente y NO puede ser editada.")
        return redirect('main_incidencia')

    # -------------- sigue la lógica normal --------------
    if request.method == 'POST':
        nombre_incidencia = request.POST.get('nombre_incidencia')
        id_direccion = request.POST.get('id_direccion')
        id_departamento = request.POST.get('id_departamento')

        if not all([nombre_incidencia]):
            messages.error(request, 'Debe ingresar un nombre para la incidencia.')
            return redirect('editar_incidencia', id=id)

        try:
            # Solo se actualiza si no está rechazada
            incidencia.nombre_incidencia = nombre_incidencia
            incidencia.id_direccion_id = id_direccion or None
            incidencia.id_departamento_id = id_departamento or None
            incidencia.save()
            messages.success(request, 'Tipo de incidencia actualizado correctamente.')
            return redirect('main_incidencia')
        except Exception as e:
            messages.error(request, f'Error al actualizar tipo de incidencia: {str(e)}')
            return redirect('editar_incidencia', id=id)

    else:
        direcciones = Direccion.objects.filter(activo=True)
        departamentos = Departamento.objects.filter(activo=True)
        return render(request, 'incidencia/editar_incidencia.html', {
            'incidencia_data': incidencia,
            'direcciones': direcciones,
            'departamentos': departamentos
        })



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


@departamento_required
def derivar_incidencia(request, id_solicitud):
    if request.method != 'POST':
        return redirect('dashboard_departamento')

    try:
        solicitud = SolicitudIncidencia.objects.get(pk=id_solicitud)
    except:
        messages.error(request, 'No existe la solicitud')
        return redirect('dashboard_departamento')

    try:
        cuadrilla_id = request.POST.get('cuadrilla_id')
        if not cuadrilla_id:
            raise ValueError("Debe seleccionar una cuadrilla para derivar.")

        cuadrilla = User.objects.get(
            pk=cuadrilla_id,
            perfil__id=Perfiles.CUADRILLA.value,
            departamento=request.user.departamento
        )

        if solicitud.estado != 'abierta':
            messages.success(
                request,
                f'Cuadrilla transferida desde "{solicitud.cuadrilla_asignada}" a "{cuadrilla}"'
            )
        else:
            messages.success(request, f'Solicitud derivada correctamente a "{cuadrilla}".')

        solicitud.cuadrilla_asignada = cuadrilla
        solicitud.estado = 'derivada'
        solicitud.save()

        return redirect('to_dashboard')

    except User.DoesNotExist:
        messages.error(request, 'La cuadrilla seleccionada no es válida o no pertenece a su departamento.')
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f'Error al derivar la solicitud: {str(e)}')

    return redirect('to_dashboard')


@cuadrilla_required
def resolver_incidencia(request, id_solicitud):
    if request.method == 'GET':
        solicitud = get_object_or_404(SolicitudIncidencia, pk=id_solicitud)
        encuesta_data = solicitud.encuesta_base
        archivos_resolucion = ArchivoSolicitud.objects.filter(solicitud=solicitud, tipo='resolucion')
        archivos_evidencia = ArchivoSolicitud.objects.filter(solicitud=solicitud, tipo='evidencia')
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
        context = {
            'solicitud': solicitud,
            'encuesta_data': solicitud.encuesta_base,
            'preguntas_con_respuestas': preguntas_con_respuestas,
            'archivos_evidencia': archivos_evidencia,
            'archivos_resolucion_existentes': archivos_resolucion,
            'user': request.user,
        }
        return render(request, 'incidencia/resolver_incidencia.html', context)
    else:
        solicitud = get_object_or_404(SolicitudIncidencia, pk=id_solicitud)

        if solicitud.cuadrilla_asignada != request.user:
            messages.error(request, 'No puede resolver una solicitud que no le fue asignada.')
            return redirect('dashboard_cuadrilla')

        if solicitud.estado != 'derivada':
            messages.error(request, 'Esta solicitud no está pendiente de resolución.')
            return redirect('to_dashboard')

        try:
            descripcion = request.POST.get('descripcion_resolucion')

            if not descripcion or not descripcion.strip():
                messages.error(request, 'Debe ingresar una descripción de la resolución.')
                return redirect('to_dashboard')

            archivos_a_eliminar = request.POST.getlist('eliminar_archivos_resolucion')
            nuevos_archivos = request.FILES.getlist('archivos_resolucion')

            if archivos_a_eliminar:
                for archivo in archivos_a_eliminar:
                    try:
                        ArchivoSolicitud.objects.filter(id=archivo, solicitud=solicitud).delete()
                    except:
                        messages.error(request, 'Hubo un error al eliminar los archivos.')
                        return redirect('resolver_incidencia', id_solicitud)
            if nuevos_archivos:
                for archivo in nuevos_archivos:
                    ArchivoSolicitud.objects.create(
                        solicitud=solicitud,
                        archivo=archivo,
                        nombre_original=archivo.name,
                        tipo_contenido=archivo.content_type,
                        tamaño=archivo.size,
                        tipo='resolucion'
                    )
            else:
                messages.error(request, 'No adjunto ningun archivo de resolucion.')
                return redirect('resolver_incidencia', id_solicitud)

            solicitud.descripcion_resolucion = descripcion
            solicitud.estado = 'finalizada'
            solicitud.save()
            messages.success(request, 'Solicitud resuelta correctamente.')
            return redirect('to_dashboard')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al guardar la resolución: {str(e)}')

        return redirect('to_dashboard')


@departamento_required
def rechazar_incidencia(request, id_solicitud):
    if request.method == 'POST':
        solicitud = get_object_or_404(SolicitudIncidencia, pk=id_solicitud)

        motivo_rechazo = request.POST.get('motivo_rechazo', '').strip()

        if not motivo_rechazo:
            messages.error(request, 'Debe ingresar un motivo para rechazar la solicitud.')
            return redirect('dashboard_departamento')

        solicitud.estado = 'rechazada'
        solicitud.descripcion_rechazo = motivo_rechazo
        solicitud.save()

        messages.success(request, f'Solicitud #{id_solicitud} rechazada exitosamente.')
        return redirect('dashboard_departamento')

    return redirect('dashboard_departamento')


@territorial_required
def cancelar_incidencia(request, id_solicitud):
    solicitud = get_object_or_404(SolicitudIncidencia, pk=id_solicitud)
    solicitud.delete()
    return redirect('to_dashboard')


@check_perfil(Perfiles.TERRITORIAL, Perfiles.CUADRILLA)
def reabrir_incidencia(request, id_solicitud):
    solicitud = get_object_or_404(SolicitudIncidencia, pk=id_solicitud)
    if solicitud.estado in ('rechazada', 'finalizada'):
        descripcion_reabrir = request.POST.get('motivo_reapertura', '')
        if request.user.perfil.id != Perfiles.CUADRILLA.value:
            if descripcion_reabrir == '':
                messages.error(request, 'La descripcion para reabrir no puede estar vacia.')
                return redirect('to_dashboard')
            solicitud.descripcion_reabrir = descripcion_reabrir
            solicitud.estado = 'abierta'
        else:
            solicitud.estado = 'derivada'
        solicitud.save()
        messages.success(request, 'Solicitud reabierta correctamente.')
        return redirect('to_dashboard')
    else:
        messages.error(request, 'La solicitud no se encuentra en un estado para poder reabrirse.')
        return redirect('to_dashboard')


@departamento_required
def revertir_derivacion(request, id_solicitud):
    try:
        solicitud = SolicitudIncidencia.objects.get(pk=id_solicitud)
    except:
        messages.error(request, 'No existe la solicitud')
        return redirect('dashboard_departamento')

    solicitud.cuadrilla_asignada = None
    solicitud.estado = 'abierta'
    solicitud.save()

    messages.success(request, 'Se revirtio correctamente la derivacion de la solicitud.')
    return redirect('to_dashboard')

@secpla_required
def eliminar_incidencia(request, id):
    incidencia = get_object_or_404(TipoIncidencia, pk=id)
    
    # Solo permitir eliminar si está rechazada
    if len(incidencia.nombre_incidencia) < 8 or not incidencia.id_direccion or not incidencia.id_departamento:
        incidencia.delete()
        messages.success(request, "Tipo de incidencia eliminado correctamente.")
    else:
        messages.error(request, "Solo se pueden eliminar incidencias RECHAZADAS automáticamente.")
        
    return redirect('main_incidencia')

