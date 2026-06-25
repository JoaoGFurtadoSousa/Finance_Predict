from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import serializers
from rest_framework.exceptions import Throttled
from rest_framework.viewsets import ModelViewSet

from core.guardrails.exceptions import SecurityViolation
from core.guardrails.security import validate_payload_security

from .models import Client
from .serializers import ClientSerializer


@method_decorator(
    ratelimit(key="ip", rate="10/m", method="POST", block=False),
    name="dispatch",
)
class ClientViewset(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

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
