from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    PERFIL_CHOICES = [
        ('Admin', 'Usuario Administrador'),
        ('Direccion', 'Usuario Dirección'),
        ('Departamento', 'Usuario Departamento'),
        ('Territorial', 'Usuario Territorial'),
        ('Cuadrilla', 'Usuario Cuadrilla'),
    ]
    
    id_perfil = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_usuario')
    nombre_perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES)
    state = models.CharField(max_length=10, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'perfil'
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
    
    def __str__(self):
        return f"{self.id_usuario.get_full_name()} - {self.nombre_perfil}"

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    id_perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='usuarios')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(max_length=150, unique=True)
    telefono = models.CharField(max_length=15)
    state = models.CharField(max_length=10, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"