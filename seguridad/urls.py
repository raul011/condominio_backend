from rest_framework.routers import DefaultRouter
from .views import RegistroSeguridadViewSet, ReclamoViewSet

router = DefaultRouter()
router.register(r'registros-seguridad', RegistroSeguridadViewSet)
router.register(r'reclamos', ReclamoViewSet)

urlpatterns = router.urls
