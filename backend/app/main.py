from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.middleware import SimpleRateLimitMiddleware
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.bootstrap import bootstrap_admin_user
from app.services.schema_compat import run_schema_compat

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_schema_compat(db)
        bootstrap_admin_user(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.add_middleware(SimpleRateLimitMiddleware, requests_per_minute=240)


@app.get('/healthz')
def health_check():
    return {'status': 'ok'}


app.include_router(api_router, prefix=settings.api_v1_prefix)
