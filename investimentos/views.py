from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from clients.models import Client
from rest_framework.response import Response
from .serializers import SerializerEmailClient, SerializerClasseAtivo
from .models import ClasseAtivo


def calculo_reserva_de_emergencia(salario:float):
    salario *= 3
    return salario


class IndicaCarteiraView(APIView):
    serializer_class = (SerializerEmailClient)      

    def post(self, request):
        data = SerializerEmailClient(data = request.data)
        data.is_valid(raise_exception=True)
        client = Client.objects.get(email = data.validated_data['email'])
        print(client)
        if client.tipo_de_investidor == "Conservador":
            if client.reserva_de_emergencia == False:
                reserva_de_emergencia = calculo_reserva_de_emergencia(client.valor_armazenado_reserva_emergencia)
                return Response({'msg': f'Voce precisa de uma reserva de emergencia. O valor ideal é de {reserva_de_emergencia}'})



class ClasseAtivoView(ModelViewSet):
    queryset = ClasseAtivo.objects.all()
    serializer_class = SerializerClasseAtivo
            
