"""
FastAPI 의존성 함수
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.core.security import verify_token
from backend.core.database import db_manager
from backend.models.user import User, TokenPayload


# HTTP Bearer 토큰 스키마
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    현재 인증된 사용자 가져오기

    Args:
        credentials: HTTP Bearer 토큰

    Returns:
        User 객체

    Raises:
        HTTPException: 인증 실패 시
    """
    token = credentials.credentials

    # 토큰 검증
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰 페이로드입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 데이터베이스에서 사용자 조회
    async with db_manager.get_connection() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1",
            user_id
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )

    # User 모델로 변환
    user_dict = dict(user)
    return User(**user_dict)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    현재 활성화된 사용자 가져오기

    Args:
        current_user: 현재 사용자

    Returns:
        활성화된 User 객체

    Raises:
        HTTPException: 비활성화된 사용자인 경우
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 사용자입니다"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    현재 슈퍼유저 가져오기

    Args:
        current_user: 현재 사용자

    Returns:
        슈퍼유저 User 객체

    Raises:
        HTTPException: 슈퍼유저가 아닌 경우
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 부족합니다"
        )
    return current_user
