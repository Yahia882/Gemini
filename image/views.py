from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import imageSerializer, prompSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
import io
import google.generativeai as genai
from django.conf import settings
from google.generativeai.types import HarmCategory, HarmBlockThreshold

genai.configure(api_key=settings.API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')


class prompt (APIView):
    def post(self, request, format=None):

        serializer = prompSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            text = serializer.validated_data["text"]
            response = model.generate_content(text)
            return Response(response.text)


class pixel (APIView):
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, format=None):
        serializer = imageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            image_file = serializer.validated_data['image']
            image = Image.open(image_file)
            #response = model.generate_content([image,f'Example Formula for Men: Body fat % = 86.010 * log10(waist - neck) - 70.041 * log10(height) + 36.76 using this formula and img do an estimate of the body fat assuming the waist: 34 inches, Neck: 16 inches, Height: 70 and Hip: 38 inches inches just give me the result of this formula ' ],
            response = model.generate_content([image,"give me rough estimate of the body fats of the person in the image just a guess just give me the guess range without any other talk"],
            safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        #HarmCategory.HARM_CATEGORY_UNSPECIFIED:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:HarmBlockThreshold.BLOCK_NONE,
    })
            return Response(response.text)
