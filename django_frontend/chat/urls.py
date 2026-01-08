from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('<int:dog_id>/', views.chat_room_view, name='chat_room'),
    path('<int:dog_id>/send/', views.send_message_api, name='send_message'),
]