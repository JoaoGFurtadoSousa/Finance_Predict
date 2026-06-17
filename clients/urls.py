from rest_framework.routers import DefaultRouter
from .views import ClientViewset


router = DefaultRouter()
router.register('clients', ClientViewset)

urlpatterns = router.urls