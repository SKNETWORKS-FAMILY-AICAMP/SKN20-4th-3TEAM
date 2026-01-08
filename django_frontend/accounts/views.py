from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
import requests
import json

# 이메일 발송
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail 설정
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "beauty1balance@gmail.com"  # ⚠️ Gmail 주소 입력
SENDER_PASSWORD = "slte ovyk rejy hzuv"  # ⚠️ 새 앱 비밀번호 입력

# 인증번호 임시 저장
verification_codes = {}
password_reset_codes = {}


def generate_verification_code():
    """6자리 인증번호 생성"""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(to_email, verification_code, is_password_reset=False):
    """인증 이메일 발송"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        
        if is_password_reset:
            msg['Subject'] = '[강아지 채팅] 비밀번호 재설정 인증번호'
            title = '비밀번호 재설정'
            desc = '비밀번호 재설정을 위한 인증번호를 보내드립니다.'
        else:
            msg['Subject'] = '[강아지 채팅] 이메일 인증번호'
            title = '이메일 인증'
            desc = '회원가입을 위한 인증번호를 보내드립니다.'
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #f7f7f7; padding: 30px; border-radius: 10px;">
                <h2 style="color: #667eea;">🐕 강아지 채팅 {title}</h2>
                <p>안녕하세요!</p>
                <p>{desc}</p>
                
                <div style="background: white; padding: 20px; margin: 20px 0; border-radius: 5px; text-align: center;">
                    <h1 style="color: #667eea; font-size: 36px; margin: 0;">{verification_code}</h1>
                </div>
                
                <p>위 인증번호를 입력하여 진행해주세요.</p>
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


# ============= 랜딩 페이지 =============

def landing_view(request):
    """메인 랜딩 페이지"""
    if request.user.is_authenticated:
        return redirect('dogs:profile_select')
    return render(request, 'landing.html')


# ============= 회원가입 관련 =============

def send_verification_view(request):
    """회원가입 인증번호 발송"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({'success': False, 'message': '이메일을 입력해주세요.'})
            
            try:
                check_response = requests.get(
                    f'{settings.FASTAPI_BASE_URL}/api/auth/check-email/{email}'
                )
                
                if check_response.status_code == 200:
                    data_response = check_response.json()
                    if data_response.get('exists'):
                        return JsonResponse({
                            'success': False,
                            'message': '이미 가입된 이메일 주소입니다.'
                        })
            except Exception as e:
                print(f"이메일 중복 체크 중 오류: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': '서버 오류가 발생했습니다.'
                })
            
            code = generate_verification_code()
            
            if send_verification_email(email, code, is_password_reset=False):
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
    """회원가입 인증번호 확인"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            
            if email in verification_codes and verification_codes[email] == code:
                del verification_codes[email]
                return JsonResponse({'success': True, 'message': '인증이 완료되었습니다.'})
            else:
                return JsonResponse({'success': False, 'message': '인증번호가 일치하지 않습니다.'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def signup_view(request):
    """회원가입"""
    if request.method == 'POST':
        email = request.POST.get('verified_email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, 'accounts/signup.html')
        
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


# ============= 로그인/로그아웃 =============

def login_view(request):
    """로그인"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
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
                request.session['access_token'] = data['access_token']
                request.session['user_email'] = email
                
                user, created = User.objects.get_or_create(
                    username=email,
                    defaults={'email': email}
                )
                
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
    return redirect('landing')


# ============= 비밀번호 재설정 (로그인 전) =============

def send_password_reset_view(request):
    """비밀번호 재설정 인증번호 발송"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({'success': False, 'message': '이메일을 입력해주세요.'})
            
            try:
                check_response = requests.get(
                    f'{settings.FASTAPI_BASE_URL}/api/auth/check-email/{email}'
                )
                
                if check_response.status_code == 200:
                    data_response = check_response.json()
                    if not data_response.get('exists'):
                        return JsonResponse({
                            'success': False,
                            'message': '가입되지 않은 이메일입니다.'
                        })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': '서버 오류가 발생했습니다.'
                })
            
            code = generate_verification_code()
            
            if send_verification_email(email, code, is_password_reset=True):
                password_reset_codes[email] = code
                print(f"🔑 비밀번호 재설정 인증번호: {email} -> {code}")
                return JsonResponse({'success': True, 'message': '인증번호가 발송되었습니다.'})
            else:
                return JsonResponse({'success': False, 'message': '이메일 발송에 실패했습니다.'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def verify_reset_code_view(request):
    """비밀번호 재설정 인증번호 확인"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            code = data.get('code')
            
            if email in password_reset_codes and password_reset_codes[email] == code:
                del password_reset_codes[email]
                return JsonResponse({'success': True, 'message': '인증이 완료되었습니다.'})
            else:
                return JsonResponse({'success': False, 'message': '인증번호가 일치하지 않습니다.'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def password_reset_view(request):
    """비밀번호 재설정 페이지"""
    if request.method == 'POST':
        email = request.POST.get('verified_email')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, 'accounts/password_reset.html')
        
        try:
            response = requests.post(
                f'{settings.FASTAPI_BASE_URL}/api/auth/reset-password',
                json={
                    'email': email,
                    'new_password': new_password
                }
            )
            
            if response.status_code == 200:
                messages.success(request, '비밀번호가 재설정되었습니다. 로그인해주세요.')
                return redirect('accounts:login')
            else:
                messages.error(request, '비밀번호 재설정에 실패했습니다.')
        except Exception as e:
            messages.error(request, f'서버 오류: {str(e)}')
    
    return render(request, 'accounts/password_reset.html')


# ============= 프로필 설정 (로그인 후) =============

@login_required
def settings_view(request):
    """설정 페이지"""
    try:
        email = request.session.get('user_email')
        
        response = requests.get(
            f'{settings.FASTAPI_BASE_URL}/api/auth/user-info/{email}'
        )
        
        if response.status_code == 200:
            user_info = response.json()
        else:
            user_info = {
                'username': request.user.username,
                'email': email
            }
    except Exception as e:
        print(f"사용자 정보 로드 오류: {str(e)}")
        user_info = {
            'username': request.user.username,
            'email': request.user.email
        }
    
    return render(request, 'accounts/settings.html', {'user_info': user_info})


@login_required
def update_profile_view(request):
    """프로필 정보 수정"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.session.get('user_email')
        
        try:
            response = requests.post(
                f'{settings.FASTAPI_BASE_URL}/api/auth/update-profile',
                json={
                    'email': email,
                    'username': username
                }
            )
            
            if response.status_code == 200:
                user = User.objects.get(username=email)
                user.username = username
                user.save()
                
                messages.success(request, '프로필이 업데이트되었습니다.')
            else:
                error_msg = response.json().get('detail', '프로필 업데이트에 실패했습니다.')
                messages.error(request, error_msg)
        except Exception as e:
            messages.error(request, f'서버 오류: {str(e)}')
    
    return redirect('accounts:settings')


@login_required
def change_password_view(request):
    """비밀번호 변경 (로그인 상태)"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            messages.error(request, '새 비밀번호가 일치하지 않습니다.')
            return redirect('accounts:settings')
        
        email = request.session.get('user_email')
        
        try:
            response = requests.post(
                f'{settings.FASTAPI_BASE_URL}/api/auth/change-password',
                json={
                    'email': email,
                    'current_password': current_password,
                    'new_password': new_password
                }
            )
            
            if response.status_code == 200:
                messages.success(request, '비밀번호가 변경되었습니다.')
            else:
                messages.error(request, '현재 비밀번호가 일치하지 않습니다.')
        except Exception as e:
            messages.error(request, f'서버 오류: {str(e)}')
    
    return redirect('accounts:settings')


@login_required
def delete_account_view(request):
    """계정 삭제"""
    email = request.session.get('user_email')
    
    try:
        response = requests.delete(
            f'{settings.FASTAPI_BASE_URL}/api/auth/delete-account/{email}'
        )
        print(f"계정 삭제 응답: {response.status_code}")
    except Exception as e:
        print(f"계정 삭제 오류: {str(e)}")
    
    request.user.delete()
    logout(request)
    
    messages.success(request, '계정이 삭제되었습니다.')
    return redirect('landing')