from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

# 이메일 발송을 위한 함수들
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail 설정
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "beauty1balance@gmail.com"  # ⚠️ 여기에 본인의 Gmail 주소 입력!
SENDER_PASSWORD = "slte ovyk rejy hzuv"

# 인증번호 임시 저장
verification_codes = {}


def generate_verification_code():
    """6자리 인증번호 생성"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(to_email, verification_code):
    """인증 이메일 발송"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = '[강아지 채팅] 이메일 인증번호'
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f7f7f7; padding: 30px; border-radius: 10px;">
                <h2 style="color: #667eea;">🐕 강아지 채팅 이메일 인증</h2>
                <p>안녕하세요!</p>
                <p>회원가입을 위한 인증번호를 보내드립니다.</p>
                
                <div style="background: white; padding: 20px; margin: 20px 0; border-radius: 5px; text-align: center;">
                    <h1 style="color: #667eea; font-size: 36px; margin: 0;">{verification_code}</h1>
                </div>
                
                <p>위 인증번호를 입력하여 회원가입을 완료해주세요.</p>
                <p style="color: #999; font-size: 12px;">* 이 인증번호는 5분간 유효합니다.</p>
                <p style="color: #999; font-size: 12px;">* 본인이 요청하지 않은 경우 이 메일을 무시하세요.</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ 인증 이메일 발송 성공: {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {str(e)}")
        return False


def send_verification_view(request):
    """인증번호 발송 API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({'success': False, 'message': '이메일을 입력해주세요.'})
            
            # ⭐ FastAPI에 이메일 중복 체크 요청
            try:
                check_response = requests.get(
                    f'{settings.FASTAPI_BASE_URL}/api/auth/check-email/{email}'
                )
                
                if check_response.status_code == 200:
                    data_response = check_response.json()
                    
                    # 이미 가입된 이메일이면 에러 반환
                    if data_response.get('exists'):
                        return JsonResponse({
                            'success': False,
                            'message': '이미 가입된 이메일 주소입니다.'
                        })
            except Exception as e:
                print(f"이메일 중복 체크 중 오류: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
                })
            
            # 인증번호 생성
            code = generate_verification_code()
            
            # 이메일 발송
            if send_verification_email(email, code):
                # 인증번호 저장
                verification_codes[email] = code
                print(f"🔑 인증번호 저장: {email} -> {code}")
                return JsonResponse({'success': True, 'message': '인증번호가 발송되었습니다.'})
            else:
                return JsonResponse({'success': False, 'message': '이메일 발송에 실패했습니다.'})
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def verify_code_view(request):
    """인증번호 확인 API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            
            print(f"🔍 인증 확인: {email} -> {code}")
            print(f"📝 저장된 코드: {verification_codes.get(email)}")
            
            if email in verification_codes and verification_codes[email] == code:
                # 인증 성공
                del verification_codes[email]
                return JsonResponse({'success': True, 'message': '인증이 완료되었습니다.'})
            else:
                return JsonResponse({'success': False, 'message': '인증번호가 일치하지 않습니다.'})
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def signup_view(request):
    """회원가입 페이지"""
    if request.method == 'POST':
        email = request.POST.get('verified_email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # 비밀번호 확인
        if password != password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, 'accounts/signup.html')
        
        # FastAPI 백엔드로 회원가입 요청
        try:
            response = requests.post(
                f'{settings.FASTAPI_BASE_URL}/api/auth/signup',
                json={
                    'email': email,
                    'username': username,
                    'password': password
                }
            )
            
            if response.status_code == 201:
                messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
                return redirect('accounts:login')
            else:
                error_msg = response.json().get('detail', '회원가입에 실패했습니다.')
                messages.error(request, error_msg)
        except Exception as e:
            messages.error(request, f'서버 오류: {str(e)}')
    
    return render(request, 'accounts/signup.html')


def login_view(request):
    """로그인 페이지"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # FastAPI 백엔드로 로그인 요청
        try:
            response = requests.post(
                f'{settings.FASTAPI_BASE_URL}/api/auth/login',
                json={
                    'email': email,
                    'password': password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                # 세션에 토큰 저장
                request.session['access_token'] = data['access_token']
                request.session['user_email'] = email
                
                # Django 사용자 생성 또는 가져오기
                user, created = User.objects.get_or_create(
                    username=email,
                    defaults={'email': email}
                )
                
                # Django 로그인
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                messages.success(request, '로그인 되었습니다.')
                return redirect('dogs:profile_select')
            else:
                messages.error(request, '이메일 또는 비밀번호가 잘못되었습니다.')
        except Exception as e:
            messages.error(request, f'서버 오류: {str(e)}')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """로그아웃"""
    if 'access_token' in request.session:
        del request.session['access_token']
    if 'user_email' in request.session:
        del request.session['user_email']
    
    logout(request)
    messages.success(request, '로그아웃 되었습니다.')
    return redirect('accounts:login')