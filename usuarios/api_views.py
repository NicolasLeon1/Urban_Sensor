from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import send_mail
from register.models import User, Profile, Perfiles
from departamento.models import Departamento
from direccion.models import Direccion
from incidencia.models import SolicitudIncidencia
from .serializers import UserSerializer, ProfileSerializer, DepartamentoSerializer, DireccionSerializer
import string
import secrets

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-created') # Ordenar por más reciente
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        # Esta función conecta el formulario de React con la base de datos
        data = request.data
        try:
            # 1. Validaciones
            if User.objects.filter(email=data.get('email')).exists():
                return Response({'error': 'El email ya está registrado'}, status=400)
            if User.objects.filter(username=data.get('username')).exists():
                return Response({'error': 'El username ya está ocupado'}, status=400)

            # 2. Guardar Usuario Base
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # 3. Generar Contraseña y Enviar Correo
            password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            user.set_password(password)
            user.save()
            
            print(f"✅ USUARIO CREADO: {user.username} / Pass: {password}") # Log en consola para ver que funciona

            # Intentar enviar correo (no falla si no hay internet)
            try:
                send_mail(
                    "Bienvenido a Urban Sensor",
                    f"Usuario: {user.username}\nClave: {password}",
                    'admin@urbansensor.cl',
                    [user.email],
                    fail_silently=True
                )
            except:
                pass

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        user = self.get_object()
        user.activo = not user.activo
        user.save()
        return Response({'status': 'ok', 'activo': user.activo})

# Esta vista envía los Perfiles, Deptos y Direcciones a los selectores de React
class DataOptionsViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({
            'perfiles': ProfileSerializer(Profile.objects.all(), many=True).data,
            'departamentos': DepartamentoSerializer(Departamento.objects.filter(activo=True), many=True).data,
            'direcciones': DireccionSerializer(Direccion.objects.filter(activo=True), many=True).data,
        })

# Esta vista envía los datos para los gráficos del Dashboard
class DashboardStatsViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({
            'total_usuarios': User.objects.count(),
            'total_abiertas': SolicitudIncidencia.objects.filter(estado='abierta').count(),
            'total_derivadas': SolicitudIncidencia.objects.filter(estado='derivada').count(),
            'total_rechazadas': SolicitudIncidencia.objects.filter(estado='rechazada').count(),
            'total_finalizadas': SolicitudIncidencia.objects.filter(estado='finalizada').count(),
        })