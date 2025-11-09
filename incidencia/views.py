from register.decorators import *
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import TipoIncidencia, SolicitudIncidencia, RespuestaSolicitud # Importar nuevos modelos
from direccion.models import Direccion
from departamento.models import Departamento
from register.models import User, Perfiles
from django.core.exceptions import ValidationError

@login_required
def dashboard_main(request):
    perfil_id = getattr(request.user, "perfil_id", None)

    if perfil_id == Perfiles.TERRITORIAL.value:
        return redirect('dashboard_territorial')
    elif perfil_id == Perfiles.DEPARTAMENTO.value:
        return redirect('dashboard_departamento')
    elif perfil_id == Perfiles.CUADRILLA.value:
        return redirect('dashboard_cuadrilla')
    # Si tienes otros perfiles tipo SECPLA / DIRECCION / ADMIN, puedes rutearlos acá:
    # elif perfil_id == Perfiles.SECPLA.value:
    #     return redirect('dashboard_admin')

    # Fallback por si algo no cuadra
    return redirect('dashboard_admin')



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

# --- NUEVAS VISTAS PARA GESTIÓN DE SOLICITUDES (Tickets) ---

@login_required # Usar login_required general
def detalle_solicitud(request, id_solicitud):
    """
    Vista genérica para ver el detalle de una solicitud (ticket).
    Muestra la solicitud, la encuesta base, y las respuestas dadas.
    La plantilla HTML debe mostrar/ocultar los botones de "Derivar" o "Resolver"
    según el perfil del usuario (ej. request.user.perfil.id).
    """
    solicitud = get_object_or_404(
        SolicitudIncidencia.objects.select_related(
            'encuesta_base', 
            'creado_por', 
            'direccion_asignada',
            'departamento_asignado',
            'cuadrilla_asignada'
        ), 
        pk=id_solicitud
    )
    
    # --- Validación de Permisos (Simplificada) ---
    user = request.user
    puede_ver = False
    
    if user.perfil.id == Perfiles.SECPLA.value:
        puede_ver = True
    elif user.perfil.id == Perfiles.DIRECCION.value and user.direccion == solicitud.direccion_asignada:
        puede_ver = True
    elif user.perfil.id == Perfiles.DEPARTAMENTO.value and user.departamento == solicitud.departamento_asignado:
        puede_ver = True
    elif user.perfil.id == Perfiles.TERRITORIAL.value and user == solicitud.creado_por:
        puede_ver = True
    elif user.perfil.id == Perfiles.CUADRILLA.value and user == solicitud.cuadrilla_asignada:
        puede_ver = True

    if not puede_ver:
        messages.error(request, 'No tiene permisos para ver esta solicitud.')
        # Redirigir al dashboard general (dashboard/urls.py usa 'to_dashboard')
        return redirect('to_dashboard') 

    # Obtener las respuestas (R: Pregunta -> Respuesta)
    respuestas = RespuestaSolicitud.objects.filter(solicitud=solicitud).select_related('pregunta')
    
    # Contexto para derivación (si es Depto)
    cuadrillas_depto = []
    if user.perfil.id == Perfiles.DEPARTAMENTO.value and solicitud.estado == 'abierta':
         cuadrillas_depto = User.objects.filter(
            activo=True, 
            perfil__id=Perfiles.CUADRILLA.value,
            departamento=user.departamento # Asume que cuadrilla pertenece a depto
        )

    return render(request, 'incidencia/detalle_solicitud.html', {
        'solicitud': solicitud,
        'respuestas_listado': respuestas,
        'cuadrillas_disponibles': cuadrillas_depto,
    })

@login_required
@territorial_required
def detalle_solicitud_territorial(request, pk):
    solicitud = get_object_or_404(
        SolicitudIncidencia,
        pk=pk,
        creado_por=request.user
    )

    respuestas = RespuestaSolicitud.objects.filter(
        solicitud=solicitud
    ).select_related('pregunta')

    context = {
        'solicitud': solicitud,
        'respuestas': respuestas,
    }
    return render(request, 'incidencia/detalle_solicitud_territorial.html', context)

def derivar_solicitud_territorial(request, pk):
    solicitud = get_object_or_404(
        SolicitudIncidencia,
        pk=pk,
        creado_por=request.user
    )

    if solicitud.estado != SolicitudIncidencia.ESTADO_ABIERTA:
        messages.error(request, "Solo puedes derivar incidencias en estado 'Abierta'.")
        return redirect('dashboard_territorial')

    try:
        direccion_destino, depto_destino = solicitud.get_departamento_destino()
    except ValidationError as e:
        messages.error(request, f"No es posible derivar esta incidencia: {e.messages[0]}")
        return redirect('dashboard_territorial')

    if not depto_destino:
        messages.error(
            request,
            "No hay un Departamento configurado para esta incidencia. Contacta a SECPLA."
        )
        return redirect('dashboard_territorial')

    # 🔹 Solo asignamos destino; mantenemos estado='abierta'
    solicitud.direccion_asignada = direccion_destino
    solicitud.departamento_asignado = depto_destino
    # NO cambiamos solicitud.estado aquí
    solicitud.save()



    # Seteamos destino según la lógica centralizada
    solicitud.direccion_asignada = direccion_destino
    solicitud.departamento_asignado = depto_destino
    solicitud.estado = SolicitudIncidencia.ESTADO_DERIVADA
    solicitud.save()

    messages.success(
        request,
        f"La incidencia #{solicitud.id} fue derivada al departamento '{depto_destino.nombre_departamento}'."
    )
    return redirect('dashboard_territorial')

@login_required
@cuadrilla_required
def detalle_solicitud_cuadrilla(request, pk):
    """
    Detalle de incidencia para usuarios de cuadrilla.
    Solo puede ver incidencias asignadas a esa cuadrilla.
    """
    solicitud = get_object_or_404(
        SolicitudIncidencia,
        pk=pk,
        cuadrilla_asignada=request.user
    )

    # 👇 Igual que en la vista de territorial
    respuestas = RespuestaSolicitud.objects.filter(
        solicitud=solicitud
    ).select_related('pregunta')

    context = {
        'solicitud': solicitud,
        'respuestas': respuestas,
        'desde': 'cuadrilla',
    }
    return render(request, 'incidencia/detalle_solicitud_territorial.html', context)

@departamento_required
def derivar_solicitud(request, id_solicitud):
    """
    Vista (solo POST) que usa el Departamento para asignar 
    una solicitud 'abierta' a una Cuadrilla.
    (Requerimiento: Departamento ... Puede derivar una incidencia a una cuadrilla)
    """
    if request.method != 'POST':
        return redirect('dashboard_departamento')
    
    solicitud = get_object_or_404(SolicitudIncidencia, pk=id_solicitud)
    
    # Validar que el depto es el dueño
    if solicitud.departamento_asignado != request.user.departamento:
        messages.error(request, 'No puede derivar una solicitud que no pertenece a su departamento.')
        return redirect('dashboard_departamento')
    
    # Validar que esté 'abierta'
    if solicitud.estado != 'abierta':
        messages.error(request, 'Esta solicitud ya ha sido gestionada (derivada, rechazada o finalizada).')
        return redirect('detalle_solicitud', id_solicitud=id_solicitud)

    try:
        cuadrilla_id = request.POST.get('id_cuadrilla')
        if not cuadrilla_id:
            raise ValueError("Debe seleccionar una cuadrilla para derivar.")
            
        # Validar que la cuadrilla exista, sea de este depto y tenga el perfil correcto
        cuadrilla = User.objects.get(
            pk=cuadrilla_id, 
            perfil__id=Perfiles.CUADRILLA.value, 
            departamento=request.user.departamento
        )
        
        solicitud.cuadrilla_asignada = cuadrilla
        solicitud.estado = 'derivada'
        solicitud.save()
        
        messages.success(request, f'Solicitud derivada correctamente a {cuadrilla.nombre} {cuadrilla.apellido}.')
        return redirect('detalle_solicitud', id_solicitud=id_solicitud)

    except User.DoesNotExist:
        messages.error(request, 'La cuadrilla seleccionada no es válida o no pertenece a su departamento.')
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f'Error al derivar la solicitud: {str(e)}')
    
    return redirect('detalle_solicitud', id_solicitud=id_solicitud)


@cuadrilla_required
def resolver_solicitud(request, id_solicitud):
    """
    Vista (solo POST) que usa la Cuadrilla para marcar 
    una solicitud 'derivada' como 'finalizada'.
    (Requerimiento: Cuadrilla ... subir imágenes o descripciones)
    """
    if request.method != 'POST':
        return redirect('dashboard_cuadrilla')

    solicitud = get_object_or_404(SolicitudIncidencia, pk=id_solicitud)
    
    # Validar que la cuadrilla es la asignada
    if solicitud.cuadrilla_asignada != request.user:
        messages.error(request, 'No puede resolver una solicitud que no le fue asignada.')
        return redirect('dashboard_cuadrilla')
    
    # Validar que esté 'derivada' (pendiente de resolución)
    if solicitud.estado != 'derivada':
        messages.error(request, 'Esta solicitud no está pendiente de resolución.')
        return redirect('detalle_solicitud', id_solicitud=id_solicitud)
    
    try:
        descripcion = request.POST.get('descripcion_resolucion')
        # imagen = request.FILES.get('imagen_resolucion') # (Lógica de imagen no implementada)

        if not descripcion or not descripcion.strip():
            raise ValueError("Debe ingresar una descripción de la resolución.")

        solicitud.descripcion_resolucion = descripcion
        solicitud.estado = 'finalizada'
        # solicitud.imagen_resolucion = imagen # (Si se implementa imagen)
        solicitud.save()
        
        messages.success(request, 'Solicitud marcada como finalizada correctamente.')
        # Devolver al dashboard de cuadrilla (la tarea ya no aparecerá en pendientes)
        return redirect('dashboard_cuadrilla')

    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f'Error al guardar la resolución: {str(e)}')
    
    return redirect('detalle_solicitud', id_solicitud=id_solicitud)