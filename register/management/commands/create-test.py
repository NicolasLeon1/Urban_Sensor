from django.core.management.base import BaseCommand
from departamento.models import Departamento
from incidencia.models import TipoIncidencia
from direccion.models import Direccion
from register.models import User, Profile

class Command(BaseCommand):
    help = 'Configura datos de prueba básicos para el sistema de incidencias municipales'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando configuración de datos de prueba básicos...'))
        
        direcciones_data = [
            'Dirección de Obras Municipales',
            'Dirección de Medio Ambiente'
        ]
        
        direcciones = []
        for nombre in direcciones_data:
            direccion = Direccion(nombre_direccion=nombre)
            direccion.save()
            direcciones.append(direccion)
            self.stdout.write(self.style.SUCCESS(f'Dirección creada: {nombre}'))

        departamentos_data = [
            ('Departamento de Obras Públicas', direcciones[0]),
            ('Departamento de Alumbrado Público', direcciones[0]),
            ('Departamento de Áreas Verdes', direcciones[1]),
            ('Departamento de Control Ambiental', direcciones[1])
        ]
        
        departamentos = []
        for nombre, direccion in departamentos_data:
            departamento = Departamento(
                nombre_departamento=nombre,
                direccion=direccion
            )
            departamento.save()
            departamentos.append(departamento)
            self.stdout.write(self.style.SUCCESS(f'Departamento creado: {nombre}'))

        tipos_incidencia_data = [
            ('Bache en calle principal', direcciones[0], departamentos[0]),
            ('Cuneta obstruida', direcciones[0], departamentos[0]),
            ('Alumbrado público defectuoso', direcciones[0], departamentos[1]),
            ('Poste de luz dañado', direcciones[0], departamentos[1]),
            ('Árbol caído en vía pública', direcciones[1], departamentos[2]),
            ('Césped sin cortar en área pública', direcciones[1], departamentos[2]),
            ('Acumulación de basura', direcciones[1], departamentos[3]),
            ('Quema de residuos no autorizada', direcciones[1], departamentos[3])
        ]
        
        for nombre, direccion, departamento in tipos_incidencia_data:
            tipo = TipoIncidencia(
                nombre_incidencia=nombre,
                id_direccion=direccion,
                id_departamento=departamento
            )
            tipo.save()
            self.stdout.write(self.style.SUCCESS(f'Tipo de incidencia creado: {nombre}'))

        perfil_secpla = Profile.objects.get(nombre_perfil='SECPLA')
        perfil_departamento = Profile.objects.get(nombre_perfil='Departamento')
        perfil_direccion = Profile.objects.get(nombre_perfil='Direccion')
        perfil_territorial = Profile.objects.get(nombre_perfil='Territorial')
        perfil_cuadrilla = Profile.objects.get(nombre_perfil='Cuadrilla')

        user_secpla = User(
            nombre='Administrador',
            apellido='SECPLA',
            username='secpla1',
            email='secpla1@municipalidad.com',
            telefono='912345670',
            perfil=perfil_secpla
        )
        user_secpla.set_password('1234')
        user_secpla.save()
        self.stdout.write(self.style.SUCCESS('Usuario SECPLA creado: secpla1'))

        prefijo = 1
        for direccion in direcciones:
            user = User(
                nombre=f'Direccion',
                apellido=f'{prefijo}',
                username=f'direccion{prefijo}',
                email=f'direccion{prefijo}@municipalidad.com',
                telefono=f'91234567',
                perfil=perfil_direccion,
                direccion=direccion
            )
            user.set_password('1234')
            user.first_session = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario Dirección creado: direccion{prefijo} - Dirección: {direccion.nombre_direccion}'))
            prefijo += 1

        prefijo = 1
        for departamento in departamentos:
            user = User(
                nombre='Departamento',
                apellido=f'{prefijo}',
                username=f'departamento{prefijo}',
                email=f'departamento{prefijo}@municipalidad.com',
                telefono=f'9123456',
                perfil=perfil_departamento,
                departamento=departamento
            )
            user.set_password('1234')
            user.first_session = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario Departamento creado: departamento{prefijo} - Departamento: {departamento.nombre_departamento}'))
            prefijo += 1

        for i in range(1, 4):
            user = User(
                nombre=f'Inspector',
                apellido=f'{i}',
                username=f'territorial{i}',
                email=f'territorial{i}@municipalidad.com',
                telefono=f'9123456',
                perfil=perfil_territorial
            )
            user.set_password('1234')
            user.first_session = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario Territorial creado: territorial{i}'))

        cuadrillas_data = [
            ('cuadrilla1', 'Obras A', departamentos[0]),
            ('cuadrilla2', 'Obras B', departamentos[0]),
            
            ('cuadrilla3', 'Alumbrado A', departamentos[1]),
            ('cuadrilla4', 'Alumbrado B', departamentos[1]),
            
            ('cuadrilla5', 'Áreas Verdes A', departamentos[2]),
            ('cuadrilla6', 'Áreas Verdes B', departamentos[2]),
            
            ('cuadrilla7', 'Ambiental A', departamentos[3]),
            ('cuadrilla8', 'Ambiental B', departamentos[3])
        ]

        
        for username, nombre, departamento in cuadrillas_data:
            user = User(
                nombre='Cuadrilla',
                apellido=nombre,
                username=username,
                email=f'{username}@municipalidad.com',
                telefono=f'9123456',
                perfil=perfil_cuadrilla,
                departamento=departamento
            )
            user.set_password('1234')
            user.first_session = False
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario Cuadrilla creado: {username} - Departamento: {departamento.nombre_departamento}'))