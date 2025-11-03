from django.shortcuts import render, redirect
from register.decorators import *
from register.utils import *

# Create your views here.

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
    return render(request, 'dashboard/dashboard_admin.html')

@departamento_required
def dashboard_departamento(request):
    return render(request, 'dashboard/dashboard_departamento.html')

@direccion_required
def dashboard_direccion(request):
    return render(request, 'dashboard/dashboard_direccion.html')

@territorial_required
def dashboard_territorial(request):
    return render(request, 'dashboard/dashboard_territorial.html')

@cuadrilla_required
def dashboard_cuadrilla(request):
    return render(request, 'dashboard/dashboard_cuadrilla.html')