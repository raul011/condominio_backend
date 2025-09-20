from rest_framework.routers import DefaultRouter
from .views import AreaComunViewSet, InventarioViewSet, VerificacionInventarioViewSet, ReservaViewSet

router = DefaultRouter()
router.register(r'areas-comunes', AreaComunViewSet)
router.register(r'inventario', InventarioViewSet)
router.register(r'verificacion-inventario', VerificacionInventarioViewSet)
router.register(r'reservas', ReservaViewSet)

urlpatterns = router.urls
