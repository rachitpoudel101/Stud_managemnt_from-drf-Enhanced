from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, notice
from teacher.models import Subject

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
        queryset=Subject.objects.all(), many=True, required=False
    )

    class Meta:
        model = User  # or your custom user model
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'role', 'subjects']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        subjects = validated_data.pop('subjects', [])
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        
        # If user is a teacher, update the teacher field on subjects
        if user.role == 'teacher' and subjects:
            Subject.objects.filter(id__in=[s.id for s in subjects]).update(teacher=user)
            
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