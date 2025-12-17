from rest_framework import viewsets, permissions
from .models import Tarea
from .serializers import TareaSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class TareaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    """
    queryset = Tarea.objects.all().order_by('-fecha_creacion')
    serializer_class = TareaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Add filtering capabilities
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'prioridad', 'empleado_asignado']
    search_fields = ['titulo', 'descripcion']
    ordering_fields = ['fecha_limite', 'prioridad', 'estado']

    def get_serializer_context(self):
        """
        Pass the request object to the serializer context.
        """
        return {'request': self.request}
