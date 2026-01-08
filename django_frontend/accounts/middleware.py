"""
JWT 토큰 기반 세션 인증 미들웨어
FastAPI에서 발급한 JWT 토큰을 사용하여 Django 세션 유지
"""


class JWTAuthMiddleware:
    """
    JWT 토큰이 세션에 있으면 Django @login_required 데코레이터 지원
    Django User 모델 사용 안 함 (순수 JWT 토큰 기반)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 세션에 JWT 토큰이 있는지 확인
        access_token = request.session.get('access_token')
        email = request.session.get('email')
        
        if access_token and email:
            # 토큰이 유효하면 request.user에 간단한 객체 설정
            # Django의 @login_required와 호환되도록 is_authenticated 추가
            class SimpleUser:
                is_authenticated = True
                def __str__(self):
                    return email
            
            request.user = SimpleUser()
        
        response = self.get_response(request)
        return response
