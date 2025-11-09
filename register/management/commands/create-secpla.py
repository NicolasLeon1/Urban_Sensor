from django.core.management.base import BaseCommand
from register.models import User, Profile

class Command(BaseCommand):
    help = 'Crea el primer usuario Secpla'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Forzar la creación incluso si ya existen usuarios'
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if User.objects.exists():
            if not force:
                self.stdout.write(
                    self.style.WARNING('Ya existen usuarios en el sistema. Usa --force para recrearlos. (Precaucion: usar --force borrara todos los usuarios existentes.)')
                )
                return
            else:
                User.objects.all().delete()
                self.stdout.write('Todos los usuarios existentes han sido eliminados.')

        if not Profile.objects.exists():
            self.stdout.write(
                self.style.WARNING('No existen perfiles, ejecute el comando "create-profiles" primero.')
            )
            return

        perfil_secpla = Profile.objects.get(nombre_perfil='SECPLA')
        perfil_departamento = Profile.objects.get(nombre_perfil='Departamento')
        perfil_direccion = Profile.objects.get(nombre_perfil='Direccion')
        perfil_territorial = Profile.objects.get(nombre_perfil='Territorial')
        perfil_cuadrilla = Profile.objects.get(nombre_perfil='Cuadrilla')

        secpla = User(
            nombre='Administrador',
            apellido='Secpla',
            username='admin',
            email='secpla@municipalidad.cl',
            telefono='912345678',
            perfil=perfil_secpla,
            first_session=False
        )

        departamento = User(
            nombre='Departamento',
            apellido='Departamento',
            username='depto',
            email='departamento@municipalidad.cl',
            telefono='912345678',
            perfil=perfil_departamento,
            first_session=False
        )

        direccion = User(
            nombre='Direccion',
            apellido='Direccion',
            username='dir',
            email='direccion@municipalidad.cl',
            telefono='912345678',
            perfil=perfil_direccion,
            first_session=False
        )

        territorial = User(
            nombre='Territorial',
            apellido='Territorial',
            username='ter',
            email='territorial@municipalidad.cl',
            telefono='912345678',
            perfil=perfil_territorial,
            first_session=False
        )

        cuadrilla = User(
            nombre='Cuadrilla',
            apellido='Cuadrilla',
            username='cuad',
            email='cuadrilla@municipalidad.cl',
            telefono='912345678',
            perfil=perfil_cuadrilla,
            first_session=False
        )

        secpla.set_password('admin')
        departamento.set_password('depto')
        direccion.set_password('dir')
        territorial.set_password('ter')
        cuadrilla.set_password('cuad')

        secpla.save()
        departamento.save()
        direccion.save()
        territorial.save()
        cuadrilla.save()

        self.stdout.write(
            self.style.SUCCESS('Usuarios creados exitosamente')
        )
        self.stdout.write('=== Credenciales por perfil ===')
        self.stdout.write('SECPLA:')
        self.stdout.write('  Usuario: admin')
        self.stdout.write('  Contraseña: admin')
        self.stdout.write('Departamento:')
        self.stdout.write('  Usuario: depto')
        self.stdout.write('  Contraseña: depto')
        self.stdout.write('Direccion:')
        self.stdout.write('  Usuario: dir')
        self.stdout.write('  Contraseña: dir')
        self.stdout.write('Territorial:')
        self.stdout.write('  Usuario: ter')
        self.stdout.write('  Contraseña: ter')
        self.stdout.write('Cuadrilla:')
        self.stdout.write('  Usuario: cuad')
        self.stdout.write('  Contraseña: cuad')