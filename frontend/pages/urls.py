from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.send_verification_code, name='signup'),
    path('verify/', views.verify_code, name='verify_code'),
    path('resend-code/', views.resend_verification_code, name='resend_code'),
    path('complete-signup/', views.complete_signup, name='complete_signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('chat/', views.chat, name='chat'),
    path('pet-settings/', views.pet_settings, name='pet_settings'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('select-pet/', views.select_pet, name='select_pet'),
    path('withdraw/', views.withdraw, name='withdraw'),
]