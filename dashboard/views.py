from django.shortcuts import render, redirect
from register.decorators import *
from register.utils import *
from incidencia.models import SolicitudIncidencia
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
    num_usuarios = User.objects.filter(activo=True).count()
    
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
    solicitudes_depto = SolicitudIncidencia.objects.filter(
        departamento_asignado=request.user.departamento
    ).order_by('-actualizado')
    
    solicitudes_pendientes = solicitudes_depto.filter(estado='abierta')
    solicitudes_derivadas = solicitudes_depto.filter(estado='derivada')
    solicitudes_rechazadas = solicitudes_depto.filter(estado='rechazada')
    solicitudes_finalizadas = solicitudes_depto.filter(estado='finalizada')

    cuadrillas = User.objects.filter(
        perfil=Perfiles.CUADRILLA.value,
        departamento=request.user.departamento
    )
    
    context = {
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_derivadas': solicitudes_derivadas,
        'solicitudes_rechazadas': solicitudes_rechazadas,
        'solicitudes_finalizadas': solicitudes_finalizadas,
        'conteo_abiertas': solicitudes_pendientes.count(),
        'conteo_derivadas': solicitudes_derivadas.count(),
        'conteo_rechazadas': solicitudes_rechazadas.count(),
        'conteo_finalizadas': solicitudes_finalizadas.count(),
        'cuadrillas_departamento': cuadrillas
    }
    return render(request, 'dashboard/dashboard_departamento.html', context)

@direccion_required
def dashboard_direccion(request):
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
    solicitudes_creadas = SolicitudIncidencia.objects.filter(
        creado_por=request.user
    )
    
    stats = solicitudes_creadas.values('estado').annotate(total=Count('estado'))
    stats_dict = {
        'abierta': 0, 'derivada': 0, 'rechazada': 0, 'finalizada': 0
    }
    for s in stats:
        stats_dict[s['estado']] = s['total']

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
    incidencias_asignadas = SolicitudIncidencia.objects.filter(
        cuadrilla_asignada=request.user
    ).order_by('actualizado')

    incidencias_derivadas = incidencias_asignadas.filter(estado='derivada')
    incidencias_finalizadas = incidencias_asignadas.filter(estado='finalizada')
    
    context = {
        'incidencias_asignadas': incidencias_derivadas,
        'incidencias_finalizadas': incidencias_finalizadas,
        'conteo_asignadas': incidencias_derivadas.count(),
        'conteo_finalizadas': incidencias_finalizadas.count(),
    }
    return render(request, 'dashboard/dashboard_cuadrilla.html', context)