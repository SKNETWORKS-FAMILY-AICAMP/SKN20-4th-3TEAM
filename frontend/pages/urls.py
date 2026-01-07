from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # 기본 페이지
    path('', views.home, name='home'),
    
    # 인증 관련
    path('login/', views.login, name='login'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('signup/', views.signup, name='signup'),
    path('withdraw/', views.withdraw, name='withdraw'),
    
    # 채팅 관련
    path('select-pet/', views.select_pet, name='select_pet'),
    path('chat/', views.chat, name='chat'),
    path('pet-settings/', views.pet_settings, name='pet_settings'),
]
