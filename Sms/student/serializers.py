from rest_framework import serializers
from student.models import Marks, StudentProfile, StudentSubmission
from teacher.serializers import SubjectSerializer, UserBasicSerializer
from teacher.models import Subject
from user.models import User

class MarksSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    student_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Marks
        fields = ['id', 'student', 'subject', 'marks', 'published', 'subject_name', 'student_name']
        
    def get_student_name(self, obj):
        user = obj.student.user
        return f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username

class StudentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.user.username')
    assignment_title = serializers.ReadOnlyField(source='assignment.title')
    
    class Meta:
        model = StudentSubmission
        fields = ['id', 'assignment', 'assignment_title', 'student', 
                  'student_name', 'file', 'submitted_at', 'comments']
        read_only_fields = ['student', 'submitted_at', 'student_name', 'assignment_title']
    
    def update(self, instance, validated_data):
        # Handle file updates carefully - only update if a new file is provided
        if 'file' in validated_data and validated_data['file'] is not None:
            instance.file = validated_data['file']
        
        # Update other fields
        instance.comments = validated_data.get('comments', instance.comments)
        instance.save()
        return instance
    
class StudentProfileSerializer(serializers.ModelSerializer):
    user_details = UserBasicSerializer(source='user', read_only=True)
    subject_details = SubjectSerializer(source='subjects', many=True, read_only=True)
    grade_display = serializers.CharField(source='get_grade_display', read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    subjects = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'user_details', 'username', 'email', 'education_level', 'grade', 'grade_display', 'subjects', 'subject_details']
        extra_kwargs = {
            'user': {'write_only': True}
        }
    
    def create(self, validated_data):
        subjects = validated_data.pop('subjects', [])
        profile = StudentProfile.objects.create(**validated_data)
        if subjects:
            profile.subjects.set(subjects)
        return profile
        
    def update(self, instance, validated_data):
        subjects = validated_data.pop('subjects', None)
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update subjects if provided
        if subjects is not None:
            instance.subjects.set(subjects)
        return instance
