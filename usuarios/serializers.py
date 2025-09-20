from rest_framework import serializers
from .models import User
from residentes.serializers import ResidenteSerializer
from empleados.serializers import EmpleadoSerializer


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
