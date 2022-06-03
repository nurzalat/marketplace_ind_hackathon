from django.contrib.auth.views import LogoutView
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView

from . import serializers
from .send_email import send_confirmation_email, send_reset_passwor_email
# from .tasks import send_activation_email

User = get_user_model()


class StandardPaginationClass(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SellerListView(ListAPIView):
    queryset = User.objects.filter(is_staff=True, is_superuser=False)
    serializer_class = serializers.SellerListSerializer
    pagination_class = StandardPaginationClass


class SellerDetailView(RetrieveAPIView):
    queryset = User.objects.filter(is_staff=True, is_superuser=False)
    serializer_class = serializers.SellerDetailedSerializer


class SellerRegistrationApiView(APIView):
    def post(self, request):
        serializer = serializers.ManagerRegisterApiSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            if user:
                send_confirmation_email(user)
                # send_activation_email.delay(user.email)
            return Response('Check your mail, you will receive email with link for activation of your account.\n'
                            'Thanks for choosing us!', status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomerRegistrationApiView(APIView):
    def post(self, request):
        serializer = serializers.CustomerRegisterApiSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            if user:
                send_confirmation_email(user)
                # send_activation_email.delay(user.email)
            return Response('Check your mail, you will receive email with link for activation of your account.\n'
                            'Thanks for choosing us!', status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ActivationView(APIView):
    def get(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ''
            user.save()
            return Response({'msg': 'Successfully activated'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg': 'Link expired'}, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(TokenObtainPairView):
    serializer_class = serializers.LoginSerializer


class NewPasswordView(APIView):
    def post(self, request):
        serializer = serializers.CreateNewPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Password changed')


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = serializers.PasswordResetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(email=serializer.data.get('email'))
            user.create_activation_code()
            user.save()
            send_reset_passwor_email(user)
            return Response('Check your email')


class LogoutApiView(GenericAPIView):
    serializer_class = serializers.LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Successfully logged out.', status=status.HTTP_204_NO_CONTENT)
