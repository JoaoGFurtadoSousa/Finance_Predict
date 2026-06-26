from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from core.guardrails.exceptions import SecurityViolation
from core.guardrails.sanitizers import sanitize_payload
from core.guardrails.security import validate_payload_security
from core.guardrails.validators import normalize_cpf

from .guardrails import GuardrailViolation, InvestmentGuardrails
from .models import Client


class ClientSerializer(ModelSerializer):
    SECURITY_FIELDS = {"nome", "email", "preocupacao_atual"}

    def to_internal_value(self, data):
        allowed_fields = {
            field_name
            for field_name, field in self.fields.items()
            if not field.read_only
        }
        unexpected = set(data.keys()) - allowed_fields
        if unexpected:
            field = sorted(unexpected)[0]
            raise serializers.ValidationError(
                {field: "Campo não permitido no payload."}
            )

        protected = sanitize_payload(dict(data))
        if "cpf" in protected:
            protected["cpf"] = normalize_cpf(protected["cpf"])
        try:
            validate_payload_security(protected, self.SECURITY_FIELDS)
        except SecurityViolation as exc:
            raise serializers.ValidationError(
                {exc.field or "non_field_errors": exc.message}
            ) from exc
        return super().to_internal_value(protected)

    def validate(self, attrs):
        try:
            protected = InvestmentGuardrails().process_input(
                attrs,
                pii_excluded_fields={"cpf", "email", "nome"},
            )
        except GuardrailViolation as exc:
            field = exc.details.get("field", "non_field_errors")
            raise serializers.ValidationError({field: exc.message}) from exc

        values = {}
        if self.instance is not None:
            values.update(
                {
                    field.name: getattr(self.instance, field.name)
                    for field in Client._meta.fields
                    if field.name != "id"
                }
            )
        values.update(protected)
        candidate = Client(**values)
        try:
            candidate.clean()
        except SecurityViolation as exc:
            raise serializers.ValidationError(
                {exc.field or "non_field_errors": exc.message}
            ) from exc
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            ) from exc
        return super().validate(protected)

    class Meta:
        model = Client
        fields = "__all__"
        read_only_fields = ("id", "tipo_de_investidor", "perfil_sintetico")
