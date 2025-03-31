from rest_framework import views, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from core.api.serializers import AuthInputSerializer, AuthResponseSerializer
from core.auth.auth import match_auth_provider, auth_create_or_update_user
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import os


env = os.environ.get


class SocialAuthenticationView(ViewSet):
    authentication_classes = []
    permission_classes = []

    @action(methods=['POST'], detail=False, url_path="social", url_name="social-auth")
    def social_auth(self, request: Request) -> Response:
        input_serializer = AuthInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        provider = input_serializer.validated_data['provider']
        code = input_serializer.validated_data['code']
        # for later use
        # code_verifier = input_serializer.validated_data.get('code_verifier')
        try:
            auth_provider = match_auth_provider(provider)
            access_token = auth_provider.get_bearer(code)
            user_info = auth_provider.get_user_info(access_token)
            email = user_info.get('email')
            user = auth_create_or_update_user(email, user_info)
            refresh = RefreshToken.for_user(user)

            response_data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': f'{user.first_name} {user.last_name}'.strip()
                }
            }

            output_serializer = AuthResponseSerializer(data=response_data)
            output_serializer.is_valid(raise_exception=True)
            # temporary stuff
        except Exception as e:
            raise ParseError(detail=str(e))
        return Response(output_serializer.validated_data)



class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(data={
            "message": "Authentication successful!",
            "user_id": request.user.id,
            "email": request.user.email
        }, status=status.HTTP_200_OK)
