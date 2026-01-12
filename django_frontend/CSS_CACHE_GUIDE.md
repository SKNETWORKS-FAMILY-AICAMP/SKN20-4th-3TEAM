# CSS 캐시 문제 해결 가이드

## 문제 원인
같은 HTML/CSS 코드를 사용하는데도 사람마다 디자인이 다르게 보이는 이유는 **브라우저 캐시** 때문입니다.

## 해결 방법

### 1. 자동 캐시 버스팅 (권장)
이제 프로젝트에 자동 캐시 버스팅 시스템이 적용되었습니다.

**CSS를 수정한 후 모든 사용자에게 즉시 적용하려면:**

1. `django_frontend/config/settings.py` 파일을 엽니다
2. `STATIC_VERSION` 값을 증가시킵니다:
   ```python
   # 정적 파일 캐시 버스팅 버전
   STATIC_VERSION = '11'  # 10 → 11로 변경
   ```
3. Django 서버를 재시작합니다

### 2. 개발자용 브라우저 캐시 강제 삭제

**Chrome/Edge:**
- `Ctrl + Shift + Delete` → "캐시된 이미지 및 파일" 선택 → 삭제
- 또는 `Ctrl + F5` (하드 리프레시)

**Firefox:**
- `Ctrl + Shift + Delete` → "캐시" 선택 → 삭제
- 또는 `Ctrl + F5` (하드 리프레시)

**개발자 도구 사용:**
1. `F12` 키로 개발자 도구 열기
2. Network 탭 선택
3. "Disable cache" 체크박스 선택
4. 개발자 도구가 열린 상태에서 페이지 새로고침

### 3. 템플릿에서 CSS 추가 방법

새로운 CSS 파일을 추가할 때는 반드시 다음 형식을 사용하세요:

```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <!-- ⭐ 반드시 ?v={{ STATIC_VERSION }} 추가 -->
    <link rel="stylesheet" href="{% static 'css/your-style.css' %}?v={{ STATIC_VERSION }}">
</head>
```

### 4. 프로젝트 구조

```
django_frontend/
├── config/
│   ├── settings.py          # STATIC_VERSION = '10' 설정
│   └── context_processors.py # STATIC_VERSION을 템플릿에서 사용 가능하게
├── templates/
│   ├── base.html             # ?v={{ STATIC_VERSION }} 적용됨
│   └── landing.html          # ?v={{ STATIC_VERSION }} 적용됨
└── static/
    └── css/
        ├── style.css
        └── landing.css
```

## 주의사항

1. **절대 하드코딩하지 마세요:**
   ```html
   <!-- ❌ 나쁜 예 -->
   <link rel="stylesheet" href="{% static 'css/style.css' %}?v=10">

   <!-- ✅ 좋은 예 -->
   <link rel="stylesheet" href="{% static 'css/style.css' %}?v={{ STATIC_VERSION }}">
   ```

2. **CSS 수정 후 버전 업데이트를 잊지 마세요:**
   - CSS 파일을 수정했는데 변경사항이 안 보인다면?
   - `settings.py`의 `STATIC_VERSION`을 증가시키세요!

3. **Production 환경:**
   - 배포 전에 `python manage.py collectstatic` 실행
   - 서버 재시작

## 트러블슈팅

### Q: 여전히 이전 CSS가 보여요
A: 다음을 순서대로 시도하세요:
1. `STATIC_VERSION` 값이 증가했는지 확인
2. Django 서버 재시작
3. 브라우저에서 `Ctrl + F5` (하드 리프레시)
4. 브라우저 캐시 완전 삭제

### Q: 일부 사용자만 새 CSS를 못 받아요
A: 해당 사용자에게 브라우저 캐시 삭제를 안내하세요.

### Q: 개발 중 매번 버전을 올려야 하나요?
A: 개발 중에는 개발자 도구의 "Disable cache" 옵션을 사용하세요.
   배포 시에만 버전을 올리면 됩니다.
