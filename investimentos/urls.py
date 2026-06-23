from django.urls import path
from .views import IndicaCarteiraView

urlpatterns = [
    path('indica-carteira/', IndicaCarteiraView.as_view(), name='indica-carteira'),
]