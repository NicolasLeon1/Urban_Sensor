from django.db import models
from django.utils import timezone
from departamento.models import Departamento
from direccion.models import Direccion
import secrets
import hashlib
import re

from enum import Enum

class Perfiles(Enum):
    SECPLA = 1
    DIRECCION = 2
    DEPARTAMENTO = 3
    TERRITORIAL = 4
    CUADRILLA = 5

class Profile(models.Model):
    nombre_perfil = models.CharField()

    def __str__(self):
        return self.nombre_perfil

class User(models.Model):
    nombre = models.CharField(max_length=48)
    apellido = models.CharField(max_length=48)
    username = models.CharField(unique=True, max_length=24)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=9)
    password = models.CharField(max_length=128)
    perfil = models.ForeignKey(Profile, on_delete=models.CASCADE)

    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, null=True)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, null=True)

    session_token = models.CharField(max_length = 255,null=True, blank=True, default=None)
    expires_at = models.DateTimeField(null=True, blank=True)

    first_session = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    activo = models.BooleanField(default=True)

    @classmethod
    def generate_token(cls):
        return f"auth_{secrets.token_urlsafe(32)}"
    
    def check_password(self, raw_password):
        hashed_password = hashlib.sha256(raw_password.encode()).hexdigest()
        return hashed_password == self.password
    
    def set_password(self, raw_password):
        hashed_password = hashlib.sha256(raw_password.encode()).hexdigest()
        self.password = hashed_password
        

    @classmethod
    def validar_contraseña(cls, raw_password, username, nombre, apellido):    
        errores = []
        
        if len(raw_password) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")
        
        info_personal = [username, nombre, apellido]
        
        for info in info_personal:
            if info and info.lower() in raw_password.lower():
                errores.append(f"La contraseña no puede contener: {info}")
        
        numeros = re.findall(r'\d', raw_password)
        if len(numeros) < 4:
            errores.append("La contraseña debe contener al menos 4 números")
        
        caracteres_especiales = re.findall(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', raw_password)
        if len(caracteres_especiales) < 1:
            errores.append("La contraseña debe contener al menos un carácter especial")
        
        if errores:
            return False, errores
        else:
            return True, "Contraseña válida"
    
    @classmethod
    def is_username_valid(cls, username):
        try:
            User.objects.get(username=username)
            return False
        except:
            return True
    
    @classmethod
    def is_email_valid(cls, email):
        try:
            User.objects.get(email=email)
            return False
        except:
            return True
    
    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['created']

    def __str__(self):
        return f'{self.nombre} {self.apellido}'