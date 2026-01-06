"""
LIMS-ELN Integration Platform
FastAPI Application Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.routes import sync, validate, health, nlp
from app.database.postgres import engine, Base
from app.database.mongodb import mongodb

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    logger.info("Initializing LIMS-ELN Integration Platform")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized")
        
        await mongodb.client.admin.command('ping')
        logger.info("MongoDB connection established")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise
    
    yield
    
    logger.info("Shutting down application")
    await mongodb.client.close()


app = FastAPI(
    title="LIMS-ELN Integration Platform",
    description="Middleware for laboratory information systems integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": str(request.url)}
    )


app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["Synchronization"])
app.include_router(validate.router, prefix="/api/v1/validate", tags=["Validation"])
app.include_router(nlp.router, prefix="/api/v1/nlp", tags=["NLP"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LIMS-ELN Integration Platform API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
