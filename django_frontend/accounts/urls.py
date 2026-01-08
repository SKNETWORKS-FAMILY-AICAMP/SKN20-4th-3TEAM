from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # 이메일 인증 API
    path('send-verification/', views.send_verification_view, name='send_verification'),
    path('verify-code/', views.verify_code_view, name='verify_code'),
]