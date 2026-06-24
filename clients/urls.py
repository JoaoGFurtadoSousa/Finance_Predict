from rest_framework.routers import DefaultRouter
from .views import ClientViewset
from django.urls import path
from .views import AgenteConservadorView

router = DefaultRouter()
router.register('clients', ClientViewset)

urlpatterns = [
    path('agente-conservador/', AgenteConservadorView.as_view())
]

urlpatterns += router.urls