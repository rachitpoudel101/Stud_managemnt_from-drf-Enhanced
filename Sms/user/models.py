from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_deleted = models.BooleanField(default=False)
    def delete(self, using=None, keep_parents=False):
        """Override delete to perform soft delete"""
        self.is_deleted = True
        self.is_active = False 
        self.save()
        
    def restore(self):
        """Restore a soft-deleted user"""
        self.is_deleted = False
        self.is_active = True
        self.save()
    def __str__(self):
        return self.username

class notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)

    FOR_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('both', 'Both'),
    )
    audience = models.CharField(max_length=10, choices=FOR_CHOICES)
    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Notices'
        ordering = ['-created_at']  # Newest notices first