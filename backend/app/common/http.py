# app/common/http.py
from fastapi import Request

def get_public_base_url(request: Request) -> str:
    """
    Resolve public base URL correctly behind reverse proxies (NGINX).
    """
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.headers.get("host"))
    return f"{proto}://{host}"
