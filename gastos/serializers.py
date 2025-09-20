from rest_framework import serializers
from .models import Gasto, TipoGasto


class TipoGastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoGasto
        fields = '__all__'


class GastoSerializer(serializers.ModelSerializer):
    tipo_gasto_nombre = serializers.CharField(source='tipo_gasto.nombre', read_only=True)

    class Meta:
        model = Gasto
        fields = '__all__'
