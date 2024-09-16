from rest_framework.response import Response
from rest_framework import fields
from rest_framework import status, serializers
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import webAppserializer, pageSerializer, functionSerializer, createpageSerializer, currentPageserializer
from .models import webApp, Profile
from PIL import Image
import google.generativeai as genai
import json
from django.shortcuts import get_object_or_404
from django.conf import settings
from image.serializers import prompSerializer
import re
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
User = get_user_model()
PROMPT_PRIMING = 'You are an expert Frontend developer, your HTML,JavaScript,CSS code is thorough, easily human readable and and up to date . You only provide the code without any additional information and remove markdown formatting.'
context = """
question/prompt:
generate HTML, Javascript, and Css code for the image provided. name the key for HTML code index.html and JS code script.js and Css code style.css.

Answer
{"index.html":"<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Webpage</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1 id="title">Welcome to My Webpage</h1>
    <button onclick="changeText()">Click Me!</button>

    <script src="script.js"></script>
</body>
</html>",
"style.css":"body {
    font-family: Arial, sans-serif;
    background-color: #f0f0f0;
    text-align: center;
    padding: 50px;
}

",
"script.js":"function changeText() {
    const title = document.getElementById('title');
    title.textContent = "You clicked the button!";
    title.style.color = "#FF6347";  
"}



this a good example of how the code format should be returned 

retrun in JSON format
Do not add comment.
example 
function changeText() {
    const title = document.getElementById('title');
    title.textContent = "You clicked the button!";
    title.style.color = "#FF6347";
this is good example of answer that does not include comment just code

generate code for transfer html pages
example prompt: make that button transfer to example.html 
answer:
document.getElementById("button").onclick = function() {
            window.location.href = "page2.html"; // Replace with the relative path to your target page
        };
example prompt: after fetch operation handle the promise if successful to transfer to name.html page
try {
        const response = await fetch('http://localhost:8000/auth/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password, password2 })
        });

        if (response.ok) {
            // Handle successful signup, e.g., redirect to login page
            console.log('Signup successful!');
            function redirectToAnotherPage() {
            window.location.href = "name.html"; 
} 
        } else {
            const data = await response.json();
            console.error('Signup failed:', data.detail);
            // Handle error, e.g., display error message to the user
        }
    } catch (error) {
        console.error('Error during signup:', error);
        // Handle unexpected errors
    }
});

"""


genai.configure(api_key=settings.API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')


def add_html_extension(filename):
    if not filename.endswith('.html'):
        return filename + '.html'
    return filename


def pereviewCode(code, name):
    html_key = None
    for key in code.keys():
        print(key)
        if key.endswith("html"):
            html_key = key
            break
    html_code = code[html_key]
    head_end_index = html_code.find("</head>")
    if head_end_index != -1:
        combined_code = (
            html_code[:head_end_index] +
            f"<style>{code[f'{name}.css']}</style>" +
            html_code[head_end_index:]
        )
    body_end_index = combined_code.find("</body>")
    if body_end_index != -1:
        combined_code = (
            combined_code[:body_end_index] +
            f"<script>{code[f'{name}.js']}</script>" +
            combined_code[body_end_index:]
        )
    code_object = {}
    code_object["code"] = combined_code
    return combined_code


def clean(code):
    code = code.text
    code = code.lstrip("```json").rstrip("```")
    code = json.loads(code)
    return code


def functionprocessing(func):
    func_prompt = ""
    counter = 0
    for n in func:
        serializer = pageSerializer(data=n)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        header_prompt = ""
        note_prompt = ""
        header = validated_data.get("header")
        note = validated_data.get("note")
        if header:
            header_prompt = ", use {header}"
        if note:
            note_prompt = ", and  {note}"
        counter += 1
        func_prompt += f"""function number {counter} : I want to associate this function with {validated_data["pertian_to"]}, purpose of this function {validated_data["purpose"]}, use {validated_data["method"]} method,
         use "{validated_data["url"]}" {header_prompt} and body {validated_data["body"]}.
         {note_prompt}.
           """
    return func_prompt


class webAppCreate(CreateAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = webApp.objects.all()
    serializer_class = webAppserializer

    def perform_create(self, serializer):
        profile = get_object_or_404(Profile, user=self.request.user)
        new_instance = serializer.save(user=self.request.user)
        profile.currentWeb = new_instance
        profile.save()


class webAppDelete(DestroyAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = webApp.objects.all()
    serializer_class = webAppserializer

    def get_queryset(self):
        user = self.request.user
        return webApp.objects.filter(user=user)


class webAppUpdate(UpdateAPIView):
    permission_classes = [IsAuthenticated,]
    queryset = webApp.objects.all()
    serializer_class = webAppserializer

    def get_queryset(self):
        user = self.request.user
        return webApp.objects.filter(user=user)


class webAppList(ListAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = webAppserializer

    def get_queryset(self):
        user = self.request.user
        return webApp.objects.filter(user=user)


@extend_schema(
    description="""create a page, pass list of objects that contain the specs of the page.
    function_dictionary=[{"pertian to":"","purpose":"",}]""",
    request=functionSerializer(),
    responses=inline_serializer("success_page_retrieval2", {"code": serializers.CharField(
    ), "id": serializers.IntegerField(), "name": serializers.CharField()}),
    examples=[
        OpenApiExample("eaxmple",value = {"function_dictionary":"[{},{}]","image":"string($url)","name":"string"},request_only=True),
    ],
    
)
class createpage(APIView):
    permission_classes = [IsAuthenticated,]
    parser_classes = (FormParser, MultiPartParser)
    def post(self, request, **kwargs):
        id = kwargs.get('pk')
        instance = get_object_or_404(webApp, id=id)
        Mcode = instance.pages
        serializer = functionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        name = validated_data["name"]
        image = validated_data["image"]
        html_name = add_html_extension(name)
        image = Image.open(image)
        funcprompt = functionprocessing(validated_data["function_dictionary"])
        main_prompt = f"""generate HTML, Javascript, and Css code for the image provided.. name the key for HTML code {html_name} and JS code {name}.js and Css code {name}.css.
         add the following functionality:
         {funcprompt}
            """
        fullPrompt = context + main_prompt
        response = model.generate_content([image, fullPrompt], )
        code = clean(response)
        print(code)
        previewCode = pereviewCode(code, name=name)

        for key in code:
            Mcode[key] = code[key]
        instance.save()
        res = {"code": previewCode, "id": id, "name": name}
        return Response(res)


@extend_schema(
    description="List pages' name for the app with the id of the app",
    responses=inline_serializer(
        "list", {"pages": serializers.ListField(), "webApp_id": serializers.IntegerField()})
)
class ListPages(APIView):
    def get(self, request, **kwargs):
        id = kwargs.get('pk')
        instance = get_object_or_404(webApp, id=id)
        profile = get_object_or_404(Profile, user=request.user)
        profile.currentWeb = instance
        profile.save()
        pages = instance.pages
        html_keys = [key for key in pages.keys() if key.endswith('.html')]
        name_list = [key[:-5] for key in html_keys if key.endswith('.html')]
        res = {"pages": name_list, "webApp_id": id}
        return Response(res)


@extend_schema(
    description="get a specific page from the app with the id of the app and name of the page",
    responses=inline_serializer("success_page_retrieval", {"code": serializers.CharField(), "id": serializers.IntegerField(), "name": serializers.CharField()})
)
class retrievePage(APIView):
    def get(self, request, **kwargs):
        id = kwargs.get('pk')
        name = kwargs.get('name')
        Name = name + ".html"
        instance = get_object_or_404(webApp, id=id)
        pages = instance.pages
        if Name not in pages:
            return Response("there is no page with that name")
        print(pages)
        name_dict = {key: value for key,
                     value in pages.items() if key.startswith(name)}
        print(name_dict)
        previewcode = pereviewCode(code=name_dict, name=name)
        return Response({"code": previewcode, "id": id, "name": name})


@extend_schema(
    description="perform changes to the generated code",
    responses=inline_serializer("update", {"code": serializers.CharField(
    ), "id": serializers.IntegerField(), "name": serializers.CharField()})
)
class feedbackPage(APIView):
    serializer_class = prompSerializer()
    def put(self, request, **kwargs):
        id = kwargs.get('pk')
        name = kwargs.get('name')
        instance = get_object_or_404(webApp, id=id)
        pages = instance.pages
        name_dict = {key: value for key,
                     value in pages.items() if key.startswith(name)}
        serializer = prompSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feedback = serializer.validated_data["text"]
        # Code = json.dumps(name_dict)
        fullPrompt = f'{context}."do the following changes to this code {
            name_dict}. changes " {feedback}'
        response = model.generate_content(fullPrompt)
        code = clean(response)
        previewcode = pereviewCode(code, name=name)
        for key in code:
            pages[key] = code[key]
        instance.save()
        return Response({"code": previewcode, "id": id, "name": name})

@extend_schema(
    responses=inline_serializer("deletePage",{})
)
class deletePage(APIView):
    def delete(self, request, **kwargs):
        id = kwargs.get('pk')
        name = kwargs.get('name')
        instance = get_object_or_404(webApp, id=id)
        pages = instance.pages
        for key in list(pages.keys()):
            if key.startswith(name):
                del pages[key]
        instance.save()
        return Response({f"{name}": "Deleted"}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    description="profile",
    responses=inline_serializer("profile", {"username": serializers.CharField(
    ), "last_visited_app": serializers.IntegerField(), "avatar": serializers.ImageField()})
)
class profile(APIView):
    def get(self, request, **kwargs):
        instance = get_object_or_404(Profile, user=request.user)
        avatar = instance.avatar
        if not avatar:
            avatar = None
        currentWeb = instance.currentWeb.id
        if not currentWeb:
            currentWeb = None
        return Response({"username": instance.user.username, "avatar": avatar, "last_visited_app": currentWeb})


@extend_schema(
    description="fully customized input to create a page for the app with the id of the app",
    responses=inline_serializer("success_page_creation", {"code": serializers.CharField(
    ), "id": serializers.IntegerField(), "name": serializers.CharField()})
)
class createPageCustomizedInput(APIView):
    permission_classes = [IsAuthenticated,]
    parser_classes = (FormParser, MultiPartParser)
    serializer_class = createpageSerializer()

    def post(self, request, **kwargs):
        id = kwargs.get('pk')
        instance = get_object_or_404(webApp, id=id)
        pages = instance.pages
        serializer = createpageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        name = validated_data["name"]
        image = validated_data["image"]
        text = validated_data["text"]
        html_name = add_html_extension(name)
        image = Image.open(image)
        fullPrompt = PROMPT_PRIMING + text
        response = model.generate_content([image, fullPrompt], )
        code = {}
        code = response.text.lstrip("```html").rstrip("```")
        pages[html_name] = code
        print(code)
        instance.save()
        res = {"code": code, "id": id, "name": name}
        return Response(res)


# class currentpageview(APIView):
#     def post(self,request,*args, **kwargs):
#        instance = Pages(user = self.request.user)
#        pages = instance.currentpage
#        serializer = currentPageserializer(data=request.data)
#        serializer.is_valid(raise_exception=True)
#        validated_data = serializer.validated_data
#        image = validated_data["image"]
#        text = validated_data["text"]
#        image = Image.open(image)
#        fullPrompt =  PROMPT_PRIMING + text
#        response = model.generate_content([image,fullPrompt],)
#        code = {}
#        code =response.text.lstrip("```html").rstrip("```")
#        pages["index.html"]= code
#        print(code)
#        instance.save()
#        res = {"code":code,}
#        return Response(res)


class extension (APIView):
    @extend_schema(
    description= "get the last visited page by the user making the request (current Page)",
    responses={200:inline_serializer("extensionSerializer",{"index.html":serializers.CharField()})},
    examples=[OpenApiExample(
        "extension",
        value={"index.html":"code","index.js":"code","index.css":"code"}
        ,response_only= True
    ,)
    ]
)
    def get(self, request, *args, **kwargs):
        instance = get_object_or_404(Profile, user=request.user)
        try:
            pages = instance.currentWeb.pages
        except:
            pages  = None
        return Response(pages)
