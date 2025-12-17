from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegistroSeguridadViewSet, ReclamoViewSet, ObjectDetectionView

router = DefaultRouter()
router.register(r'registros-seguridad', RegistroSeguridadViewSet)
router.register(r'reclamos', ReclamoViewSet)

# The router URLs are included first, then the custom path for object detection
urlpatterns = router.urls + [
    path('detect/', ObjectDetectionView.as_view(), name='object_detection'),
]
