from django.core.management.base import BaseCommand
from register.models import Profile, User, Perfiles
from departamento.models import Departamento
from direccion.models import Direccion
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Repara la base de datos y crea los perfiles necesarios'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando reparación del sistema...'))

        # 1. Crear Perfiles (Esencial)
        perfiles = [
            (1, 'SECPLA'),
            (2, 'DIRECCION'),
            (3, 'DEPARTAMENTO'),
            (4, 'TERRITORIAL'),
            (5, 'CUADRILLA')
        ]
        
        for pid, nombre in perfiles:
            obj, created = Profile.objects.update_or_create(
                id=pid, 
                defaults={'nombre_perfil': nombre}
            )
            estado = "Creado" if created else "Ya existía"
            self.stdout.write(f"- Perfil {nombre}: {estado}")

        # 2. Crear Direcciones y Departamentos de Prueba (Para que los selectores no estén vacíos)
        dir1, _ = Direccion.objects.get_or_create(id_direccion=1, defaults={'nombre_direccion': 'Dirección de Obras', 'activo': True})
        dir2, _ = Direccion.objects.get_or_create(id_direccion=2, defaults={'nombre_direccion': 'DIDECO', 'activo': True})
        
        Departamento.objects.get_or_create(id=1, defaults={'nombre_departamento': 'Aseo y Ornato', 'direccion': dir1, 'activo': True})
        Departamento.objects.get_or_create(id=2, defaults={'nombre_departamento': 'Asistencia Social', 'direccion': dir2, 'activo': True})
        
        self.stdout.write(self.style.SUCCESS('✅ DATOS BASE CREADOS CORRECTAMENTE'))
        self.stdout.write(self.style.SUCCESS('   - Perfiles: OK'))
        self.stdout.write(self.style.SUCCESS('   - Departamentos: OK'))
        self.stdout.write(self.style.SUCCESS('   - Direcciones: OK'))