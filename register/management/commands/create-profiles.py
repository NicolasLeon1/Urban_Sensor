from django.core.management.base import BaseCommand
from register.models import Profile

class Command(BaseCommand):
    help = 'Crea los perfiles del sistema con IDs especificos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Recrear todos los perfiles (elimina los existentes)'
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if Profile.objects.exists() and not force:
            self.stdout.write(
                self.style.WARNING('Ya existen perfiles. Usa --force para recrearlos.')
            )
            return
        
        if force and Profile.objects.exists():
            Profile.objects.all().delete()
            self.stdout.write('Perfiles existentes eliminados.')

        perfiles = [
            (1, 'SECPLA'),
            (2, 'Direccion'), 
            (3, 'Departamento'),
            (4, 'Territorial'),
            (5, 'Cuadrilla')
        ]

        for id_perfil, nombre_perfil in perfiles:
            existing_by_id = Profile.objects.filter(id=id_perfil).first()
            if existing_by_id and existing_by_id.nombre_perfil != nombre_perfil:
                self.stdout.write(
                    self.style.WARNING(f'Eliminando perfil con ID {id_perfil} (nombre incorrecto)')
                )
                existing_by_id.delete()
            
            existing_by_name = Profile.objects.filter(nombre_perfil=nombre_perfil).first()
            if existing_by_name and existing_by_name.id != id_perfil:
                self.stdout.write(
                    self.style.WARNING(f'Eliminando perfil {nombre_perfil} (ID incorrecto)')
                )
                existing_by_name.delete()
            
            profile, created = Profile.objects.get_or_create(
                id=id_perfil,
                defaults={'nombre_perfil': nombre_perfil}
            )
            
            if not created:
                profile.nombre_perfil = nombre_perfil
                profile.save()
                self.stdout.write(f'Perfil {nombre_perfil} (ID {id_perfil}) actualizado.')
            else:
                self.stdout.write(f'Perfil {nombre_perfil} (ID {id_perfil}) creado.')

        self.stdout.write(
            self.style.SUCCESS('Todos los perfiles creados con IDs correctos')
        )
        
        self.stdout.write('\nPerfiles creados:')
        for profile in Profile.objects.all().order_by('id'):
            self.stdout.write(f'  ID {profile.id}: {profile.nombre_perfil}')