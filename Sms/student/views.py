from rest_framework import status
from rest_framework.response import Response
from teacher.models import Subject
from rest_framework.decorators import action
from rest_framework import viewsets
from student.models import Marks, StudentProfile
from student.serializers import MarksSerializer
from user import permissions
from user.permissions import IsTeacher


class MarksViewSet(viewsets.ModelViewSet):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'publish_results', 'bulk_create']:
            return [IsTeacher()]
        return [permissions.IsAuthenticated()]

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
