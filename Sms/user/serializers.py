from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, notice
from student.models import Subject

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Use the parent class's validate method to authenticate the user
        data = super().validate(attrs)
        
        # Prevent login if user is soft deleted
        if self.user.is_deleted:
            raise serializers.ValidationError(_("This account has been deleted. Please contact admin."))
        
        # Get the refresh and access tokens
        refresh = self.get_token(self.user)
        
        # Add the tokens to the response
        data['access'] = str(refresh.access_token)
        data['refresh'] = str(refresh)
        
        # Add user data to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role
        }
        
        return data

class UserSerializer(serializers.ModelSerializer):
    subjects = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=Subject.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'role', 'subjects']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        # Remove subjects field from validated_data if it exists
        subjects = validated_data.pop('subjects', None)
        
        # Create the user
        user = User.objects.create_user(**validated_data)
        
        # The subjects will be handled in the view
        return user

class NoticeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = notice
        fields = ['id', 'title', 'content', 'created_at', 'created_by', 'updated_at', 'published', 'audience', 'created_by_name']
        read_only_fields = ['created_by']
        
    def get_created_by_name(self, obj):
        user = obj.created_by
        return f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username