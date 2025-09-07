from rest_framework import viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from users.models import Users
from .serializers import UsersSerializer, UserSignupSerializer, UserLoginSerializer, ForgotPasswordSerializer, VerifyCodeSerializer, ResetPasswordSerializer

from django.core.mail import send_mail
from django.conf import settings
import random
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model
User = get_user_model()

otp_storage = {}


class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

class UserSignupView(CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSignupSerializer

class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)  # create authenticated session

        return Response({"detail": "User logged in successfully."}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP
        otp = str(random.randint(1000, 9999))
        otp_storage[email] = otp  # Save OTP, add expiry logic as needed

        # Send OTP to email (use your email config)
        send_mail(
            'Your OTP for password reset',
            f'Your OTP is {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response({"detail": "OTP sent to your email."})


class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        # Validate OTP
        if otp_storage.get(email) != otp:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
        # OTP verified
        return Response({"detail": "OTP verified."})


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Reset password
        user.set_password(password)
        user.save()

        # Remove OTP after successful reset if stored
        otp_storage.pop(email, None)
        return Response({"detail": "Password reset successful."})





