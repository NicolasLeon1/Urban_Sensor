from django.shortcuts import render, redirect
from register.decorators import *
from register.utils import *

# --- IMPORTS AÑADIDOS ---
from incidencia.models import SolicitudIncidencia # Importar el nuevo modelo de solicitud
from register.models import User, Perfiles
from django.db.models import Count

@login_required
def to_dashboard(request):
    if tiene_perfil(request, Perfiles.SECPLA):
        return redirect('dashboard_admin')
    elif tiene_perfil(request, Perfiles.DEPARTAMENTO):
        return redirect('dashboard_departamento')
    elif tiene_perfil(request, Perfiles.DIRECCION):
        return redirect('dashboard_direccion')
    elif tiene_perfil(request, Perfiles.TERRITORIAL):
        return redirect('dashboard_territorial')
    elif tiene_perfil(request, Perfiles.CUADRILLA):
        return redirect('dashboard_cuadrilla')
    return redirect('login')

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

@departamento_required
def dashboard_departamento(request):
    # Requerimiento: Ver incidencias asignadas a su departamento y su estado
    # Asume que el usuario de Depto tiene un campo 'departamento'
    solicitudes_depto = SolicitudIncidencia.objects.filter(
        departamento_asignado=request.user.departamento
    ).order_by('-actualizado')
    
    # Requerimiento: Puede derivar una incidencia a una cuadrilla
    # Filtramos las que están 'abiertas' para que el depto las derive
    solicitudes_pendientes = solicitudes_depto.filter(estado='abierta')
    solicitudes_derivadas = solicitudes_depto.filter(estado='derivada')
    solicitudes_finalizadas = solicitudes_depto.filter(estado='finalizada')

    cuadrillas = User.objects.filter(perfil=Perfiles.CUADRILLA.value)
    
    context = {
        'solicitudes_listado': solicitudes_depto,
        'solicitudes_pendientes': solicitudes_pendientes,
        'conteo_abiertas': solicitudes_pendientes.count(),
        'conteo_derivadas': solicitudes_derivadas.count(),
        'conteo_finalizadas': solicitudes_finalizadas.count(),
        'cuadrillas_departamento': cuadrillas
    }
    return render(request, 'dashboard/dashboard_departamento.html', context)

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
        creado_por=request.user
    )
    
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
    # Requerimiento: Ver incidencias (solicitudes) asignadas
    # Solo mostrar las que están 'derivadas' (pendientes de resolver)
    solicitudes_asignadas = SolicitudIncidencia.objects.filter(
        cuadrilla_asignada=request.user,
        estado='derivada' 
    ).order_by('actualizado')
    
    context = {
        'tareas_pendientes': solicitudes_asignadas
    }
    return render(request, 'dashboard/dashboard_cuadrilla.html', context)