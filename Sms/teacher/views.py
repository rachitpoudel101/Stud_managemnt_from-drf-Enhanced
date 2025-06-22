from rest_framework import status
from rest_framework.response import Response
from student.models import StudentProfile
from user import models, permissions, serializers
from teacher.models import Assignment, Subject
from user.permissions import IsAdmin, IsTeacher, IsTeacherOrAdmin
from rest_framework.decorators import action
from rest_framework import viewsets
from teacher.serializers import AssignmentSerializer, SubjectSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            # Only admins can create or delete subjects
            return [IsAdmin()]
        if self.action in ['update', 'partial_update']:
            # Only teachers or admins can update subjects
            return [permissions.IsAuthenticated() & (IsTeacher() | IsAdmin())]
        # Anyone authenticated can view subjects
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'], url_path='unassigned')
    def unassigned_subjects(self, request):
        # Get all subjects without a teacher or with null teacher
        unassigned = Subject.objects.filter(teacher__isnull=True)
        serializer = self.get_serializer(unassigned, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my-subjects')
    def my_subjects(self, request):
        """Get subjects assigned to the current teacher"""
        user = request.user
        if user.role != 'teacher':
            return Response(
                {"error": "Only teachers can access their subjects"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        subjects = Subject.objects.filter(teacher=user)
        serializer = self.get_serializer(subjects, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Don't assign a teacher when creating a subject through the API
        serializer.save(teacher=None)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Subject.objects.none()
            
        if user.role == 'teacher':
            return Subject.objects.filter(teacher=user)
        # Admin can see all subjects
        return Subject.objects.all()
    
class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Assignment.objects.none()
            
        if user.role == 'student':
            # Students can see assignments for subjects they're enrolled in AND published assignments
            try:
                student_profile = StudentProfile.objects.get(user=user)
                # Get student's enrolled subjects
                student_subjects = student_profile.subjects.all()
                
                return Assignment.objects.filter(
                    subject__in=student_subjects,
                    published=True
                ).distinct()
            except StudentProfile.DoesNotExist:
                return Assignment.objects.none()
                
        elif user.role == 'teacher':
            # Teachers can see assignments they created or for subjects they teach
            return Assignment.objects.filter(
                models.Q(created_by=user) | models.Q(subject__teacher=user)
            ).distinct()
        # Admin can see all assignments
        return Assignment.objects.all()
        
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        user = self.request.user
        assignment = self.get_object()
        
        # Check permissions for updating assignments
        if user.role == 'admin':
            # Admin can edit any assignment
            pass
        elif user.role == 'teacher':
            # Teachers can only edit assignments they created
            if assignment.created_by != user:
                raise serializers.ValidationError("You can only edit assignments that you created")
        else:
            raise serializers.ValidationError("You don't have permission to edit assignments")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        user = self.request.user
        assignment = instance
        
        print(f"Delete request from user: {user.username} (ID: {user.id}, Role: {user.role})")
        print(f"Assignment created by: {assignment.created_by.username} (ID: {assignment.created_by.id})")
        
        # Check permissions for deleting assignments
        if user.role == 'admin':
            # Admin can delete any assignment
            print("Admin permission granted for delete")
            pass
        elif user.role == 'teacher':
            # Teachers can only delete assignments they created
            if assignment.created_by != user:
                print(f"Teacher permission denied: {assignment.created_by.id} != {user.id}")
                raise serializers.ValidationError("You can only delete assignments that you created")
            print("Teacher permission granted for delete")
        else:
            print("No delete permission")
            raise serializers.ValidationError("You don't have permission to delete assignments")
        
        # Delete the assignment
        assignment.delete()
