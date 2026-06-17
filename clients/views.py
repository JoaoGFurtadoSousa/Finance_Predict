from rest_framework.viewsets import ModelViewSet
from .models import Client
from .serializers import ClientSerializer


class ClientViewset(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    
