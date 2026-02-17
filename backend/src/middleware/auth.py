from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from src.config import settings
from typing import Optional

# Security scheme for Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        user_id: UUID string of authenticated user

    Raises:
        HTTPException: 401 if token is invalid or missing

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user)):
            # user_id is automatically injected
            return {"user_id": user_id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials

        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # Extract user_id from token payload
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        return user_id

    except JWTError:
        raise credentials_exception


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[str]:
    """
    Optional authentication dependency.

    Returns user_id if valid token provided, None otherwise.
    Does not raise exception for missing/invalid tokens.

    Usage:
        @app.get("/optional-auth")
        async def optional_route(user_id: Optional[str] = Depends(get_current_user_optional)):
            if user_id:
                # User is authenticated
                pass
            else:
                # User is not authenticated
                pass
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: Optional[str] = payload.get("sub")
        return user_id
    except JWTError:
        return None


def create_access_token(user_id: str) -> str:
    """
    Create JWT access token for user.

    Note: This is a helper function for Better-Auth integration.
    Better-Auth typically handles token creation, but this is provided
    for testing or custom authentication flows.

    Args:
        user_id: User UUID string

    Returns:
        JWT token string
    """
    from datetime import datetime, timedelta

    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode = {
        "sub": user_id,
        "exp": expire
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt
