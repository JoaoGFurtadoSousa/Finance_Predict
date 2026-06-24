from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from investimentos.serializers import SerializerEmailClient
from .models import Client
from .serializers import ClientSerializer
from investimentos.agents.agente_conservador import agente_conservador
from investimentos.agents.agente_moderado import agente_moderado
from investimentos.agents.agente_agressivo import agente_agressivo
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


class AgenteModeradoView(APIView):

    def post(self, request):
        data = SerializerEmailClient(data = request.data)
        data.is_valid(raise_exception=True)
        client = Client.objects.get(email = data.validated_data['email'])
        response = agente_moderado(client)
        return Response({'msg':f'{response}'})
    

class AgenteAvancadoView(APIView):

    def post(self, request):
        data = SerializerEmailClient(data = request.data)
        data.is_valid(raise_exception=True)
        client = Client.objects.get(email = data.validated_data['email'])
        response = agente_agressivo(client)
        return Response({'msg':f'{response}'})
        


    