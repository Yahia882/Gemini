from rest_framework import serializers
from .models import webApp
from . import validators
class webAppserializer(serializers.ModelSerializer):
    
    name = serializers.CharField(required = True)
    class Meta:
        model = webApp
        fields = ["id","name"]


class pageSerializer(serializers.Serializer):
    
    pertian_to = serializers.CharField(max_length = 100,required = True)
    purpose = serializers.CharField(max_length = 100,required = True)
    method = serializers.CharField(validators=[validators.RequestMethodValidator],required = True)
    header = serializers.CharField(max_length = 100,required = False)
    body = serializers.CharField(required = True)
    note = serializers.CharField(max_length=300,required = False)
    url = serializers.CharField(validators=[validators.validate_url],required = True)
    


class functionSerializer(serializers.Serializer):
    function_dictionary = serializers.JSONField(required = True,validators=[validators.validateListOfObjects]) 
    image = serializers.ImageField(required = True)
    name = serializers.CharField(validators=[validators.validate_single_word],required = True)


class createpageSerializer(serializers.Serializer):
    image = serializers.ImageField(required = True)
    name = serializers.CharField(validators=[validators.validate_single_word],required = True)
    text = serializers.CharField(required = True)

class currentPageserializer(serializers.Serializer):  #just for Gemini competition demo the app is still in progress
    text = serializers.CharField(required = True)
    image = serializers.ImageField(required = True)