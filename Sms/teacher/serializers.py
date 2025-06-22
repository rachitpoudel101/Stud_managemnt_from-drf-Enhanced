from rest_framework import serializers
from teacher.models import Assignment, Subject
from user.models import User

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'name', 'teacher', 'teacher_name']
        read_only_fields = ['teacher_name']

class AssignmentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    subject_name = serializers.ReadOnlyField(source='subject.name')
    
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'created_at', 'created_by', 
                  'created_by_name', 'file', 'due_date', 'subject', 'subject_name',
                  'remarks', 'audience', 'published']
        read_only_fields = ['created_by', 'created_at']