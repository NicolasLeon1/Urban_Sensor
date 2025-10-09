from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from registration.models import Profile
from usuarios.models import Usuario, Perfil

# Vista principal - Listar usuarios
@login_required
def main_usuario(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:  # Solo Admin
        usuario_listado = Usuario.objects.filter(state='Activo').order_by('nombre')
        return render(request, 'usuarios/main_usuario.html', {'usuario_listado': usuario_listado})
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

# Vista para mostrar formulario de crear usuario
@login_required
def usuario_crear(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        perfiles_listado = Perfil.PERFIL_CHOICES
        return render(request, 'usuarios/usuario_crear.html', {'perfiles_listado': perfiles_listado})
    else:
        messages.error(request, 'No tiene permisos para acceder a esta sección')
        return redirect('main_admin')

# Vista para guardar usuario
@login_required
def usuario_guardar(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')
            perfil_seleccionado = request.POST.get('perfil')
            
            if nombre == '' or apellido == '' or correo == '' or telefono == '' or perfil_seleccionado == '':
                messages.error(request, 'Debe completar todos los campos')
                return redirect('usuario_crear')
            
            # Verificar si el correo ya existe
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, 'El correo ya está registrado')
                return redirect('usuario_crear')
            
            try:
                # Crear usuario de Django (auth_user)
                from django.contrib.auth.models import User
                user = User.objects.create_user(
                    username=correo,
                    email=correo,
                    first_name=nombre,
                    last_name=apellido
                )
                user.set_password('temporal123')  # Contraseña temporal
                user.save()
                
                # Crear perfil asociado
                perfil = Perfil.objects.create(
                    id_usuario=user,
                    nombre_perfil=perfil_seleccionado
                )
                
                # Crear registro en tabla Usuario
                usuario_save = Usuario(
                    id_perfil=perfil,
                    nombre=nombre,
                    apellido=apellido,
                    correo=correo,
                    telefono=telefono
                )
                usuario_save.save()
                
                messages.success(request, 'Usuario creado correctamente')
                return redirect('main_usuario')
                
            except Exception as e:
                messages.error(request, f'Error al crear usuario: {str(e)}')
                return redirect('usuario_crear')
    else:
        messages.error(request, 'No tiene permisos')
        return redirect('main_admin')

# Vista para ver detalle de usuario
@login_required
def usuario_ver(request, usuario_id=None):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        usuario_count = Usuario.objects.filter(pk=usuario_id).count()
        if usuario_count == 0:
            messages.error(request, 'El usuario no existe')
            return redirect('main_usuario')
        
        usuario_data = Usuario.objects.get(pk=usuario_id)
        return render(request, 'usuarios/usuario_ver.html', {'usuario_data': usuario_data})
    else:
        messages.error(request, 'No tiene permisos')
        return redirect('main_admin')

# Vista para actualizar usuario
@login_required
def usuario_actualiza(request, usuario_id=None):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        messages.error(request, 'No tiene perfil asociado')
        return redirect('check_profile')
    
    if profile.group_id == 1:
        # Si es POST, actualizar
        if request.method == 'POST':
            id_usuario = request.POST.get('id_usuario')
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')
            perfil_seleccionado = request.POST.get('perfil')
            
            if nombre == '' or apellido == '' or correo == '' or telefono == '':
                messages.error(request, 'Debe completar todos los campos')
                return redirect('usuario_actualiza', usuario_id=id_usuario)
            
            try:
                usuario = Usuario.objects.get(pk=id_usuario)
                usuario.nombre = nombre
                usuario.apellido = apellido
                usuario.correo = correo
                usuario.telefono = telefono
                
                # Actualizar perfil si cambió
                if perfil_seleccionado != usuario.id_perfil.nombre_perfil:
                    usuario.id_perfil.nombre_perfil = perfil_seleccionado
                    usuario.id_perfil.save()
                
                usuario.save()
                
                messages.success(request, 'Usuario actualizado correctamente')
                return redirect('main_usuario')
                
            except Exception as e:
                messages.error(request, f'Error al actualizar: {str(e)}')
                return redirect('usuario_actualiza', usuario_id=id_usuario)
        
        # Si es GET, mostrar formulario
        else:
            usuario_count = Usuario.objects.filter(pk=usuario_id).count()
            if usuario_count == 0:
                messages.error(request, 'El usuario no existe')
                return redirect('main_usuario')
            
            usuario_data = Usuario.objects.get(pk=usuario_id)
            perfiles_listado = Perfil.PERFIL_CHOICES
            return render(request, 'usuarios/usuario_actualiza.html', {
                'usuario_data': usuario_data,
                'perfiles_listado': perfiles_listado
            })
    else:
        messages.error(request, 'No tiene permisos')
        return redirect('main_admin')



@login_required
def usuario_bloquea(request, usuario_id):
    
    try:
        current_user_profile = Profile.objects.get(user=request.user)
        if current_user_profile.group.name != 'Admin':
            messages.error(request, 'No tienes permisos para realizar esta acción.')
            return redirect('home')
    except Profile.DoesNotExist:
        messages.error(request, 'Tu perfil no está configurado.')
        return redirect('logout')

    try:
        # CAMBIA ESTA LÍNEA
        Usuario.objects.filter(pk=usuario_id).update(state='Bloqueado')
        messages.success(request, 'Usuario bloqueado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al bloquear el usuario: {e}')
    
    return redirect('main_usuario')



@login_required
def main_usuario_bloqueado(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id) 
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Hubo un error de perfil')
        return redirect('login')

    if profile.group_id == 1: 
   
        usuarios_bloqueados = Usuario.objects.filter(state='Bloqueado').order_by('nombre')
        
        template_name = 'usuarios/main_usuario_bloqueado.html'
        # Envía la lista de Usuarios, no de Profiles
        return render(request, template_name, {'usuario_listado': usuarios_bloqueados})
    else:
        return redirect('logout')



@login_required
def usuario_desbloquea(request, usuario_id):
    try:
        profile = Profile.objects.get(user_id=request.user.id) 
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, 'Hubo un error de perfil')
        return redirect('logout')

    if profile.group_id == 1:
     
        Usuario.objects.filter(pk=usuario_id).update(state='Activo')
        
        messages.add_message(request, messages.INFO, 'Usuario desbloqueado')
        return redirect('main_usuario_bloqueado')
    else:
        return redirect('logout')