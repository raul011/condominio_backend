from rest_framework import serializers
from .models import CategoriaInventario


class CategoriaInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaInventario
        fields = '__all__'
