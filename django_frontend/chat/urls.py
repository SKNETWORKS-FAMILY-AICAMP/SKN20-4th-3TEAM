from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('<int:dog_id>/', views.chat_room_view, name='chat_room'),
    path('<int:dog_id>/send/', views.send_message_view, name='send_message'),
    path('<int:dog_id>/sessions/', views.chat_sessions_view, name='chat_sessions'),
    path('<int:dog_id>/sessions/<str:session_id>/messages/', views.chat_session_messages_view, name='chat_session_messages'),
    path('<int:dog_id>/sessions/<str:session_id>/delete/', views.chat_session_delete_view, name='chat_session_delete'),
    path('<int:dog_id>/history/delete/', views.chat_history_delete_view, name='chat_history_delete'),
    path('quick/', views.quick_chat_view, name='quick_chat'),
    path('quick/send/', views.quick_chat_send_view, name='quick_chat_send'),
    path('quick/sessions/', views.quick_chat_sessions_view, name='quick_chat_sessions'),
    path('quick/sessions/<str:session_id>/messages/', views.quick_chat_session_messages_view, name='quick_chat_session_messages'),
    path('quick/sessions/<str:session_id>/delete/', views.quick_chat_session_delete_view, name='quick_chat_session_delete'),
    path('quick/history/', views.quick_chat_history_view, name='quick_chat_history'),
    path('quick/history/delete/', views.quick_chat_history_delete_view, name='quick_chat_history_delete'),
]