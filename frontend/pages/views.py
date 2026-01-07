from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerification


def send_verification_code(request):
    """이메일 인증코드 발송"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # 이메일 입력 확인
        if not email:
            messages.error(request, '이메일을 입력해주세요.')
            return render(request, 'pages/signup.html')
        
        # 이미 가입된 이메일 확인
        if User.objects.filter(email=email).exists():
            messages.error(request, '이미 가입된 이메일입니다.')
            return render(request, 'pages/signup.html')
        
        # 기존 인증코드 삭제 (같은 이메일)
        EmailVerification.objects.filter(email=email).delete()
        
        # 새 인증코드 생성
        code = EmailVerification.generate_code()
        EmailVerification.objects.create(email=email, code=code)
        
        # 이메일 발송
        try:
            subject = '[반려견 질병 상담 챗봇] 이메일 인증 코드'
            message = f'''
안녕하세요!

반려견 질병 상담 챗봇 회원가입을 위한 인증 코드입니다.

인증 코드: {code}

10분 내에 입력해주세요.

감사합니다.
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, f'{email}로 인증 코드가 발송되었습니다.')
            return render(request, 'pages/verify_code.html', {'email': email})
        
        except Exception as e:
            messages.error(request, f'이메일 발송 실패: {str(e)}')
            return render(request, 'pages/signup.html')
    
    return render(request, 'pages/signup.html')


def verify_code(request):
    """인증코드 확인"""
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        
        # 입력값 확인
        if not email or not code:
            messages.error(request, '이메일과 인증코드를 모두 입력해주세요.')
            return render(request, 'pages/verify_code.html', {'email': email})
        
        try:
            verification = EmailVerification.objects.get(email=email, code=code)
            
            # 만료 확인
            if verification.is_expired():
                messages.error(request, '인증 코드가 만료되었습니다. 다시 시도해주세요.')
                verification.delete()
                return redirect('pages:signup')  # 수정!
            
            # 인증 완료 처리
            verification.is_verified = True
            verification.save()
            
            messages.success(request, '이메일 인증이 완료되었습니다. 회원가입을 완료해주세요.')
            return render(request, 'pages/complete_signup.html', {'email': email})
            
        except EmailVerification.DoesNotExist:
            messages.error(request, '잘못된 인증 코드입니다.')
            return render(request, 'pages/verify_code.html', {'email': email})
    
    return redirect('pages:signup')  # 수정!


def resend_verification_code(request):
    """인증코드 재발송"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # 기존 인증코드 삭제
        EmailVerification.objects.filter(email=email).delete()
        
        # 새 인증코드 생성 및 발송
        code = EmailVerification.generate_code()
        EmailVerification.objects.create(email=email, code=code)
        
        try:
            subject = '[반려견 질병 상담 챗봇] 이메일 인증 코드 (재발송)'
            message = f'''
안녕하세요!

재발송된 인증 코드입니다.

인증 코드: {code}

10분 내에 입력해주세요.

감사합니다.
            '''
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, '인증 코드가 재발송되었습니다.')
        except Exception as e:
            messages.error(request, f'이메일 발송 실패: {str(e)}')
        
        return render(request, 'pages/verify_code.html', {'email': email})
    
    return redirect('pages:signup')  # 수정!


def complete_signup(request):
    """회원가입 완료"""
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # 입력값 확인
        if not all([email, username, password, password_confirm]):
            messages.error(request, '모든 항목을 입력해주세요.')
            return render(request, 'pages/complete_signup.html', {'email': email})
        
        # 비밀번호 확인
        if password != password_confirm:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return render(request, 'pages/complete_signup.html', {'email': email})
        
        # 이메일 인증 확인
        verification = EmailVerification.objects.filter(
            email=email, 
            is_verified=True
        ).first()
        
        if not verification:
            messages.error(request, '이메일 인증이 필요합니다.')
            return redirect('pages:signup')  # 수정!
        
        # 중복 확인
        if User.objects.filter(username=username).exists():
            messages.error(request, '이미 사용중인 아이디입니다.')
            return render(request, 'pages/complete_signup.html', {'email': email})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '이미 가입된 이메일입니다.')
            return redirect('pages:signup')  # 수정!
        
        try:
            # 회원가입 처리
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # 사용한 인증코드 삭제
            verification.delete()
            
            messages.success(request, '회원가입이 완료되었습니다. 로그인해주세요.')
            return redirect('pages:login')  # 수정!
            
        except Exception as e:
            messages.error(request, f'회원가입 실패: {str(e)}')
            return render(request, 'pages/complete_signup.html', {'email': email})
    
    # GET 요청시 이메일 파라미터 확인
    email = request.GET.get('email', '')
    return render(request, 'pages/complete_signup.html', {'email': email})


def user_login(request):
    """로그인"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'{username}님 환영합니다!')
            return redirect('pages:home')  # 수정!
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'pages/login.html')


def user_logout(request):
    """로그아웃"""
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('pages:home')  # 수정!


def home(request):
    """홈페이지"""
    return render(request, 'pages/home.html')


def chat(request):
    """채팅 페이지"""
    return render(request, 'pages/chat.html')


def pet_settings(request):
    """반려견 설정 페이지"""
    from .models import Pet
    
    if not request.user.is_authenticated:
        messages.error(request, '로그인이 필요합니다.')
        return redirect('pages:login')
    
    if request.method == 'POST':
        # 폼 데이터 받기
        name = request.POST.get('name')
        breed = request.POST.get('breed')
        age = request.POST.get('age')
        weight = request.POST.get('weight')
        gender = request.POST.get('gender')
        neutered = request.POST.get('neutered')
        diseases = request.POST.get('diseases', '')
        medications = request.POST.get('medications', '')
        allergies = request.POST.get('allergies', '')
        
        # 필수 항목 확인
        if not all([name, breed, age, weight, gender, neutered]):
            messages.error(request, '필수 항목을 모두 입력해주세요.')
            return render(request, 'pages/pet_settings.html')
        
        try:
            # 반려견 등록
            Pet.objects.create(
                owner=request.user,
                name=name,
                breed=breed,
                age=int(age),
                weight=float(weight),
                gender=gender,
                neutered=neutered,
                diseases=diseases,
                medications=medications,
                allergies=allergies
            )
            messages.success(request, f'{name}이(가) 성공적으로 등록되었습니다!')
            return redirect('pages:select_pet')
            
        except Exception as e:
            messages.error(request, f'반려견 등록 실패: {str(e)}')
            return render(request, 'pages/pet_settings.html')
    
    return render(request, 'pages/pet_settings.html')


def reset_password(request):
    """비밀번호 재설정 페이지"""
    return render(request, 'pages/reset_password.html')


def select_pet(request):
    """반려견 선택 페이지"""
    from .models import Pet
    
    if not request.user.is_authenticated:
        messages.error(request, '로그인이 필요합니다.')
        return redirect('pages:login')
    
    # 사용자의 반려견 목록 가져오기
    pets = Pet.objects.filter(owner=request.user)
    
    return render(request, 'pages/select_pet.html', {'pets': pets})


def withdraw(request):
    """회원 탈퇴 페이지"""
    return render(request, 'pages/withdraw.html')