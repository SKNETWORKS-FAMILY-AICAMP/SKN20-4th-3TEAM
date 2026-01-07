from django.shortcuts import render
from django.views.decorators.http import require_http_methods

# 메인 페이지
def home(request):
    """메인 페이지 - 서비스 소개용 랜딩 페이지"""
    return render(request, 'pages/home.html')

# 로그인 페이지
@require_http_methods(["GET", "POST"])
def login(request):
    """로그인 페이지 - 더미 페이지"""
    if request.method == 'POST':
        # 실제 로직 없음
        pass
    return render(request, 'pages/login.html')

# 비밀번호 재설정
@require_http_methods(["GET", "POST"])
def reset_password(request):
    """비밀번호 재설정 페이지 - 더미 페이지"""
    if request.method == 'POST':
        # 실제 로직 없음
        pass
    return render(request, 'pages/reset_password.html')

# 회원가입 페이지
@require_http_methods(["GET", "POST"])
def signup(request):
    """회원가입 페이지 - 더미 페이지"""
    if request.method == 'POST':
        # 실제 로직 없음
        pass
    return render(request, 'pages/signup.html')

# 회원 탈퇴
@require_http_methods(["GET", "POST"])
def withdraw(request):
    """회원 탈퇴 페이지 - 더미 페이지"""
    if request.method == 'POST':
        # 실제 로직 없음
        pass
    return render(request, 'pages/withdraw.html')

# 반려견 선택 페이지
def select_pet(request):
    """반려견 선택 페이지 - 채팅 진입 전"""
    # 더미 반려견 데이터
    pets = [
        {'name': '뽀삐', 'breed': '포메라니안', 'age': 3},
        {'name': '초코', 'breed': '라브라도', 'age': 5},
        {'name': '몽이', 'breed': '푸들', 'age': 2},
    ]
    context = {'pets': pets}
    return render(request, 'pages/select_pet.html', context)

# 채팅 페이지
def chat(request):
    """채팅 페이지 - 더미 메시지 포함"""
    # 더미 데이터
    context = {
        'current_pet': '뽀삐',
    }
    return render(request, 'pages/chat.html', context)

# 반려견 설정 페이지
@require_http_methods(["GET", "POST"])
def pet_settings(request):
    """반려견 설정 페이지 - 더미 페이지"""
    if request.method == 'POST':
        # 실제 로직 없음
        pass
    return render(request, 'pages/pet_settings.html')
