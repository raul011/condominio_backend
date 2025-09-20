from rest_framework import serializers
from .models import Cuota, Pago, Multa, TipoCuota


class TipoCuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCuota
        fields = '__all__'


class CuotaSerializer(serializers.ModelSerializer):
    residente_nombre = serializers.CharField(source='residente.nombre_completo', read_only=True)
    tipo_cuota_nombre = serializers.CharField(source='tipo_cuota.nombre', read_only=True)
    user_nombre = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Cuota
        fields = '__all__'


class MultaSerializer(serializers.ModelSerializer):
    residente_nombre = serializers.CharField(source='residente.nombre_completo', read_only=True)
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)

    class Meta:
        model = Multa
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    user_nombre = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Pago
        fields = '__all__'
