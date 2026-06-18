from fastapi import APIRouter

from app.api.routes import (
    analytics,
    auth,
    backup,
    categories,
    dashboard,
    events,
    goals,
    scheduler,
    search,
    settings,
    tasks,
    templates,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(events.router)
api_router.include_router(tasks.router)
api_router.include_router(goals.router)
api_router.include_router(templates.router)
api_router.include_router(search.router)
api_router.include_router(scheduler.router)
api_router.include_router(settings.router)
api_router.include_router(dashboard.router)
api_router.include_router(analytics.router)
api_router.include_router(backup.router)
