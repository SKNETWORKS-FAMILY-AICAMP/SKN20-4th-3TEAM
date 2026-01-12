"""
커스텀 컨텍스트 프로세서
모든 템플릿에서 전역적으로 사용 가능한 변수 제공
"""

from django.conf import settings


def static_version(request):
    """
    정적 파일 캐시 버스팅을 위한 버전 번호를 제공
    템플릿에서 {{ STATIC_VERSION }}으로 사용 가능

    사용 예시:
    <link rel="stylesheet" href="{% static 'css/style.css' %}?v={{ STATIC_VERSION }}">
    """
    return {
        'STATIC_VERSION': getattr(settings, 'STATIC_VERSION', '1')
    }
