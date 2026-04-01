from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.core.config import settings

security_scheme = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    # jose/pyjwt expect exp as Unix seconds (numeric date)
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def verify_cron_or_jwt(
    x_genpos_cron_secret: str | None = Header(None, alias="X-GenPos-Cron-Secret"),
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
) -> dict:
    """
    For operator/cron endpoints: accept X-GenPos-Cron-Secret when DAILY_BATCH_CRON_SECRET is set,
    otherwise require a normal Bearer JWT.
    """
    if settings.daily_batch_cron_secret and x_genpos_cron_secret == settings.daily_batch_cron_secret:
        return {"sub": "cron", "cron": True}
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization bearer or valid X-GenPos-Cron-Secret",
        )
    try:
        return jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
