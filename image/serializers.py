from rest_framework import serializers


class imageSerializer(serializers.Serializer):
    image = serializers.ImageField()
    text = serializers.CharField()

class prompSerializer(serializers.Serializer):
    text = serializers.CharField()

class fileSerializer(serializers.Serializer):
    video = serializers.FileField()