from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse


class HTTPSRedirectWithProxyMiddleware(BaseHTTPMiddleware):
    """Redirect HTTP requests to HTTPS, while respecting reverse-proxy headers."""

    async def dispatch(self, request: Request, call_next):
        forwarded_proto = request.headers.get("x-forwarded-proto", "").lower()
        is_https = request.url.scheme == "https" or forwarded_proto == "https"

        if not is_https:
            https_url = str(request.url.replace(scheme="https"))
            return RedirectResponse(url=https_url, status_code=307)

        return await call_next(request)
