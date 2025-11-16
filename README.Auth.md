# 인증 및 권한 관리 시스템

GovPlan_AI의 JWT 기반 인증 및 권한 관리 시스템 가이드입니다.

## 목차

- [개요](#개요)
- [인증 시스템 구조](#인증-시스템-구조)
- [데이터베이스 설정](#데이터베이스-설정)
- [API 엔드포인트](#api-엔드포인트)
- [사용 예시](#사용-예시)
- [보호된 라우트 작성](#보호된-라우트-작성)

## 개요

### 주요 기능

- JWT (JSON Web Token) 기반 인증
- 액세스 토큰 / 리프레시 토큰 방식
- 비밀번호 bcrypt 해싱
- 사용자 역할 관리 (일반 사용자, 슈퍼유저)
- 보호된 라우트 미들웨어

### 기술 스택

- **FastAPI**: 웹 프레임워크
- **python-jose**: JWT 토큰 생성 및 검증
- **passlib**: 비밀번호 해싱 (bcrypt)
- **PostgreSQL**: 사용자 정보 저장

## 인증 시스템 구조

```
backend/
├── api/
│   └── auth.py              # 인증 API 엔드포인트
├── core/
│   ├── security.py          # JWT 및 비밀번호 유틸리티
│   ├── dependencies.py      # 인증 의존성 함수
│   └── config.py            # JWT 설정
├── models/
│   └── user.py              # 사용자 모델
└── migrations/
    └── 001_create_users_table.sql  # 사용자 테이블 생성
```

## 데이터베이스 설정

### 1. 사용자 테이블 생성

```bash
# PostgreSQL에 접속
psql -U postgres -d govplan_ai

# 마이그레이션 실행
\i backend/migrations/001_create_users_table.sql
```

### 2. 기본 사용자 계정

마이그레이션 실행 시 자동으로 생성됩니다:

#### 슈퍼유저 (관리자)
- **이메일**: `admin@govplan.ai`
- **비밀번호**: `admin123`
- **권한**: 슈퍼유저

#### 테스트 사용자
- **이메일**: `test@govplan.ai`
- **비밀번호**: `testuser123`
- **권한**: 일반 사용자

**⚠️ 보안 주의**: 프로덕션 환경에서는 반드시 비밀번호를 변경하세요!

## API 엔드포인트

### 1. 회원가입

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "홍길동"
}
```

**응답**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "홍길동",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00"
}
```

### 2. 로그인

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@govplan.ai&password=admin123
```

**응답**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. 토큰 갱신

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 4. 현재 사용자 정보 조회

```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 5. 사용자 정보 수정

```http
PUT /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "full_name": "새로운 이름",
  "password": "newpassword123"
}
```

## 사용 예시

### Python (requests)

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# 1. 로그인
response = requests.post(
    f"{API_URL}/auth/login",
    data={
        "username": "admin@govplan.ai",
        "password": "admin123"
    }
)
tokens = response.json()
access_token = tokens["access_token"]

# 2. 인증이 필요한 API 호출
headers = {
    "Authorization": f"Bearer {access_token}"
}

# 현재 사용자 정보
user = requests.get(f"{API_URL}/auth/me", headers=headers).json()
print(f"로그인 사용자: {user['email']}")

# 보호된 엔드포인트 호출
response = requests.get(f"{API_URL}/companies", headers=headers)
```

### JavaScript (Fetch API)

```javascript
const API_URL = 'http://localhost:8000/api/v1';

// 1. 로그인
async function login(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
  });

  const tokens = await response.json();
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
  return tokens;
}

// 2. 인증이 필요한 API 호출
async function fetchProtectedData() {
  const token = localStorage.getItem('access_token');

  const response = await fetch(`${API_URL}/companies`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
}

// 3. 토큰 갱신
async function refreshToken() {
  const refresh_token = localStorage.getItem('refresh_token');

  const response = await fetch(`${API_URL}/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token })
  });

  const tokens = await response.json();
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
}
```

### cURL

```bash
# 로그인
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@govplan.ai&password=admin123"

# 현재 사용자 정보
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 보호된 라우트 작성

### 1. 기본 인증 (로그인 필요)

```python
from fastapi import APIRouter, Depends
from backend.core.dependencies import get_current_active_user
from backend.models.user import User

router = APIRouter()

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    """로그인한 사용자만 접근 가능"""
    return {"message": f"안녕하세요, {current_user.email}님!"}
```

### 2. 슈퍼유저 전용

```python
from backend.core.dependencies import get_current_superuser

@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser)
):
    """슈퍼유저만 접근 가능"""
    # 사용자 삭제 로직
    return {"message": "사용자가 삭제되었습니다"}
```

### 3. 선택적 인증

```python
from typing import Optional

@router.get("/public-or-private")
async def optional_auth(
    current_user: Optional[User] = Depends(get_current_user)
):
    """로그인 없이도 접근 가능, 로그인 시 추가 정보 제공"""
    if current_user:
        return {"message": f"환영합니다, {current_user.email}님!"}
    else:
        return {"message": "게스트로 접속하셨습니다"}
```

## 보안 설정

### 환경 변수 (.env)

```bash
# JWT 시크릿 키 (프로덕션에서 반드시 변경!)
SECRET_KEY=your-super-secret-key-change-this-in-production

# 토큰 만료 시간
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24시간
REFRESH_TOKEN_EXPIRE_DAYS=7       # 7일
```

### 보안 체크리스트

- [ ] `SECRET_KEY`를 강력한 랜덤 문자열로 변경
- [ ] 기본 관리자 비밀번호 변경
- [ ] HTTPS 사용 (프로덕션)
- [ ] CORS 설정 확인
- [ ] 비밀번호 정책 강화 (최소 길이, 복잡도)
- [ ] Rate limiting 설정
- [ ] 로그인 시도 제한

## 토큰 만료 처리

### 프론트엔드에서 자동 갱신

```javascript
async function apiCall(url, options = {}) {
  let token = localStorage.getItem('access_token');

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });

    // 401 Unauthorized - 토큰 만료
    if (response.status === 401) {
      // 리프레시 토큰으로 갱신 시도
      await refreshToken();
      token = localStorage.getItem('access_token');

      // 재시도
      return await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${token}`
        }
      });
    }

    return response;
  } catch (error) {
    console.error('API 호출 실패:', error);
    throw error;
  }
}
```

## 문제 해결

### 401 Unauthorized 오류

- 토큰이 만료되었거나 유효하지 않음
- 리프레시 토큰으로 갱신 시도
- 갱신 실패 시 재로그인 필요

### 403 Forbidden 오류

- 권한이 부족함
- 슈퍼유저 권한이 필요한 엔드포인트

### 비밀번호 재설정이 필요한 경우

현재 구현에는 비밀번호 재설정 기능이 없습니다. 필요 시 다음 기능 추가:
- 이메일 인증 기반 비밀번호 재설정
- 임시 비밀번호 발급

## 다음 단계

- [ ] 이메일 인증 (회원가입 시)
- [ ] 비밀번호 재설정 기능
- [ ] 2단계 인증 (2FA)
- [ ] 소셜 로그인 (Google, Kakao 등)
- [ ] API Rate Limiting
- [ ] 감사 로그 (로그인 기록)
