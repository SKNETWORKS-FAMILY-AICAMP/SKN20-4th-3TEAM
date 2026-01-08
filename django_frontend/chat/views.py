from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import requests
import json


@login_required
def chat_room_view(request, dog_id):
    """강아지 채팅방"""
    token = request.session.get('access_token')
    
    try:
        response = requests.get(
            f'{settings.FASTAPI_BASE_URL}/api/dogs/{dog_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            dog = response.json()
            
            return render(request, 'chat/chat_room.html', {
                'dog': dog,
                'dog_data': json.dumps(dog, ensure_ascii=False)
            })
        else:
            messages.error(request, '프로필을 찾을 수 없습니다.')
            return redirect('dogs:profile_select')
    except Exception as e:
        messages.error(request, f'서버 오류: {str(e)}')
        return redirect('dogs:profile_select')


@login_required
def send_message_view(request, dog_id):
    """메시지 전송 (강아지 채팅)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')
            
            token = request.session.get('access_token')
            
            # FastAPI로 메시지 전송
            response = requests.post(
                f'{settings.FASTAPI_BASE_URL}/api/chat/{dog_id}',
                json={'message': message},
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                return JsonResponse({
                    'success': True,
                    'message': ai_response.get('response', '응답을 생성할 수 없습니다.')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '메시지 전송에 실패했습니다.'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def quick_chat_view(request):
    """빠른상담 페이지"""
    return render(request, 'chat/quick_chat.html')


@login_required
def quick_chat_send_view(request):
    """빠른상담 메시지 전송"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message')
            
            token = request.session.get('access_token')
            
            # FastAPI로 메시지 전송
            response = requests.post(
                f'{settings.FASTAPI_BASE_URL}/api/chat/quick',
                json={'message': message},
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                return JsonResponse({
                    'success': True,
                    'message': ai_response.get('response', '응답을 생성할 수 없습니다.')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': '메시지 전송에 실패했습니다.'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})