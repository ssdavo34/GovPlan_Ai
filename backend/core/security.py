"""
보안 유틸리티 (JWT, 비밀번호 해싱)
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.core.config import settings


# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# JWT 설정
SECRET_KEY = getattr(settings, 'secret_key', 'your-secret-key-change-this-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'access_token_expire_minutes', 30)
REFRESH_TOKEN_EXPIRE_DAYS = getattr(settings, 'refresh_token_expire_days', 7)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증

    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호

    Returns:
        검증 성공 여부
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    비밀번호 해싱

    Args:
        password: 평문 비밀번호

    Returns:
        해시된 비밀번호
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    액세스 토큰 생성

    Args:
        data: 토큰에 포함할 데이터 (보통 user_id, email 등)
        expires_delta: 만료 시간 (기본값: 30분)

    Returns:
        JWT 액세스 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    리프레시 토큰 생성

    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 만료 시간 (기본값: 7일)

    Returns:
        JWT 리프레시 토큰
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT 토큰 디코딩

    Args:
        token: JWT 토큰

    Returns:
        디코딩된 페이로드 또는 None (실패 시)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    JWT 토큰 검증

    Args:
        token: JWT 토큰
        token_type: 토큰 타입 ("access" 또는 "refresh")

    Returns:
        디코딩된 페이로드 또는 None (실패 시)
    """
    payload = decode_token(token)

    if payload is None:
        return None

    # 토큰 타입 검증
    if payload.get("type") != token_type:
        return None

    return payload
