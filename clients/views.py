import logging

from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework import serializers
from rest_framework.exceptions import Throttled
from rest_framework.viewsets import ModelViewSet
from investimentos.serializers import SerializerEmailClient

from core.guardrails.exceptions import SecurityViolation
from core.guardrails.security import validate_payload_security

from .models import Client
from .serializers import ClientSerializer
from investimentos.agents.agente_conservador import agente_conservador
from investimentos.agents.agente_moderado import agente_moderado
from investimentos.agents.agente_agressivo import agente_agressivo
from rest_framework.response import Response


logger = logging.getLogger("validation_guardrails")


@method_decorator(
    ratelimit(key="ip", rate="10/m", method="POST", block=False),
    name="dispatch",
)
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
        


    
    def initial(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            raise Throttled(
                detail="Limite de requisições excedido. Tente novamente em breve."
            )
        if request.method in {"POST", "PUT", "PATCH"} and isinstance(
            request.data, dict
        ):
            try:
                validate_payload_security(
                    request.data,
                    fields=ClientSerializer.SECURITY_FIELDS,
                )
            except SecurityViolation as exc:
                raise serializers.ValidationError(
                    {exc.field or "non_field_errors": exc.message}
                ) from exc
        return super().initial(request, *args, **kwargs)
