from rest_framework.routers import DefaultRouter
from .views import EmpleadoViewSet, CargoEmpleadoViewSet, EmpresaExternaViewSet

router = DefaultRouter()
router.register(r'empleados', EmpleadoViewSet)
router.register(r'cargos-empleado', CargoEmpleadoViewSet)
router.register(r'empresas-externas', EmpresaExternaViewSet)

urlpatterns = router.urls
