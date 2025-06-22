# Import User model
from django.db import models
from django.conf import settings
from user.models import User

class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'teacher'},
        related_name='teaching_subjects',
        null=True,
        blank=True
    )
    def __str__(self):
        return self.name

class Assignment(models.Model):
    FOR_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('both', 'Both'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='assignments/', blank=True, null=True)  # Make file optional
    due_date = models.DateTimeField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    remarks = models.TextField(blank=True, null=True)
    audience = models.CharField(max_length=10, choices=FOR_CHOICES)
    published = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Assignments'
        ordering = ['-created_at']