from rest_framework.routers import DefaultRouter
from .views import GastoViewSet, TipoGastoViewSet

router = DefaultRouter()
router.register(r'gastos', GastoViewSet)
router.register(r'tipos-gasto', TipoGastoViewSet)

urlpatterns = router.urls
