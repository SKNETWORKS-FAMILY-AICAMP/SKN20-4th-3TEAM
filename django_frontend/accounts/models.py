from django.db import models
from django.contrib.auth.models import User

# accounts 앱은 Django 기본 User 모델을 사용합니다.
# 추가적인 사용자 프로필이 필요하면 여기에 작성

class UserProfile(models.Model):
    """사용자 프로필 확장 (필요시 사용)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}의 프로필"