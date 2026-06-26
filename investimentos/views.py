from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from clients.models import Client
from rest_framework.response import Response
from .serializers import SerializerEmailClient, SerializerClasseAtivo
from .models import ClasseAtivo
from .agents.agente_conservador import agente_conservador
from .agents.agente_moderado import agente_moderado
from .agents.agente_agressivo import agente_agressivo
from .services.functions import calculo_reserva_de_emergencia



class IndicaCarteiraView(APIView):
    serializer_class = (SerializerEmailClient)      

    def post(self, request):
        data = SerializerEmailClient(data = request.data)
        data.is_valid(raise_exception=True)
        client = Client.objects.get(email = data.validated_data['email'])
        print(client.tipo_de_investidor)
        if client.reserva_de_emergencia == False:
            reserva_de_emergencia = calculo_reserva_de_emergencia(client.valor_armazenado_reserva_emergencia)
            return Response({'msg': f'Voce precisa de uma reserva de emergencia. O valor ideal é de {reserva_de_emergencia}'})
        
        if client.tipo_de_investidor == "Conservador":
            response = agente_conservador(client)
            return Response({'msg': response})
        elif client.tipo_de_investidor == "Moderado":
             response = agente_moderado(client)
             return Response({'msg': response})
        else:
            response = agente_agressivo(client)
            return Response({'msg': response})
            



class ClasseAtivoView(ModelViewSet):
    queryset = ClasseAtivo.objects.all()
    serializer_class = SerializerClasseAtivo
            
