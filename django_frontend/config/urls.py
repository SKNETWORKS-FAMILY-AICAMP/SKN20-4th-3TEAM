"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import landing_view  # 추가!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_view, name='landing'),  # 루트 URL을 랜딩 페이지로 변경!
    path('accounts/', include('accounts.urls')),
    path('dogs/', include('dogs.urls')),
    path('chat/', include('chat.urls')),
]

# 개발 환경에서 media 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)