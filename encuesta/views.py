from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from registration.models import Profile
from .models import Encuesta, Pregunta, Departamento, TipoIncidencia

# Vista principal - Listar encuestas
@login_required
def main_encuesta(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:  # Solo Admin
        encuesta_listado = Encuesta.objects.order_by('-creado')
        return render(request, 'encuesta/main_encuesta.html', {'encuesta_listado': encuesta_listado})
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

# Vista para mostrar formulario de crear encuesta
@login_required
def encuesta_crear(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        departamentos = Departamento.objects.filter(activo=True)
        tipo_incidencias = TipoIncidencia.objects.filter(activo=True)
        
        return render(request, 'encuesta/encuesta_crear.html', {
            'departamentos': departamentos,
            'tipo_incidencias': tipo_incidencias,
            'prioridades': Encuesta.PRIORIDADES
        })
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

# Vista para guardar encuesta
@login_required
def encuesta_guardar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        if request.method == 'POST':
            try:
                # Datos básicos de la encuesta
                titulo_encuesta = request.POST.get('titulo_encuesta')
                descripcion_incidente = request.POST.get('descripcion_incidente')
                prioridad = request.POST.get('prioridad')
                id_departamento = request.POST.get('id_departamento')
                id_tipo_incidencia = request.POST.get('id_tipo_incidencia')
                
                # Validaciones básicas
                if not all([titulo_encuesta, descripcion_incidente, id_departamento, id_tipo_incidencia]):
                    messages.error(request, 'Debe completar todos los campos obligatorios')
                    return redirect('encuesta_crear')
                
                # Crear encuesta
                encuesta = Encuesta(
                    titulo_encuesta=titulo_encuesta,
                    descripcion_incidente=descripcion_incidente,
                    prioridad=prioridad,
                    id_departamento_id=id_departamento,
                    id_tipo_incidencia_id=id_tipo_incidencia
                )
                encuesta.save()
                
                # Procesar preguntas adicionales
                preguntas = request.POST.getlist('preguntas[]')
                for texto_pregunta in preguntas:
                    if texto_pregunta.strip():  # Solo agregar si no está vacío
                        Pregunta.objects.create(
                            id_encuesta=encuesta,
                            texto_pregunta=texto_pregunta.strip()
                        )
                
                messages.success(request, 'Encuesta creada correctamente')
                return redirect('main_encuesta')
                
            except Exception as e:
                messages.error(request, f'Error al crear encuesta: {str(e)}')
                return redirect('encuesta_crear')
    else:
        messages.error(request, 'No tiene permisos')
        return redirect('main_admin')

# Vista para ver detalle de encuesta
@login_required
def encuesta_ver(request, encuesta_id=None):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        try:
            encuesta_data = Encuesta.objects.get(pk=encuesta_id)
            preguntas = Pregunta.objects.filter(id_encuesta=encuesta_data)
            
            return render(request, 'encuesta/encuesta_ver.html', {
                'encuesta_data': encuesta_data,
                'preguntas': preguntas
            })
        except Encuesta.DoesNotExist:
            messages.error(request, 'La encuesta no existe')
            return redirect('main_encuesta')
    else:
        messages.error(request, 'No tiene permisos')
        return redirect('main_admin')

# Vista para actualizar encuesta
@login_required
def encuesta_actualiza(request, encuesta_id=None):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        # Si es POST, actualizar
        if request.method == 'POST':
            id_encuesta = request.POST.get('id_encuesta')
            titulo_encuesta = request.POST.get('titulo_encuesta')
            descripcion_incidente = request.POST.get('descripcion_incidente')
            prioridad = request.POST.get('prioridad')
            id_departamento = request.POST.get('id_departamento')
            id_tipo_incidencia = request.POST.get('id_tipo_incidencia')
            
            if not all([titulo_encuesta, descripcion_incidente, id_departamento, id_tipo_incidencia]):
                messages.error(request, 'Debe completar todos los campos obligatorios')
                return redirect('encuesta_actualiza', encuesta_id=id_encuesta)
            
            try:
                encuesta = Encuesta.objects.get(pk=id_encuesta)
                
                # Verificar que la encuesta no esté activa (según requerimientos)
                if encuesta.activo:
                    messages.error(request, 'No es posible editar una encuesta activa. Debe bloquearla primero.')
                    return redirect('encuesta_actualiza', encuesta_id=id_encuesta)
                
                encuesta.titulo_encuesta = titulo_encuesta
                encuesta.descripcion_incidente = descripcion_incidente
                encuesta.prioridad = prioridad
                encuesta.id_departamento_id = id_departamento
                encuesta.id_tipo_incidencia_id = id_tipo_incidencia
                encuesta.save()
                
                # Procesar preguntas existentes (marcadas para eliminar)
                preguntas_eliminadas = request.POST.getlist('preguntas_eliminadas[]')
                for pregunta_id, valor in zip(request.POST.getlist('preguntas_existentes[]'), preguntas_eliminadas):
                    if valor == '1':  # Si está marcada para eliminar
                        try:
                            pregunta = Pregunta.objects.get(pk=pregunta_id.split('[')[1].split(']')[0])
                            pregunta.delete()
                        except (Pregunta.DoesNotExist, IndexError):
                            pass

                # Procesar nuevas preguntas
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
                return redirect('encuesta_actualiza', encuesta_id=id_encuesta)
        
        # Si es GET, mostrar formulario
        else:
            try:
                encuesta_data = Encuesta.objects.get(pk=encuesta_id)
                preguntas = Pregunta.objects.filter(id_encuesta=encuesta_data)
                departamentos = Departamento.objects.filter(activo=True)
                tipo_incidencias = TipoIncidencia.objects.filter(activo=True)
                
                return render(request, 'encuesta/encuesta_actualizar.html', {
                    'encuesta_data': encuesta_data,
                    'preguntas': preguntas,
                    'departamentos': departamentos,
                    'tipo_incidencias': tipo_incidencias,
                    'prioridades': Encuesta.PRIORIDADES
                })
            except Encuesta.DoesNotExist:
                messages.error(request, 'La encuesta no existe')
                return redirect('main_encuesta')
    else:
        messages.error(request, 'No tiene permisos')
        return redirect('main_admin')

# Vista para bloquear encuesta
@login_required
def encuesta_bloquea(request, encuesta_id=None):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        try:
            encuesta = Encuesta.objects.get(pk=encuesta_id)
            encuesta.activo = False
            encuesta.save()
            messages.success(request, 'Encuesta bloqueada correctamente')
            return redirect('main_encuesta')
        except Encuesta.DoesNotExist:
            messages.error(request, 'La encuesta no existe')
            return redirect('main_encuesta')
    else:
        messages.error(request, 'No tiene permisos')
        return redirect('main_admin')

# Vista para activar encuesta
@login_required
def encuesta_activa(request, encuesta_id=None):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        try:
            encuesta = Encuesta.objects.get(pk=encuesta_id)
            encuesta.activo = True
            encuesta.save()
            messages.success(request, 'Encuesta activada correctamente')
            return redirect('main_encuesta')
        except Encuesta.DoesNotExist:
            messages.error(request, 'La encuesta no existe')
            return redirect('main_encuesta')
    else:
        messages.error(request, 'No tiene permisos')
        return redirect('main_admin')