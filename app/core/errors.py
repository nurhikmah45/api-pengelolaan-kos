"""Exception domain + handler terpusat dengan format error seragam."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"


class BusinessRuleError(AppError):
    status_code = 400
    code = "BUSINESS_RULE_VIOLATION"


def _body(status: str, code: str, path: str, details) -> dict:
    return {"status": status, "code": code, "path": path, "details": details}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_body("error", exc.code, request.url.path, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        details = [
            {"field": " -> ".join(str(p) for p in e["loc"]), "msg": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_body("error", "VALIDATION_ERROR", request.url.path, details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        codes = {401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
        return JSONResponse(
            status_code=exc.status_code,
            content=_body("error", codes.get(exc.status_code, "HTTP_ERROR"), request.url.path, exc.detail),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        # Jangan bocorkan detail internal ke klien.
        return JSONResponse(
            status_code=500,
            content=_body("error", "INTERNAL_ERROR", request.url.path, "Terjadi kesalahan pada server."),
        )
