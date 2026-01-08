from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('<int:dog_id>/', views.chat_room_view, name='chat_room'),
    path('<int:dog_id>/send/', views.send_message_view, name='send_message'),
    path('quick/', views.quick_chat_view, name='quick_chat'),
    path('quick/send/', views.quick_chat_send_view, name='quick_chat_send'),
]