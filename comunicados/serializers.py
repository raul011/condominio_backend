from rest_framework import serializers
from .models import Comunicado, ComunicadoResidente



class ComunicadoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Comunicado
        fields = '__all__'

        
class ComunicadoResidenteSerializer(serializers.ModelSerializer):
    residente_nombre = serializers.CharField(source='residente.nombre_completo', read_only=True)
    #comunicado_titulo = serializers.CharField(source='comunicado.titulo', read_only=True)
    #comunicado_contenido = serializers.CharField(source='comunicado.contenido', read_only=True)
    #comunicado_detalle = ComunicadoSerializer(source='comunicado', read_only=True)

    class Meta:
        model = ComunicadoResidente
        fields = '__all__'




