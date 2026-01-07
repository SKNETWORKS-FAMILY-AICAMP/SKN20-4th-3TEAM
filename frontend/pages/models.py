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


class Pet(models.Model):
    """반려견 정보 모델"""
    # 기본 정보
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets', verbose_name='소유자')
    name = models.CharField(max_length=50, verbose_name='이름')
    breed = models.CharField(max_length=100, verbose_name='종')
    age = models.IntegerField(verbose_name='나이')
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='체중(kg)')
    gender = models.CharField(max_length=10, choices=[
        ('male', '수컷'),
        ('female', '암컷')
    ], verbose_name='성별')
    
    # 건강 정보
    neutered = models.CharField(max_length=10, choices=[
        ('yes', '중성화 함'),
        ('no', '중성화 안 함'),
        ('unknown', '모름')
    ], verbose_name='중성화 여부')
    diseases = models.TextField(blank=True, null=True, verbose_name='기저질환')
    medications = models.TextField(blank=True, null=True, verbose_name='복용 중인 약')
    allergies = models.TextField(blank=True, null=True, verbose_name='알레르기')
    
    # 메타 정보
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '반려견'
        verbose_name_plural = '반려견'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.owner.username})"