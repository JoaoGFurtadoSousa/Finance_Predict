from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from investimentos.serializers import SerializerEmailClient
from .models import Client
from .serializers import ClientSerializer
from investimentos.agents.agente_conservador import agente_conservador
from rest_framework.response import Response


class ClientViewset(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class AgenteConservadorView(APIView):

    def post(self, request):
        data = SerializerEmailClient(data = request.data)
        data.is_valid(raise_exception=True)
        client = Client.objects.get(email = data.validated_data['email'])
        response = agente_conservador(client)
        return Response({'msg':f'{response}'})

        


    