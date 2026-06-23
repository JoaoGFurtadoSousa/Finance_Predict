from rest_framework.serializers import Serializer, EmailField


class SerializerEmailClient(Serializer):
    email = EmailField()

    