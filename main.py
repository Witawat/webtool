import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.config import settings
from core.errors import AppError
from core.i18n import t
from core.paths import STATIC_DIR, TEMPLATES_DIR
from routers import home

logger = logging.getLogger("webtool")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.version)

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(home.router)

    @app.exception_handler(AppError)
    async def _app_error_handler(request: Request, exc: AppError):
        from routers import get_lang

        return JSONResponse(
            status_code=exc.status,
            content={"ok": False, "error": exc.to_dict(get_lang(request))},
        )

    @app.exception_handler(Exception)
    async def _generic_error_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled error on %s %s", request.method, request.url.path
        )
        from routers import get_lang

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": {
                    "code": "INTERNAL",
                    "message": t(get_lang(request), "err.INTERNAL"),
                },
            },
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
