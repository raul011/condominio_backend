from rest_framework import serializers
from .models import Residente, Unidad, Visita, Notificacion


class ResidenteSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Residente
        fields = ['id', 'nombre', 'apellido', 'nombre_completo', 'ci', 'email', 'tipo_residente']


class UnidadSerializer(serializers.ModelSerializer):
    residente_nombre = serializers.CharField(source='residente.nombre_completo', read_only=True)

    class Meta:
        model = Unidad
        fields = '__all__'


class VisitaSerializer(serializers.ModelSerializer):
    residente_nombre = serializers.CharField(source='residente.nombre_completo', read_only=True)
    user_entrada_nombre = serializers.CharField(source='user_entrada.username', read_only=True)
    user_salida_nombre = serializers.CharField(source='user_salida.username', read_only=True)

    class Meta:
        model = Visita
        fields = '__all__'


class NotificacionSerializer(serializers.ModelSerializer):
    user_nombre = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Notificacion
        fields = '__all__'
