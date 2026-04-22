from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from src.api.users import public_router as users_public_router
from src.api.users import protected_router as users_protected_router
from src.api.categories import public_router as categories_public_router
from src.api.categories import protected_router as categories_protected_router
from src.api.locations import public_router as locations_public_router
from src.api.locations import protected_router as locations_protected_router
from src.api.comments import public_router as comments_public_router
from src.api.comments import protected_router as comments_protected_router
from src.api.posts import public_router as posts_public_router
from src.api.posts import protected_router as posts_protected_router
from src.exceptions import AppException
from src.api.auth import router as auth_router
import logging
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        docs_url="/docs",
        title="FastAPI App",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Глобальный обработчик AppException
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        status_code_map = {
            "not_found": status.HTTP_404_NOT_FOUND,
            "conflict": status.HTTP_409_CONFLICT,
            "validation_error": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "database_error": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "db_connection_error": status.HTTP_503_SERVICE_UNAVAILABLE,
            "db_query_error": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "db_integrity_error": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "forbidden": status.HTTP_403_FORBIDDEN,
        }

        status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                    "path": str(request.url.path)
                }
            }
        )

    # Глобальный обработчик валидации Pydantic (422)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Ошибка валидации данных",
                    "details": {
                        "errors": [
                            {
                                "field": ".".join(str(x) for x in err["loc"]),
                                "message": err["msg"],
                                "type": err["type"]
                            }
                            for err in exc.errors()
                        ],
                        "path": str(request.url.path)
                    }
                }
            }
        )

    # Глобальный обработчик всех остальных исключений
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "Внутренняя ошибка сервера",
                    "details": {
                        "error_type": type(exc).__name__,
                        "path": str(request.url.path)
                    }
                }
            }
        )

    # Регистрируем роутеры
    app.include_router(auth_router)
    app.include_router(users_public_router)
    app.include_router(users_protected_router)
    app.include_router(categories_public_router)
    app.include_router(categories_protected_router)
    app.include_router(locations_public_router)
    app.include_router(locations_protected_router)
    app.include_router(comments_public_router)
    app.include_router(comments_protected_router)
    app.include_router(posts_public_router)
    app.include_router(posts_protected_router)

    # Настройка OpenAPI для Swagger с Bearer авторизацией
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        from fastapi.openapi.utils import get_openapi

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # Добавляем схему безопасности
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Введите JWT токен (без слова Bearer)"
            }
        }

        for path, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                # Для всех методов в категориях, кроме GET, добавляем security
                if path.startswith("/categories") and method in ["post", "patch", "delete"]:
                    operation["security"] = [{"BearerAuth": []}]
                # Для остальных защищенных эндпоинтов
                elif method in ["post", "patch", "delete", "put"]:
                    # Проверяем, не публичный ли это эндпоинт
                    if not path.startswith("/auth/login") and not path.startswith("/users/register"):
                        operation["security"] = [{"BearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    # Отладка запросов при ошибках
    # @app.middleware("http")
    # async def debug_auth_middleware(request: Request, call_next):
    #     print(f"\nREQUEST: {request.method} {request.url.path}")
    #     print(f"HEADERS: {dict(request.headers)}")
    #
    #     auth_header = request.headers.get("Authorization")
    #     if auth_header:
    #         print(f"Authorization header: {auth_header[:50]}...")
    #     else:
    #         print(f"No Authorization header!")
    #
    #     response = await call_next(request)
    #     return response

    return app