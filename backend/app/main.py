"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.routers import auth, upload, search
from app.schemas.common import SuccessResponse

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="SourceLens API",
    description="SaaS product sourcing platform - find cheapest, most trusted suppliers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limit exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, specify actual hosts
)

# Include routers
app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(search.router)


@app.get("/", response_model=SuccessResponse)
@limiter.limit("100/minute")
def root():
    """Root endpoint."""
    return SuccessResponse(
        data={"message": "SourceLens API", "version": "1.0.0"},
        message="Welcome to SourceLens API"
    )


@app.get("/api/health", response_model=SuccessResponse)
@limiter.limit("100/minute")
def health_check():
    """Health check endpoint."""
    return SuccessResponse(
        data={"status": "healthy"},
        message="Service is running"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
