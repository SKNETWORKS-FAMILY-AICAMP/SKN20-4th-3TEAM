"""
HTTP 요청 최적화 유틸리티
- 연결 풀링을 통한 성능 향상
- 자동 타임아웃 설정
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings


class FastAPIClient:
    """FastAPI 요청을 위한 최적화된 클라이언트"""

    _session = None

    @classmethod
    def get_session(cls):
        """재사용 가능한 requests 세션 반환 (연결 풀링)"""
        if cls._session is None:
            cls._session = requests.Session()

            # 재시도 정책 설정
            retry_strategy = Retry(
                total=3,  # 최대 3번 재시도
                backoff_factor=0.3,  # 재시도 간격
                status_forcelist=[500, 502, 503, 504],  # 재시도할 HTTP 상태 코드
            )

            # HTTPAdapter 설정 (연결 풀링)
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=10,  # 연결 풀 크기
                pool_maxsize=20  # 최대 연결 수
            )

            cls._session.mount("http://", adapter)
            cls._session.mount("https://", adapter)

        return cls._session

    @classmethod
    def get(cls, url, **kwargs):
        """GET 요청 (자동 타임아웃 포함)"""
        session = cls.get_session()
        timeout = kwargs.pop('timeout', settings.REQUEST_TIMEOUT)
        return session.get(url, timeout=timeout, **kwargs)

    @classmethod
    def post(cls, url, **kwargs):
        """POST 요청 (자동 타임아웃 포함)"""
        session = cls.get_session()
        timeout = kwargs.pop('timeout', settings.REQUEST_TIMEOUT)
        return session.post(url, timeout=timeout, **kwargs)

    @classmethod
    def delete(cls, url, **kwargs):
        """DELETE 요청 (자동 타임아웃 포함)"""
        session = cls.get_session()
        timeout = kwargs.pop('timeout', settings.REQUEST_TIMEOUT)
        return session.delete(url, timeout=timeout, **kwargs)

    @classmethod
    def put(cls, url, **kwargs):
        """PUT 요청 (자동 타임아웃 포함)"""
        session = cls.get_session()
        timeout = kwargs.pop('timeout', settings.REQUEST_TIMEOUT)
        return session.put(url, timeout=timeout, **kwargs)
