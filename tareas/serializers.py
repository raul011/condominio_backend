from rest_framework import serializers
from .models import Tarea

class TareaSerializer(serializers.ModelSerializer):
    # Read-only fields to return related object names
    empleado_asignado_nombre = serializers.CharField(source='empleado_asignado.nombre_completo', read_only=True)
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)

    class Meta:
        model = Tarea
        fields = [
            'id',
            'titulo',
            'descripcion',
            'fecha_creacion',
            'fecha_limite',
            'estado',
            'prioridad',
            'empleado_asignado',
            'empleado_asignado_nombre',
            'creado_por',
            'creado_por_username',
        ]
        # Make creado_por read-only as it will be set automatically from the request user
        read_only_fields = ['creado_por', 'creado_por_username', 'empleado_asignado_nombre']

    def create(self, validated_data):
        # Automatically assign the logged-in user as the creator
        validated_data['creado_por'] = self.context['request'].user
        return super().create(validated_data)
