from django.urls import path
from .views import IndicaCarteiraView, ClasseAtivoView, InvestimentosView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'classe-ativos', ClasseAtivoView)
router.register(r'investimentos', InvestimentosView)



urlpatterns = [
    path('indica-carteira/', IndicaCarteiraView.as_view(), name='indica-carteira'),
]

urlpatterns += router.urls