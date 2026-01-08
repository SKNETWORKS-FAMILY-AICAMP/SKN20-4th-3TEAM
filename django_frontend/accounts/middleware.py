"""
JWT 토큰 기반 세션 인증 미들웨어
FastAPI에서 발급한 JWT 토큰을 사용하여 Django 세션 유지
"""
from django.contrib.auth.models import AnonymousUser


class JWTAuthMiddleware:
    """
    JWT 토큰이 세션에 있으면 Django @login_required 데코레이터 지원
    Django User 모델 사용 안 함 (순수 JWT 토큰 기반)
    세션 만료 시 자동 로그아웃 처리
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 세션에 JWT 토큰이 있는지 확인
        access_token = request.session.get('access_token')
        email = request.session.get('email')
        username = request.session.get('username')
        user_id = request.session.get('user_id')
        
        # 세션이 없으면 AnonymousUser로 설정
        if not access_token or not email:
            # 세션 데이터 전부 삭제 (세션 만료)
            request.session.flush()
            request.user = AnonymousUser()
        else:
            # 토큰이 유효하면 request.user에 간단한 객체 설정
            # Django의 @login_required와 호환되도록 is_authenticated 추가
            class SimpleUser:
                is_authenticated = True
                
                def __init__(self, email, username, user_id):
                    self.email = email
                    self.id = user_id
                    # FastAPI에서 받은 username 사용, 없으면 이메일 앞부분 사용
                    self.username = username if username else email.split('@')[0]
                
                def __str__(self):
                    return self.email
            
            request.user = SimpleUser(email, username, user_id)
        
        response = self.get_response(request)
        return response
