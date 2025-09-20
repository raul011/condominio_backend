from rest_framework.routers import DefaultRouter
from .views import ResidenteViewSet, UnidadViewSet, VisitaViewSet, NotificacionViewSet

router = DefaultRouter()
router.register(r'residentes', ResidenteViewSet)
router.register(r'unidades', UnidadViewSet)
router.register(r'visitas', VisitaViewSet)
router.register(r'notificaciones', NotificacionViewSet)

urlpatterns = router.urls
