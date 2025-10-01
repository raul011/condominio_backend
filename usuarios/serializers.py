from rest_framework import serializers
from .models import User
from residentes.serializers import ResidenteSerializer
from empleados.serializers import EmpleadoSerializer

# users/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    residente = ResidenteSerializer(read_only=True)
    empleado = EmpleadoSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name',
            'last_name', 'residente', 'empleado', 'is_staff'
        ]
        read_only_fields = ['is_staff']





class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Determinar el role según las relaciones
        if self.user.residente is not None:
            role = "residente"
        elif self.user.empleado is not None:
            role = "empleado"
        else:
            role = "usuario"  # valor por defecto si no tiene relación
        
        # Agregar role al payload de la respuesta
        data["role"] = role

        # Puedes agregar más campos si quieres
        data["username"] = self.user.username
        data["email"] = self.user.email

        return data
