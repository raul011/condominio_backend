from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ComunicadoViewSet, ComunicadoResidenteListView, ComunicadoResidentesListByComunicadoView

router = DefaultRouter()
router.register(r'comunicados', ComunicadoViewSet)

urlpatterns = router.urls + [
    path('comunicados/residente/<int:residente_id>/', ComunicadoResidenteListView.as_view(), name='comunicados-por-residente'),
    path('comunicados/<int:comunicado_id>/residentes/', ComunicadoResidentesListByComunicadoView.as_view(), name='residentes-por-comunicado'),
]
