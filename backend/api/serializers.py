from users.models import Users
from rest_framework import serializers
from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator


class UsersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Users
        fields = ['id', 'name', 'image', 'email', 'phone_number', 'user_type', 'created_at', 'updated_at']


class UserSignupSerializer(serializers.ModelSerializer):
  username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=Users.objects.all())]
    )
    
  class Meta:
        model = Users
        fields = ['username', 'email', 'name', 'phone_number', 'user_type', 'password']
        extra_kwargs = {'password': {'write_only': True}}
  def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')
        user = Users(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        User = get_user_model()
        user = authenticate(username=email, password=password)
        if user is None:
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password.")
            if not user_obj.check_password(password):
                raise serializers.ValidationError("Invalid email or password.")
            user = user_obj
        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
 

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs