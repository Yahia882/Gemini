from rest_framework.response import Response
from rest_framework import status,serializers
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import CreateAPIView
from drf_spectacular.utils import extend_schema , OpenApiParameter,inline_serializer,OpenApiExample

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
  permission_classes = (AllowAny,)
  serializer_class = UserRegistrationSerializer()
  @extend_schema(parameters = [
     UserRegistrationSerializer()
  ],
  responses={201:inline_serializer("successful_registration",{"access":serializers.CharField(),"refresh":serializers.CharField()})}
  )
  def post(self,request,format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = get_tokens_for_user(user)
    return Response(token,status=status.HTTP_201_CREATED)