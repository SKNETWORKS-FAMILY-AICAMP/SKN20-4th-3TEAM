from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import requests
import json


@login_required
def profile_select_view(request):
    """강아지 프로필 선택 화면"""
    token = request.session.get('access_token')
    
    try:
        response = requests.get(
            f'{settings.FASTAPI_BASE_URL}/api/dogs/',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            dogs = response.json()
        else:
            dogs = []
    except Exception as e:
        messages.error(request, f'프로필을 불러오는데 실패했습니다: {str(e)}')
        dogs = []
    
    return render(request, 'dogs/profile_select.html', {'dogs': dogs})


@login_required
def profile_create_view(request):
    """강아지 프로필 생성 화면"""
    token = request.session.get('access_token')
    
    # GET 요청 시 프로필 개수 확인
    if request.method == 'GET':
        try:
            response = requests.get(
                f'{settings.FASTAPI_BASE_URL}/api/dogs/',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                dogs = response.json()
                if len(dogs) >= 10:
                    messages.warning(request, '프로필은 최대 10개까지만 생성할 수 있습니다.')
                    return redirect('dogs:profile_select')
        except:
            pass
    
    # POST 요청 시 프로필 생성
    if request.method == 'POST':
        name = request.POST.get('name')
        breed = request.POST.get('breed')
        
        # 생년월일 조합
        birth_year = request.POST.get('birth_year')
        birth_month = request.POST.get('birth_month')
        birth_day = request.POST.get('birth_day')
        
        birth_date = None
        if birth_year and birth_month and birth_day:
            birth_date = f"{birth_year}-{birth_month.zfill(2)}-{birth_day.zfill(2)}"
        
        gender = request.POST.get('gender')
        size = request.POST.get('size')
        weight = request.POST.get('weight')
        neutered = request.POST.get('neutered')
        health_info = request.POST.get('health_info')
        medication = request.POST.get('medication')
        # ⭐ 성격 필드 제거됨
        
        # 나이 계산
        age = None
        if birth_year:
            from datetime import datetime
            current_year = datetime.now().year
            age = current_year - int(birth_year)
        
        try:
            response = requests.post(
                f'{settings.FASTAPI_BASE_URL}/api/dogs/',
                json={
                    'name': name,
                    'breed': breed if breed else '믹스견',
                    'age': age,
                    'birth_date': birth_date,
                    'gender': gender,
                    'size': size,
                    'weight': weight,
                    'neutered': neutered,
                    'health_info': health_info,
                    'medication': medication
                },
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 201:
                messages.success(request, f'{name} 프로필이 생성되었습니다!')
                return redirect('dogs:profile_select')
            elif response.status_code == 400:
                error_data = response.json()
                messages.error(request, error_data.get('detail', '프로필 생성에 실패했습니다.'))
            else:
                messages.error(request, '프로필 생성에 실패했습니다.')
        except Exception as e:
            messages.error(request, f'서버 오류: {str(e)}')
    
    return render(request, 'dogs/profile_create.html')


@login_required
def profile_edit_view(request, dog_id):
    """강아지 프로필 수정 화면"""
    token = request.session.get('access_token')
    
    # 기존 프로필 정보 가져오기
    try:
        response = requests.get(
            f'{settings.FASTAPI_BASE_URL}/api/dogs/{dog_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            dog = response.json()
        else:
            messages.error(request, '프로필을 찾을 수 없습니다.')
            return redirect('dogs:profile_select')
    except Exception as e:
        messages.error(request, f'서버 오류: {str(e)}')
        return redirect('dogs:profile_select')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        breed = request.POST.get('breed')
        
        # 생년월일 조합
        birth_year = request.POST.get('birth_year')
        birth_month = request.POST.get('birth_month')
        birth_day = request.POST.get('birth_day')
        
        birth_date = None
        if birth_year and birth_month and birth_day:
            birth_date = f"{birth_year}-{birth_month.zfill(2)}-{birth_day.zfill(2)}"
        
        gender = request.POST.get('gender')
        size = request.POST.get('size')
        weight = request.POST.get('weight')
        neutered = request.POST.get('neutered')
        health_info = request.POST.get('health_info')
        medication = request.POST.get('medication')
        # ⭐ 성격 필드 제거됨
        
        # 나이 계산
        age = None
        if birth_year:
            from datetime import datetime
            current_year = datetime.now().year
            age = current_year - int(birth_year)
        
        try:
            response = requests.put(
                f'{settings.FASTAPI_BASE_URL}/api/dogs/{dog_id}',
                json={
                    'name': name,
                    'breed': breed if breed else '믹스견',
                    'age': age,
                    'birth_date': birth_date,
                    'gender': gender,
                    'size': size,
                    'weight': weight,
                    'neutered': neutered,
                    'health_info': health_info,
                    'medication': medication
                },
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                messages.success(request, f'{name} 프로필이 수정되었습니다!')
                return redirect('dogs:profile_select')
            elif response.status_code == 400:
                error_data = response.json()
                messages.error(request, error_data.get('detail', '프로필 수정에 실패했습니다.'))
            else:
                messages.error(request, '프로필 수정에 실패했습니다.')
        except Exception as e:
            messages.error(request, f'서버 오류: {str(e)}')
    
    # dog 객체를 JSON으로 변환하여 JavaScript에서 사용할 수 있도록 함
    # personality 속성은 제거되었으므로 포함되지 않음
    dog_data = json.dumps(dog)
    
    return render(request, 'dogs/profile_edit.html', {
        'dog': dog,
        'dog_data': dog_data
    })


@login_required
def profile_delete_view(request, dog_id):
    """강아지 프로필 삭제"""
    if request.method == 'POST':
        token = request.session.get('access_token')
        
        try:
            response = requests.delete(
                f'{settings.FASTAPI_BASE_URL}/api/dogs/{dog_id}',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                messages.success(request, '프로필이 삭제되었습니다.')
            else:
                messages.error(request, '프로필 삭제에 실패했습니다.')
        except Exception as e:
            messages.error(request, f'서버 오류: {str(e)}')
    
    return redirect('dogs:profile_select')


@login_required
def profile_detail_view(request, dog_id):
    """강아지 프로필 상세 화면"""
    token = request.session.get('access_token')
    
    try:
        response = requests.get(
            f'{settings.FASTAPI_BASE_URL}/api/dogs/{dog_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            dog = response.json()
            request.session['current_dog_id'] = dog_id
            return redirect('chat:chat_room', dog_id=dog_id)
        else:
            messages.error(request, '프로필을 찾을 수 없습니다.')
            return redirect('dogs:profile_select')
    except Exception as e:
        messages.error(request, f'서버 오류: {str(e)}')
        return redirect('dogs:profile_select')