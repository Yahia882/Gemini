from rest_framework import serializers


class imageSerializer(serializers.Serializer):
    image = serializers.ImageField()

class prompSerializer(serializers.Serializer):
    text = serializers.CharField()