from rest_framework import serializers
from register.models import User, Profile
from departamento.models import Departamento
from direccion.models import Direccion

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    # Estos campos extra muestran el nombre real en lugar de solo el número ID
    perfil_nombre = serializers.CharField(source='perfil.nombre_perfil', read_only=True)
    departamento_nombre = serializers.CharField(source='departamento.nombre_departamento', read_only=True)
    direccion_nombre = serializers.CharField(source='direccion.nombre_direccion', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'nombre', 'apellido', 'username', 'email', 'telefono', 
            'perfil', 'perfil_nombre', 
            'departamento', 'departamento_nombre', 
            'direccion', 'direccion_nombre', 
            'activo'
        ]