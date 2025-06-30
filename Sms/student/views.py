from rest_framework import status
from rest_framework.response import Response
from teacher.models import Subject
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from student.models import Marks, StudentProfile, StudentSubmission
from student.serializers import MarksSerializer, StudentSubmissionSerializer, StudentProfileSerializer
from user.permissions import IsTeacher, IsStudent, IsTeacherOrAdmin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import StudentSubmission


@method_decorator(csrf_exempt, name='dispatch')
class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer  # Changed from StudentSubmissionSerializer to StudentProfileSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            # Students can only see their own profile
            return StudentProfile.objects.filter(user=user)
        elif user.role == 'teacher':
            # Teachers can see profiles of students in subjects they teach
            return StudentProfile.objects.filter(subjects__teacher=user).distinct()
        # Admins can see all profiles
        return StudentProfile.objects.all()
        
    def perform_create(self, serializer):
        print(f"Creating student profile with data: {serializer.validated_data}")
        try:
            # Extract subjects data before saving
            if 'subjects' in self.request.data:
                print(f"Subjects data: {self.request.data['subjects']}")
                
            # Let the serializer handle the subjects
            serializer.save()
        except Exception as e:
            print(f"Error creating profile: {str(e)}")
            raise

    # Add debug endpoint to help diagnose issues
    @action(detail=False, methods=['get'], url_path='debug')
    def debug_profile(self, request):
        """Debug endpoint to check serializer and model setup"""
        return Response({
            "subjects_available": list(Subject.objects.values('id', 'name')),
            "sample_format": {
                "user": "user_id (integer)",
                "education_level": "School/College/University",
                "grade": "1-12 or equivalent",
                "subjects": [1, 2, 3]  # List of subject IDs
            }
        })


class MarksViewSet(viewsets.ModelViewSet):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'publish_results', 'bulk_create']:
            return [IsTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'student':
            # Students can only see their published marks or allow them to see unpublished too based on requirements
            student_profile = StudentProfile.objects.filter(user=user).first()
            if student_profile:
                return Marks.objects.filter(student=student_profile, published=True)
            return Marks.objects.none()
        elif user.role == 'teacher':
            # Teachers can see all marks for subjects they teach
            return Marks.objects.filter(subject__teacher=user)
        # Admins can see all marks
        return Marks.objects.all()

    @action(detail=False, methods=['post'], url_path='publish')
    def publish_results(self, request):
        """Publish marks for students"""
        subject_id = request.data.get('subject_id')
        student_ids = request.data.get('student_ids', [])
        publish_all = request.data.get('publish_all', False)

        if not subject_id:
            return Response({"error": "Subject ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if teacher teaches this subject
        subject = Subject.objects.filter(id=subject_id, teacher=request.user).first()
        if not subject:
            return Response(
                {"error": "You can only publish results for subjects you teach"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Build the filter
        filter_kwargs = {'subject': subject}
        if not publish_all and student_ids:
            filter_kwargs['student__id__in'] = student_ids

        # Update marks to published
        marks_count = Marks.objects.filter(**filter_kwargs).update(published=True)

        return Response({
            "message": f"Published {marks_count} results successfully",
            "count": marks_count
        })

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """Add marks for multiple students at once"""
        subject_id = request.data.get('subject_id')
        marks_data = request.data.get('marks_data', [])

        if not subject_id:
            return Response({"error": "Subject ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not marks_data:
            return Response({"error": "Marks data is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if teacher teaches this subject
        subject = Subject.objects.filter(id=subject_id, teacher=request.user).first()
        if not subject:
            return Response(
                {"error": "You can only add marks for subjects you teach"},
                status=status.HTTP_403_FORBIDDEN
            )

        created_count = 0
        updated_count = 0
        errors = []

        for item in marks_data:
            student_id = item.get('student_id')
            mark_value = item.get('marks')

            if not student_id or mark_value is None:
                errors.append(f"Missing student_id or marks for item: {item}")
                continue

            # Find the student profile
            student = StudentProfile.objects.filter(id=student_id).first()
            if not student:
                errors.append(f"Student with ID {student_id} not found")
                continue

            # Update or create the mark
            mark, created = Marks.objects.update_or_create(
                student=student,
                subject=subject,
                defaults={'marks': mark_value}
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return Response({
            "message": f"Created {created_count} marks and updated {updated_count} marks",
            "created": created_count,
            "updated": updated_count,
            "errors": errors
        })


class StudentSubmissionViewSet(viewsets.ModelViewSet):
    """API endpoint for student assignment submissions"""
    queryset = StudentSubmission.objects.all()
    serializer_class = StudentSubmissionSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Only students can create submissions
            return [IsAuthenticated(), IsStudent()]
        if self.action in ['update', 'partial_update', 'destroy']:
            # Only the student who created it or teachers/admins can modify
            return [IsAuthenticated()]
        # Anyone authenticated can view submissions
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return StudentSubmission.objects.none()
            
        if user.role == 'student':
            # Students can see only their own submissions
            return StudentSubmission.objects.filter(student=user)
        elif user.role == 'teacher':
            # Teachers can see submissions for assignments they created or in subjects they teach
            return StudentSubmission.objects.filter(
                assignment__subject__teacher=user
            )
        # Admin can see all submissions
        return StudentSubmission.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
        serializer.save(student=self.request.user)
