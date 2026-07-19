from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.facilities import router as facility_router
from app.routers.facility_schedule import router as facilityschedule_router
from app.routers.timeslot import router as timeslot_router
from app.routers.booking import router as booking_router

from app.core.redis_client import init_redis, close_redis
from app.core.logger import setup_logging



@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    await init_redis()

    yield  

    await close_redis()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(facility_router)
app.include_router(facilityschedule_router)
app.include_router(timeslot_router)
app.include_router(booking_router)