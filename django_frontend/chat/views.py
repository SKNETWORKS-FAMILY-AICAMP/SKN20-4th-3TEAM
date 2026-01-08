from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import requests
import json


@login_required
def chat_room_view(request, dog_id):
    """채팅방 화면"""
    token = request.session.get('access_token')
    
    # 강아지 프로필 정보 가져오기
    try:
        dog_response = requests.get(
            f'{settings.FASTAPI_BASE_URL}/api/dogs/{dog_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if dog_response.status_code == 200:
            dog = dog_response.json()
        else:
            messages.error(request, '강아지 프로필을 찾을 수 없습니다.')
            return redirect('dogs:profile_select')
        
        # 채팅 히스토리 가져오기
        history_response = requests.get(
            f'{settings.FASTAPI_BASE_URL}/api/chat/{dog_id}/history',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if history_response.status_code == 200:
            chat_history = history_response.json()
        else:
            chat_history = []
        
    except Exception as e:
        messages.error(request, f'서버 오류: {str(e)}')
        return redirect('dogs:profile_select')
    
    context = {
        'dog': dog,
        'chat_history': chat_history,
    }
    
    return render(request, 'chat/chat_room.html', context)


@login_required
def send_message_api(request, dog_id):
    """메시지 전송 API (AJAX용)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')
            
            token = request.session.get('access_token')
            
            # FastAPI로 메시지 전송
            response = requests.post(
                f'{settings.FASTAPI_BASE_URL}/api/chat/',
                json={
                    'dog_id': dog_id,
                    'message': message
                },
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 201:
                ai_response = response.json()
                return JsonResponse({
                    'success': True,
                    'message': ai_response.get('message'),
                    'is_user': ai_response.get('is_user'),
                    'created_at': ai_response.get('created_at')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '메시지 전송에 실패했습니다.'
                }, status=400)
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)