from django.shortcuts import render, redirect, get_object_or_404
from register.decorators import *
from register.utils import *
from register.decorators import (
    login_required,
    territorial_required,
    departamento_required,
    cuadrilla_required,
)
from django.utils import timezone
# --- IMPORTS AÑADIDOS ---
from incidencia.models import SolicitudIncidencia # Importar el nuevo modelo de solicitud
from register.models import User, Perfiles
from django.db.models import Count

@login_required
def dashboard_main(request):
    """
    Redirige al dashboard correcto según el perfil del usuario.
    """
    perfil_id = getattr(request.user, "perfil_id", None)

    if perfil_id == Perfiles.TERRITORIAL.value:
        return redirect('dashboard_territorial')

    if perfil_id == Perfiles.DEPARTAMENTO.value:
        return redirect('dashboard_departamento')

    if perfil_id == Perfiles.CUADRILLA.value:
        return redirect('dashboard_cuadrilla')

    # Si tienes otros perfiles con dashboard propio, agrégalos aquí.
    # if perfil_id == Perfiles.SECPLA.value:
    #     return redirect('dashboard_admin')

    # Fallback: si no sabemos qué es, mándalo al admin o logout
    return redirect('dashboard_admin')


@login_required
def to_dashboard(request):
    """
    Compatibilidad con código antiguo: apunta a dashboard_main.
    (login_view usa 'to_dashboard')
    """
    return dashboard_main(request)

@secpla_required
def dashboard_admin(request):
    # Requerimiento: Cantidad de usuarios disponibles
    num_usuarios = User.objects.filter(activo=True).count()
    
    # Requerimiento: Cantidad de incidencias (Solicitudes) por estado
    solicitudes_counts = SolicitudIncidencia.objects.values('estado').annotate(total=Count('estado'))
    stats = {s['estado']: s['total'] for s in solicitudes_counts}

    context = {
        'total_usuarios': num_usuarios,
        'total_solicitudes': SolicitudIncidencia.objects.count(),
        'total_abiertas': stats.get('abierta', 0),
        'total_derivadas': stats.get('derivada', 0),
        'total_rechazadas': stats.get('rechazada', 0),
        'total_finalizadas': stats.get('finalizada', 0),
    }
    return render(request, 'dashboard/dashboard_admin.html', context)


@login_required
@departamento_required
def dashboard_departamento(request):
    departamento = request.user.departamento

    # 🔹 Incidencias abiertas asignadas al departamento, aún sin cuadrilla
    pendientes = SolicitudIncidencia.objects.filter(
        departamento_asignado=departamento,
        cuadrilla_asignada__isnull=True,
        estado=SolicitudIncidencia.ESTADO_ABIERTA,
    ).order_by('-creado')

    # 🔹 Incidencias ya derivadas a cuadrilla (asignadas)
    derivadas = SolicitudIncidencia.objects.filter(
        departamento_asignado=departamento,
        cuadrilla_asignada__isnull=False,
        estado=SolicitudIncidencia.ESTADO_DERIVADA,
    ).order_by('-creado')

    # 🔹 Cuadrillas (usuarios con perfil CUADRILLA)
    cuadrillas = User.objects.filter(perfil_id=Perfiles.CUADRILLA.value)

    stats = {
        'abiertas': pendientes.count(),
        'derivadas': derivadas.count(),
        'finalizadas': SolicitudIncidencia.objects.filter(
            departamento_asignado=departamento,
            estado=SolicitudIncidencia.ESTADO_FINALIZADA,
        ).count(),
    }

    context = {
        'stats': stats,
        'listado_pendientes': pendientes,   # para tabla "Incidencias Pendientes del Departamento"
        'listado_derivadas': derivadas,     # para tabla "Derivadas (Asignadas)" si la tienes abajo
        'cuadrillas': cuadrillas,           # para el <select>
    }
    return render(request, 'dashboard/dashboard_departamento.html', context)

@login_required
@departamento_required
def derivar_a_cuadrilla(request, pk):
    if request.method != 'POST':
        return redirect('dashboard_departamento')

    departamento = request.user.departamento

    # Solo incidencias de este departamento, aún abiertas y sin cuadrilla
    solicitud = get_object_or_404(
        SolicitudIncidencia,
        pk=pk,
        departamento_asignado=departamento,
        cuadrilla_asignada__isnull=True,
        estado=SolicitudIncidencia.ESTADO_ABIERTA,
    )

    cuadrilla_id = request.POST.get('cuadrilla')
    if not cuadrilla_id:
        messages.error(request, "Debes seleccionar una cuadrilla antes de derivar.")
        return redirect('dashboard_departamento')

    cuadrilla = get_object_or_404(User, id=cuadrilla_id, perfil_id=Perfiles.CUADRILLA.value)

    # 🔹 Aquí se hace la magia
    solicitud.cuadrilla_asignada = cuadrilla
    solicitud.estado = SolicitudIncidencia.ESTADO_DERIVADA
    solicitud.save()

    nombre_cuadrilla = getattr(cuadrilla, 'nombre', cuadrilla.username)
    messages.success(
        request,
        f"La incidencia #{solicitud.id} fue asignada a la cuadrilla {nombre_cuadrilla}."
    )
    return redirect('dashboard_departamento')

@direccion_required
def dashboard_direccion(request):
    # Requerimiento: Ver las incidencias asignadas a su dirección y su estado
    # Asume que el usuario de Dirección tiene un campo 'direccion'
    solicitudes_dir = SolicitudIncidencia.objects.filter(
        direccion_asignada=request.user.direccion
    ).order_by('estado', '-actualizado')
    
    solicitudes_pendientes = solicitudes_dir.filter(estado='abierta')
    solicitudes_derivadas = solicitudes_dir.filter(estado='derivada')
    solicitudes_finalizadas = solicitudes_dir.filter(estado='finalizada')

    context = {
        'solicitudes_listado': solicitudes_dir,
        'conteo_abiertas': solicitudes_pendientes.count(),
        'conteo_derivadas': solicitudes_derivadas.count(),
        'conteo_finalizadas': solicitudes_finalizadas.count()
    }
    return render(request, 'dashboard/dashboard_direccion.html', context)

@territorial_required
def dashboard_territorial(request):
    # Requerimiento: Ver sus incidencias creadas por estado + stats
    solicitudes_creadas = SolicitudIncidencia.objects.filter(
        creado_por=request.user).order_by('-creado')
    
    
    # Estadísticas numéricas
    stats = solicitudes_creadas.values('estado').annotate(total=Count('estado'))
    stats_dict = {
        'abierta': 0, 'derivada': 0, 'rechazada': 0, 'finalizada': 0
    }
    for s in stats:
        stats_dict[s['estado']] = s['total']

    # Listados por estado
    context = {
        'stats': stats_dict,
        'total_creadas': solicitudes_creadas.count(),
        'listado_abiertas': solicitudes_creadas.filter(estado='abierta'),
        'listado_derivadas': solicitudes_creadas.filter(estado='derivada'),
        'listado_rechazadas': solicitudes_creadas.filter(estado='rechazada'),
        'listado_finalizadas': solicitudes_creadas.filter(estado='finalizada'),
    }
    return render(request, 'dashboard/dashboard_territorial.html', context)
    
@cuadrilla_required
def dashboard_cuadrilla(request):
    # Incidencias asignadas a esta cuadrilla y aún pendientes
    asignadas_pendientes = SolicitudIncidencia.objects.filter(
        cuadrilla_asignada=request.user,
        estado=SolicitudIncidencia.ESTADO_DERIVADA,
    ).order_by('-creado')

    # Finalizadas hoy (si quieres el contador)
    finalizadas_hoy = SolicitudIncidencia.objects.filter(
        cuadrilla_asignada=request.user,
        estado=SolicitudIncidencia.ESTADO_FINALIZADA,
        actualizado__date=timezone.now().date(),
    ).count()

    context = {
        'asignadas_pendientes': asignadas_pendientes,
        'stats': {
            'pendientes': asignadas_pendientes.count(),
            'finalizadas_hoy': finalizadas_hoy,
        }
    }
    return render(request, 'dashboard/dashboard_cuadrilla.html', context)