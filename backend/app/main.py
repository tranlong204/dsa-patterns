from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import problems, user_progress, auth
from app.config import settings

app = FastAPI(title="DSA Patterns API", version="1.0.0")

# Enable CORS for frontend using configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(problems.router, prefix="/api/problems", tags=["problems"])
app.include_router(user_progress.router, prefix="/api/user", tags=["user"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "DSA Patterns API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

