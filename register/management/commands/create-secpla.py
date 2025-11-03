from django.core.management.base import BaseCommand
from register.models import User, Profile

class Command(BaseCommand):
    help = 'Crea el primer usuario Secpla'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Forzar la creación incluso si ya existe el usuario'
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if User.objects.filter(username='admin').exists():
            if not force:
                self.stdout.write(
                    self.style.WARNING('El usuario admin ya existe. Usa --force para recrearlo. (Precaucion: usar --force borrara todos los usuarios creados.)')
                )
                return
            else:
                User.objects.filter(username='admin').delete()
                self.stdout.write('Usuario admin existente eliminado.')

        if not Profile.objects.exists():
            self.stdout.write(
                self.style.WARNING('No existen perfiles, ejecute el comando "create-profiles" primero.')
            )
            return

        perfil_secpla = Profile.objects.get(nombre_perfil='SECPLA')

        user = User(
            nombre='Administrador',
            apellido='Secpla', 
            username='admin',
            email='secpla@municipalidad.cl',
            telefono='912345678',
            perfil=perfil_secpla,
            first_session=True
        )

        user.set_password('admin')
        user.save()

        self.stdout.write(
            self.style.SUCCESS('Usuario Secpla creado exitosamente')
        )
        self.stdout.write('Usuario: admin')
        self.stdout.write('Contraseña: admin')
        self.stdout.write('Cambia la contraseña en el primer inicio de sesión')