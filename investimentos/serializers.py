from rest_framework.serializers import Serializer, ModelSerializer, EmailField
from .models import ClasseAtivo



class SerializerEmailClient(Serializer):
    email = EmailField()


class SerializerClasseAtivo(ModelSerializer):
    class Meta:
        model = ClasseAtivo
        fields = '__all__'
