from rest_framework.decorators import api_view
import os
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from .serializers import imageSerializer, prompSerializer, fileSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
import io
import google.generativeai as genai
from django.conf import settings
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_serializer, inline_serializer
from drf_spectacular.types import OpenApiTypes
import re
import json
from django.http import HttpResponseRedirect, HttpResponse
genai.configure(api_key=settings.API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

PROMPT_PRIMING = 'You are an expert Frontend developer, your HTML,JavaScript,CSS code is thorough, easily human readable and and up to date . You only provide the code without any additional information and remove markdown formatting.'

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    # HarmCategory.HARM_CATEGORY_UNSPECIFIED:HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
}

code = {
    "index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Snake Game</title>\n    <link rel=\"stylesheet\" href=\"style.css\">\n</head>\n<body>\n    <h1>Snake</h1>\n    <canvas id=\"gameCanvas\" width=\"400\" height=\"400\"></canvas>\n    <script src=\"script.js\"></script>\n</body>\n</html>",
    "style.css": "body {\n    background-color: #333;\n    display: flex;\n    flex-direction: column;\n    align-items: center;\n    justify-content: center;\n    height: 100vh;\n    margin: 0;\n}\n\ncanvas {\n    background-color: #000;\n    border: 4px solid #fff;\n}\n\nh1{\n    color: #fff;\n}",
    "script.js": "const canvas = document.getElementById('gameCanvas');\nconst ctx = canvas.getContext('2d');\n\nconst gridSize = 20;\nlet snake = [\n    { x: 10, y: 10 }\n];\nlet food = {};\nlet direction = 'right';\nlet score = 0;\n\nfunction generateFood() {\n    food = {\n        x: Math.floor(Math.random() * (canvas.width / gridSize)),\n        y: Math.floor(Math.random() * (canvas.height / gridSize))\n    };\n}\n\nfunction draw() {\n    ctx.clearRect(0, 0, canvas.width, canvas.height);\n\n    for (let i = 0; i < snake.length; i++) {\n        ctx.fillStyle = i === 0 ? 'green' : 'lime';\n        ctx.fillRect(snake[i].x * gridSize, snake[i].y * gridSize, gridSize, gridSize);\n    }\n\n    ctx.fillStyle = 'red';\n    ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize, gridSize);\n}\n\nfunction update() {\n    const head = { x: snake[0].x, y: snake[0].y };\n\n    switch (direction) {\n        case 'up': head.y--; break;\n        case 'down': head.y++; break;\n        case 'left': head.x--; break;\n        case 'right': head.x++; break;\n    }\n\n    if (head.x === food.x && head.y === food.y) {\n        score++;\n        generateFood();\n    } else {\n        snake.pop();\n    }\n\n    snake.unshift(head);\n\n    if (head.x < 0 || head.x >= canvas.width / gridSize || head.y < 0 || head.y >= canvas.height / gridSize || checkCollision(head)) {\n        alert('Game Over! Score: ' + score);\n        resetGame();\n    }\n\n    draw();\n}\n\nfunction checkCollision(head) {\n    for (let i = 1; i < snake.length; i++) {\n        if (head.x === snake[i].x && head.y === snake[i].y) {\n            return true;\n        }\n    }\n    return false;\n}\n\nfunction resetGame() {\n    snake = [{ x: 10, y: 10 }];\n    direction = 'right';\n    score = 0;\n    generateFood();\n}\n\ndocument.addEventListener('keydown', e => {\n    switch (e.key) {\n        case 'ArrowUp': if (direction !== 'down') direction = 'up'; break;\n        case 'ArrowDown': if (direction !== 'up') direction = 'down'; break;\n        case 'ArrowLeft': if (direction !== 'right') direction = 'left'; break;\n        case 'ArrowRight': if (direction !== 'left') direction = 'right'; break;\n    }\n});\n\ngenerateFood();\nsetInterval(update, 100);"
}

context = """
question/prompt:
Create a simple webpage with HTML, CSS, and JavaScript that displays a heading and a button, where clicking the button changes the heading's text and color.

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
"""


@extend_schema(
    request=prompSerializer,
    responses=None)
class prompt(APIView):
    def post(self, request, format=None):
        serializer = prompSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            mainPrompt = serializer.validated_data["text"]
            fullprompt = context + mainPrompt
            response = model.generate_content(
                fullprompt, safety_settings=safety_settings)
            result = response.text
            pattern = r"\\\n"
            print(result)
            # cleaned = re.sub(pattern, '\\n', result)
            cleaned = result.lstrip("```json").rstrip("```")
            json_data = json.loads(cleaned)
            print(json_data)
            # print(response.candidates[0].content)
            return Response(json_data)


@extend_schema(
    request=imageSerializer,
    responses=None
)
class pixel (APIView):
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, format=None):
        serializer = imageSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            image_file = serializer.validated_data['image']
            prompt = serializer.validated_data['text']
            image = Image.open(image_file)
            fullPrompt = PROMPT_PRIMING+prompt
            # response = model.generate_content([image,f'generate me the code for the same design animation for the button when i press it' ],
            response = model.generate_content([image, fullPrompt])
            # response = model.generate_content([image,f'give the name and estimate of how much calories and all the macro and micro nutrients  are in food given in the image baded on guessed weight' ],
            # response = model.generate_content([image,"give me rough estimate of the body fats and height in cm of the person in the image just give me the guess range without any other talk return the response as this ex. {height:70 cm,fats:10%} don't return the \\n "],

            return Response(response.text)


class VideoDesign(APIView):
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, format=None):
        serializer = fileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            video = serializer.validated_data['video']
            save_path = os.path.join(settings.MEDIA_ROOT, 'videos', video.name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb+') as destination:
                for chunk in video.chunks():
                    destination.write(chunk)
            video_file = genai.upload_file(path=save_path)
            history = ["image", "explain this please"]
            history[0] = video_file
            print(history)
            response = model.generate_content(history,
                                              safety_settings=safety_settings)
            return Response(response.text)


@extend_schema(
    summary="Get Code1 for test purposes ",
    description="This endpoint returns a dictionary with a key named code and value is embedded/inline format of html code.",
    responses={200: dict},  # specify response type
)
@api_view(["GET"])
def Code1(request):
    code1 = {
        "code": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Vision Login</title>\n    <link rel=\"stylesheet\" href=\"style.css\">\n<style>body {\n    font-family: sans-serif;\n    background-color: #222;\n    color: #fff;\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    min-height: 100vh;\n    margin: 0;\n}\n\n.container {\n    background-color: #333;\n    padding: 40px;\n    border-radius: 5px;\n    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);\n    text-align: center;\n}\n\nh1 {\n    color: #fff;\n    margin-bottom: 20px;\n}\n\n.form-group {\n    margin-bottom: 20px;\n}\n\nlabel {\n    display: block;\n    margin-bottom: 5px;\n    font-weight: bold;\n}\n\ninput {\n    width: 100%;\n    padding: 10px;\n    border: 1px solid #ccc;\n    border-radius: 3px;\n    box-sizing: border-box;\n}\n\nbutton {\n    background-color: #4CAF50;\n    color: white;\n    padding: 12px 20px;\n    border: none;\n    border-radius: 3px;\n    cursor: pointer;\n    width: 100%;\n}\n\nbutton:hover {\n    background-color: #45a049;\n}</style></head>\n<body>\n    <div class=\"container\">\n        <h1>Vision</h1>\n        <p>image to code</p>\n        <p>powered by Gemini</p>\n        <form id=\"loginForm\">\n            <div class=\"form-group\">\n                <label for=\"email\">Email:</label>\n                <input type=\"email\" id=\"email\" name=\"email\" required>\n            </div>\n            <div class=\"form-group\">\n                <label for=\"password\">Password:</label>\n                <input type=\"password\" id=\"password\" name=\"password\" required>\n            </div>\n            <button type=\"submit\">Login</button>\n        </form>\n    </div>\n    <script src=\"script.js\"></script>\n<script>const loginForm = document.getElementById('loginForm');\n\nloginForm.addEventListener('submit', (event) => {\n    event.preventDefault();\n    const email = document.getElementById('email').value;\n    const password = document.getElementById('password').value;\n\n    fetch('http://localhost:8000/auth/login/', {\n        method: 'POST',\n        headers: {\n            'Content-Type': 'application/json'\n        },\n        body: JSON.stringify({ email, password })\n    })\n    .then(response => response.json())\n    .then(data => {\n        console.log(data);\n        // Handle login success or failure based on data\n    })\n    .catch(error => {\n        console.error('Error:', error);\n        // Handle login error\n    });\n});\n</script></body>\n</html>"
    }
    return Response(code1)


@extend_schema(
    summary="Get Code2 for test purposes",
    description="This endpoint returns a dictionary of html and style and script as keys and its values are the their code .",
    responses={200: inline_serializer("code2", {"index.html": serializers.CharField(
    ), "styles.css": serializers.CharField(), "script.js": serializers.CharField()})}
)
@api_view(["GET"])
def Code2(request):
    code2 = {
        "index.html": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>Dynamic Page</title>\n    <link rel=\"stylesheet\" href=\"styles.css\">\n</head>\n<body>\n    <div id=\"page-container\">\n        <h1 id=\"page-title\"></h1>\n        <img id=\"page-image\" src=\"\" alt=\"\">\n        <p id=\"page-description\"></p>\n    </div>\n    \n    <script src=\"script.js\"></script>\n</body>\n</html>",
        "styles.css": "body {\n    font-family: Arial, sans-serif;\n    background-color: #f4f4f4;\n    margin: 0;\n    padding: 0;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    min-height: 100vh;\n}\n\n#page-container {\n    background-color: #fff;\n    padding: 30px;\n    border-radius: 8px;\n    text-align: center;\n}\n\n#page-image {\n    max-width: 100%;\n    height: auto;\n    margin-top: 20px;\n}",
        "script.js": "const pageTitle = prompt(\"Enter the page title:\", \"My Awesome Page\");\nconst pageDescription = prompt(\"Enter the page description:\", \"This is a cool page!\");\nconst pageImageURL = prompt(\"Enter the image URL:\", \"https://via.placeholder.com/600x400\");\n\ndocument.getElementById('page-title').innerText = pageTitle;\ndocument.getElementById('page-description').innerText = pageDescription;\ndocument.getElementById('page-image').src = pageImageURL;"}
    return Response(code2)
