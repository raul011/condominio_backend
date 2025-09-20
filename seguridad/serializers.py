from rest_framework import serializers
from .models import RegistroSeguridad, Reclamo


class RegistroSeguridadSerializer(serializers.ModelSerializer):
    user_nombre = serializers.CharField(source='user.username', read_only=True)
    resuelto_por_nombre = serializers.CharField(source='resuelto_por.username', read_only=True)

    class Meta:
        model = RegistroSeguridad
        fields = '__all__'


class ReclamoSerializer(serializers.ModelSerializer):
    residente_nombre = serializers.CharField(source='residente.nombre_completo', read_only=True)
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)

    class Meta:
        model = Reclamo
        fields = '__all__'
