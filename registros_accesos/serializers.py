from rest_framework import serializers
from .models import RegistroAcceso
from residentes.models import Residente
from empleados.models import Empleado

class RegistroAccesoSerializer(serializers.ModelSerializer):
    registrado_por_username = serializers.CharField(source='registrado_por.username', read_only=True)
    foto_url = serializers.ImageField(source='foto', read_only=True, allow_empty_file=False, use_url=True)

    # Write-only fields for linking existing Residente/Empleado
    residente_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    empleado_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    # Read-only fields to display associated names/CIs
    residente_nombre = serializers.SerializerMethodField()
    residente_ci = serializers.SerializerMethodField()
    empleado_nombre = serializers.SerializerMethodField()
    empleado_ci = serializers.SerializerMethodField()

    class Meta:
        model = RegistroAcceso
        fields = [
            'id',
            'tipo_persona',
            'nombre_completo', # Can be auto-populated or manually entered
            'ci',              # Can be auto-populated or manually entered
            'motivo',
            'tipo_acceso',
            'fecha_hora',
            'foto',
            'foto_url',
            'registrado_por',
            'registrado_por_username',
            # New fields for linking/display
            'residente_id',
            'empleado_id',
            'residente_nombre',
            'residente_ci',
            'empleado_nombre',
            'empleado_ci',
        ]
        read_only_fields = [
            'registrado_por', 'registrado_por_username', 'foto_url',
            'residente_nombre', 'residente_ci', 'empleado_nombre', 'empleado_ci'
        ]
    
    def get_residente_nombre(self, obj):
        return obj.nombre_completo if obj.tipo_persona == 'Residente' else None

    def get_residente_ci(self, obj):
        return obj.ci if obj.tipo_persona == 'Residente' else None
    
    def get_empleado_nombre(self, obj):
        return obj.nombre_completo if obj.tipo_persona == 'Empleado' else None

    def get_empleado_ci(self, obj):
        return obj.ci if obj.tipo_persona == 'Empleado' else None

    def validate(self, data):
        tipo_persona = data.get('tipo_persona')
        residente_id = data.get('residente_id')
        empleado_id = data.get('empleado_id')
        nombre_completo = data.get('nombre_completo')
        ci = data.get('ci')

        if tipo_persona == 'Residente':
            if not residente_id:
                raise serializers.ValidationError({"residente_id": "Debe seleccionar un residente existente."})
            try:
                residente = Residente.objects.get(id=residente_id)
                data['nombre_completo'] = residente.nombre_completo
                data['ci'] = residente.ci
            except Residente.DoesNotExist:
                raise serializers.ValidationError({"residente_id": "El residente seleccionado no existe."})
            
            if empleado_id:
                raise serializers.ValidationError({"empleado_id": "No se puede asignar un empleado si el tipo de persona es Residente."})
        
        elif tipo_persona == 'Empleado':
            if not empleado_id:
                raise serializers.ValidationError({"empleado_id": "Debe seleccionar un empleado existente."})
            try:
                empleado = Empleado.objects.get(id=empleado_id)
                data['nombre_completo'] = empleado.nombre_completo
                data['ci'] = empleado.ci
            except Empleado.DoesNotExist:
                raise serializers.ValidationError({"empleado_id": "El empleado seleccionado no existe."})
            
            if residente_id:
                raise serializers.ValidationError({"residente_id": "No se puede asignar un residente si el tipo de persona es Empleado."})

        else: # Visitante, Proveedor, Otro
            if residente_id or empleado_id:
                raise serializers.ValidationError({"residente_id": "No se puede asignar un residente o empleado para este tipo de persona."})
            if not nombre_completo:
                raise serializers.ValidationError({"nombre_completo": "El nombre completo es obligatorio para visitantes/proveedores."})
            # CI is optional for these types, so no validation needed if not provided
            
        return data

    def create(self, validated_data):
        # Automatically assign the logged-in user as the creator
        validated_data['registrado_por'] = self.context['request'].user
        
        # Remove _id fields as they are write_only and not model fields
        validated_data.pop('residente_id', None)
        validated_data.pop('empleado_id', None)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Remove _id fields as they are write_only and not model fields
        validated_data.pop('residente_id', None)
        validated_data.pop('empleado_id', None)

        return super().update(instance, validated_data)
