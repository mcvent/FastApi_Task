from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from src.api.users import router as users_router
from src.api.categories import router as categories_router
from src.api.locations import router as locations_router
from src.api.comments import router as comments_router
from src.api.posts import router as posts_router
from src.exceptions import AppException


def create_app() -> FastAPI:
    app = FastAPI(root_path="/api/v1")

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

    app.include_router(users_router, prefix="/users", tags=["Users"])
    app.include_router(categories_router, prefix="/categories", tags=["Categories"])
    app.include_router(locations_router, prefix="/locations", tags=["Locations"])
    app.include_router(comments_router, prefix="/comments", tags=["Comments"])
    app.include_router(posts_router, prefix="/posts", tags=["Posts"])

    return app