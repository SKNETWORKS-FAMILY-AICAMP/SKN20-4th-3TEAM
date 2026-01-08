from django.urls import path
from . import views

app_name = 'dogs'

urlpatterns = [
    path('select/', views.profile_select_view, name='profile_select'),
    path('create/', views.profile_create_view, name='profile_create'),
    path('<int:dog_id>/', views.profile_detail_view, name='profile_detail'),
]