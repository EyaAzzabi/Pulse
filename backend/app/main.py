import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import actions, admin, auth, copilot, financial, forecast, notifications, onboarding, organizations, recommendations, simulations
from app.core.config import get_settings
from app.db.session import Base, engine
from app import models  # noqa: F401  ensures all models are registered on Base.metadata

logging.basicConfig(level=logging.INFO)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(organizations.router)
app.include_router(onboarding.router)
app.include_router(financial.router)
app.include_router(forecast.router)
app.include_router(simulations.router)
app.include_router(copilot.router)
app.include_router(actions.router)
app.include_router(notifications.router)
app.include_router(recommendations.router)
