from django.db import models
from user.models import User
from teacher.models import Assignment, Subject

class StudentProfile(models.Model):
    GRADE_CHOICES = [
        ('1', 'Grade 1'),
        ('2', 'Grade 2'),
        ('3', 'Grade 3'),
        ('4', 'Grade 4'),
        ('5', 'Grade 5'),
        ('6', 'Grade 6'),
        ('7', 'Grade 7'),
        ('8', 'Grade 8'),
        ('9', 'Grade 9'),
        ('10', 'Grade 10'),
        ('11', 'Grade 11'),
        ('12', 'Grade 12'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    education_level = models.CharField(max_length=100, blank=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='1')
    subjects = models.ManyToManyField(Subject, related_name='students')

    def __str__(self):
        return f"{self.user.username}, Grade {self.grade}"
    
class Marks(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.FloatField()
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'subject')
        verbose_name_plural = 'Marks'

    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name} - {self.marks}"

class StudentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('assignment', 'student')
        verbose_name_plural = 'Student Submissions'

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"