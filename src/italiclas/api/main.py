"""REST API Main Application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware import cors

from italiclas import etl, ml
from italiclas.api.routers import ping, predict
from italiclas.config import cfg, info


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """Manage the application lifespan."""
    # : Startup
    etl.fetch_raw_data()
    etl.preprocess_raw_data()
    ml.train()

    yield

    # : Shutdown
    # nothing to do - to remove artifacts use Makefile rules


# : Setup FastAPI Application
app = FastAPI(
    title=info.name,
    version=info.version,
    description=info.description,
    docs_url=f"{cfg.api_base_endpoint}/docs",
    openapi_url=f"{cfg.api_base_endpoint}/openapi.json",
    lifespan=lifespan,
)


# : Add Middlewares
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=tuple(cfg.allowed_hosts),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# : Add Routes
router = APIRouter(prefix=cfg.api_base_endpoint)
router.include_router(ping.router)
router.include_router(predict.router)
app.include_router(router)
