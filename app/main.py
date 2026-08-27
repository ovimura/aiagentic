from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import Item  # noqa: F401  — register tables on Base.metadata
from app.routers import items


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Items CRUD API",
    description="FastAPI CRUD service for Cloud Run",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(items.router)


@app.get("/")
def root():
    return {"message": "Items CRUD API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
