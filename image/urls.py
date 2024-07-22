from django.urls import path
from .views import pixel ,prompt
urlpatterns = [
    path("describe/",pixel.as_view()),
    path("prompt/",prompt.as_view()),
]
