"""
三国演义 · 全球三市数据可视化系统
Main Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    settings = get_settings()
    print(f"\n{'='*60}")
    print(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"  Environment: {settings.APP_ENV}")
    print(f"  API Docs: http://localhost:8000/docs")
    print(f"{'='*60}\n")

    # Initialize database
    init_db()

    # Start scheduler if enabled
    if settings.SCHEDULER_ENABLED:
        from app.scheduler.jobs import start_scheduler
        start_scheduler()

    yield

    # Shutdown
    if settings.SCHEDULER_ENABLED:
        from app.scheduler.jobs import stop_scheduler
        stop_scheduler()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="全球三市（A股/港股/美股）数据可视化与投资决策系统",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/docs",
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.APP_VERSION}

    return app


app = create_app()
