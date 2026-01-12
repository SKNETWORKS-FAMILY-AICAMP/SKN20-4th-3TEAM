from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 회원가입 & 로그인
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # 회원가입 이메일 인증
    path('send-verification/', views.send_verification_view, name='send_verification'),
    path('verify-code/', views.verify_code_view, name='verify_code'),
    
    # 비밀번호 재설정 (로그인 전)
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('send-password-reset/', views.send_password_reset_view, name='send_password_reset'),
    path('verify-reset-code/', views.verify_reset_code_view, name='verify_reset_code'),
    
    # 프로필 설정 (로그인 후)
    path('settings/', views.settings_view, name='settings'),
    path('update-profile/', views.update_profile_view, name='update_profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
]