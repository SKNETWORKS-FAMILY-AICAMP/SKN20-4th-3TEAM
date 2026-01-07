from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import timedelta
from django.utils import timezone


class EmailVerification(models.Model):
    """이메일 인증을 위한 모델"""
    email = models.EmailField(verbose_name='이메일')
    code = models.CharField(max_length=6, verbose_name='인증코드')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성시간')
    is_verified = models.BooleanField(default=False, verbose_name='인증완료여부')
    
    class Meta:
        verbose_name = '이메일 인증'
        verbose_name_plural = '이메일 인증'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} - {self.code}"
    
    def is_expired(self):
        """인증코드가 만료되었는지 확인 (10분)"""
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    @staticmethod
    def generate_code():
        """6자리 랜덤 숫자 코드 생성"""
        return ''.join(random.choices(string.digits, k=6))