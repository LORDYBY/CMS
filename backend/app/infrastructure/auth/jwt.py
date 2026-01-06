# from datetime import datetime, timedelta
# from jose import jwt
# from app.settings import settings

# ACCESS_TOKEN_EXPIRE_MINUTES = 15

# def create_access_token(*, subject: str, tenant_id: str) -> str:
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

#     payload = {
#         "sub": subject,
#         "tenant_id": tenant_id,
#         "exp": expire,
#     }

#     return jwt.encode(
#         payload,
#         settings.JWT_SECRET,
#         algorithm=settings.JWT_ALGO,
#     )


from datetime import datetime, timedelta, timezone
from jose import jwt
from app.settings import settings

ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(*, subject: str, tenant_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": subject,
        "tenant_id": tenant_id,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGO,
    )
