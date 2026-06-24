from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .guardrails import GuardrailViolation, InvestmentGuardrails
from .models import Client


class ClientSerializer(ModelSerializer):
    def validate(self, attrs):
        """
        Protege o payload sem alterar campos estruturados necessários ao CRUD.

        CPF e e-mail são mantidos porque fazem parte do contrato atual; PII
        inserida no campo narrativo ``preocupacao_atual`` é anonimizada.
        """
        try:
            protected = InvestmentGuardrails().process_input(
                attrs,
                pii_excluded_fields={
                    "cpf",
                    "email",
                    "nome",
                },
            )
        except GuardrailViolation as exc:
            raise serializers.ValidationError(exc.as_dict()) from exc
        return super().validate(protected)

    class Meta:
        model = Client
        fields = '__all__'
