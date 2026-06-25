from rest_framework.serializers import Serializer, ModelSerializer, EmailField
from .models import ClasseAtivo, Investimento



class SerializerEmailClient(Serializer):
    email = EmailField()


class SerializerClasseAtivo(ModelSerializer):
    class Meta:
        model = ClasseAtivo
        fields = '__all__'


class SerializerInvestimento(ModelSerializer):
    class Meta:
        model = Investimento
        fields = '__all__'
