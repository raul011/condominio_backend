from rest_framework import serializers
from .models import Empleado, CargoEmpleado, EmpresaExterna


class CargoEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoEmpleado
        fields = '__all__'


class EmpleadoSerializer(serializers.ModelSerializer):
    cargo_nombre = serializers.CharField(source='cargo.cargo', read_only=True)
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Empleado
        fields = [
            'id', 'nombre', 'apellido', 'nombre_completo',
            'ci', 'telefono', 'direccion', 'cargo', 'cargo_nombre'
        ]


class EmpresaExternaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpresaExterna
        fields = '__all__'
