from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import imageSerializer, prompSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
import io
import google.generativeai as genai
from django.conf import settings


genai.configure(api_key=settings.API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


class prompt (APIView):
    def post(self, request, format=None):
        serializer = prompSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            text = serializer.validated_data["text"]
            response = model.generate_content(text)
            return Response(response.text)
        # print(response.text)


class pixel (APIView):
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, format=None):
        serializer = imageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            image_file = serializer.validated_data['image']
            image = Image.open(image_file)
            response = model.generate_content(image)
            return Response(response.text)
