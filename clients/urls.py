from rest_framework.routers import DefaultRouter
from .views import ClientViewset
from django.urls import path
from .views import AgenteConservadorView, AgenteModeradoView, AgenteAvancadoView

router = DefaultRouter()
router.register('clients', ClientViewset)

urlpatterns = [
    path('agente-conservador/', AgenteConservadorView.as_view()),
    path('agente-moderado/', AgenteModeradoView.as_view()),
    path('agente-avancado/', AgenteAvancadoView.as_view())
]

urlpatterns += router.urls