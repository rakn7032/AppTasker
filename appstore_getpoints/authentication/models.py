from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone

class User(AbstractUser):
    gender_choices = [('Male', 'Male'),
                      ('Female', 'Female'),
                      ('Others', 'Others')]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=500, unique=True)
    profile_pic = models.URLField(max_length=255,blank=True, null=True)
    gender = models.CharField(max_length=100,blank=True,null=True,choices = gender_choices)
    bio = models.TextField(max_length=5000,blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return self.first_name

class Permission(models.Model):
    name = models.CharField(max_length=100)
    admin = models.BooleanField(default=False)
    user = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
class UserAuth(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    permissions = models.ManyToManyField(Permission, blank=True)
    otp = models.CharField(max_length=20,blank=True,null=True)
    otp_validated_upto = models.DateTimeField(blank=True,null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        return self.user.first_name
