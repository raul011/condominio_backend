from rest_framework import serializers
from .models import AreaComun, Inventario, VerificacionInventario, Reserva


class AreaComunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaComun
        fields = '__all__'


class InventarioSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    area_comun_nombre = serializers.CharField(source='area_comun.nombre', read_only=True)
    user_nombre = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Inventario
        fields = '__all__'


class VerificacionInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificacionInventario
        fields = '__all__'


class ReservaSerializer(serializers.ModelSerializer):
    area_comun_nombre = serializers.CharField(source='area_comun.nombre', read_only=True)
    residente_nombre = serializers.CharField(source='residente.nombre_completo', read_only=True)

    class Meta:
        model = Reserva
        fields = '__all__'
