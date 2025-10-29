from django.shortcuts import render, redirect, get_object_or_404
from .models import Direccion
from django.contrib import messages
from .models import Direccion
from django.contrib.auth.decorators import login_required
from registration.models import Profile

#necesaria para ver los bloqear
@login_required
def main_direccion(request):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group.name == 'SECPLA':
            direcciones_listado = Direccion.objects.all().order_by('nombre_direccion')
            return render(request, 'direccion/main_direccion.html', {'direcciones_listado': direcciones_listado})
        else:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('main_admin') # O a la página de inicio que corresponda
    except Profile.DoesNotExist:
        messages.error(request, 'No tienes un perfil asignado. Contacta al administrador.')
        return redirect('logout')
    
@login_required
def direccion_actualiza(request, id_direccion):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group.name == 'SECPLA':
            direccion = get_object_or_404(Direccion, pk=id_direccion)
            if request.method == 'POST':
                nombre = request.POST.get('nombre_direccion')
                if not nombre:
                    messages.error(request, 'El nombre no puede estar vacío.')
                    return render(request, 'direccion/direccion_actualiza.html', {'direccion_data': direccion})
                
                direccion.nombre_direccion = nombre
                direccion.save()
                messages.success(request, 'Dirección actualizada correctamente.')
                return redirect('main_direccion')
            else:
                return render(request, 'direccion/direccion_actualiza.html', {'direccion_data': direccion})
        else:
            messages.error(request, 'No tienes permisos para esta acción.')
            return redirect('main_admin')
    except Profile.DoesNotExist:
        messages.error(request, 'No tienes un perfil asignado.')
        return redirect('logout')
    
@login_required
def direccion_bloquea_activa(request, id_direccion):
    try:
        profile = Profile.objects.get(user=request.user)
        if profile.group.name == 'SECPLA':
            direccion = get_object_or_404(Direccion, pk=id_direccion)
            if direccion.estado == 'Activo':
                direccion.estado = 'Bloqueado'
                messages.success(request, f'La dirección "{direccion.nombre_direccion}" ha sido bloqueada.')
            else:
                direccion.estado = 'Activo'
                messages.success(request, f'La dirección "{direccion.nombre_direccion}" ha sido activada.')
            direccion.save()
            return redirect('main_direccion')
        else:
            messages.error(request, 'No tienes permisos para esta acción.')
            return redirect('main_admin')
    except Profile.DoesNotExist:
        messages.error(request, 'No tienes un perfil asignado.')
        return redirect('logout')

@login_required
def main_direccion_bloqueadas(request):
    pass

@login_required
def direccion_desbloqueadas(request):
    pass