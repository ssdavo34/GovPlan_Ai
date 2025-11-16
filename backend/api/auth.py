"""
인증 API 라우터
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.core.database import db_manager
from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)
from backend.core.dependencies import get_current_active_user
from backend.models.user import (
    User,
    UserCreate,
    Token,
    UserUpdate
)


router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate) -> Any:
    """
    신규 사용자 등록

    Args:
        user_in: 사용자 등록 정보

    Returns:
        생성된 사용자 정보

    Raises:
        HTTPException: 이메일이 이미 사용중인 경우
    """
    async with db_manager.get_connection() as conn:
        # 이메일 중복 체크
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            user_in.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다"
            )

        # 비밀번호 해싱
        hashed_password = get_password_hash(user_in.password)

        # 사용자 생성
        user = await conn.fetchrow(
            """
            INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, email, full_name, is_active, is_superuser, created_at, updated_at
            """,
            user_in.email,
            hashed_password,
            user_in.full_name,
            user_in.is_active,
            user_in.is_superuser
        )

    return User(**dict(user))


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    사용자 로그인

    Args:
        form_data: OAuth2 로그인 폼 (username=email, password)

    Returns:
        액세스 토큰 및 리프레시 토큰

    Raises:
        HTTPException: 인증 실패 시
    """
    async with db_manager.get_connection() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            form_data.username  # OAuth2 스펙상 username 필드 사용
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 사용자입니다"
        )

    # 토큰 생성
    access_token = create_access_token(
        data={"sub": user['id'], "email": user['email']}
    )
    refresh_token = create_refresh_token(
        data={"sub": user['id'], "email": user['email']}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str) -> Any:
    """
    액세스 토큰 갱신

    Args:
        refresh_token: 리프레시 토큰

    Returns:
        새로운 액세스 토큰 및 리프레시 토큰

    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    # 리프레시 토큰 검증
    payload = verify_token(refresh_token, token_type="refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    email = payload.get("email")

    if user_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰 페이로드입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 새로운 토큰 생성
    new_access_token = create_access_token(
        data={"sub": user_id, "email": email}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user_id, "email": email}
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    현재 사용자 정보 조회

    Args:
        current_user: 현재 인증된 사용자

    Returns:
        사용자 정보
    """
    return current_user


@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    현재 사용자 정보 업데이트

    Args:
        user_update: 업데이트할 정보
        current_user: 현재 인증된 사용자

    Returns:
        업데이트된 사용자 정보
    """
    async with db_manager.get_connection() as conn:
        # 업데이트할 필드 구성
        update_fields = []
        params = []
        param_count = 1

        if user_update.email is not None:
            # 이메일 중복 체크
            existing_user = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1 AND id != $2",
                user_update.email,
                current_user.id
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 사용중인 이메일입니다"
                )

            update_fields.append(f"email = ${param_count}")
            params.append(user_update.email)
            param_count += 1

        if user_update.full_name is not None:
            update_fields.append(f"full_name = ${param_count}")
            params.append(user_update.full_name)
            param_count += 1

        if user_update.password is not None:
            hashed_password = get_password_hash(user_update.password)
            update_fields.append(f"hashed_password = ${param_count}")
            params.append(hashed_password)
            param_count += 1

        if user_update.is_active is not None:
            update_fields.append(f"is_active = ${param_count}")
            params.append(user_update.is_active)
            param_count += 1

        if not update_fields:
            return current_user

        # updated_at 추가
        update_fields.append(f"updated_at = ${param_count}")
        params.append("NOW()")
        param_count += 1

        # user_id 추가
        params.append(current_user.id)

        # 업데이트 쿼리 실행
        query = f"""
            UPDATE users
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING id, email, full_name, is_active, is_superuser, created_at, updated_at
        """

        # updated_at은 NOW()를 직접 사용하므로 파라미터에서 제거
        params[-2] = None
        query = query.replace(f"updated_at = ${param_count - 1}", "updated_at = NOW()")
        params = [p for p in params if p is not None]

        user = await conn.fetchrow(query, *params)

    return User(**dict(user))
