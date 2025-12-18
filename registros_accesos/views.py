from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from .models import RegistroAcceso
from .serializers import RegistroAccesoSerializer
from django.db.models import Q
from residentes.models import Residente
from empleados.models import Empleado

class RegistroAccesoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows access logs to be viewed or edited.
    Supports file uploads for photos.
    """
    queryset = RegistroAcceso.objects.all()
    serializer_class = RegistroAccesoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] # To handle file uploads

    # Add searching and ordering
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_completo', 'ci', 'tipo_persona', 'motivo']
    ordering_fields = ['fecha_hora', 'tipo_persona', 'tipo_acceso', 'nombre_completo']

    def get_queryset(self):
        queryset = super().get_queryset()
        residente_id = self.request.query_params.get('residente_id', None)
        empleado_id = self.request.query_params.get('empleado_id', None)

        if residente_id is not None:
            try:
                residente = Residente.objects.get(id=residente_id)
                queryset = queryset.filter(Q(tipo_persona='Residente') & Q(ci=residente.ci))
            except Residente.DoesNotExist:
                queryset = queryset.none() # Return empty queryset if resident does not exist
        if empleado_id is not None:
            try:
                empleado = Empleado.objects.get(id=empleado_id)
                queryset = queryset.filter(Q(tipo_persona='Empleado') & Q(ci=empleado.ci))
            except Empleado.DoesNotExist:
                queryset = queryset.none() # Return empty queryset if employee does not exist
        
        return queryset

    def get_serializer_context(self):
        """
        Pass the request object to the serializer context.
        """
        return {'request': self.request}
