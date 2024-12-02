from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, status

from config import get_settings
from database import async_session, Base, engine, get_db
from export.routers import router as export_router
from indexes.routers import router as indexes_router
from logger import get_logger
from prices.routers import router as prices_router
from stocks.routers import router as stocks_router
from tasks.routers import router as tasks_router
from tasks.scheduler import create_startup_tasks, execute_scheduled_tasks

settings = get_settings()

logger = get_logger(__name__)
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_db.setup()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        await create_startup_tasks(db=session)
        await execute_scheduled_tasks(db=session)
    scheduler.start()
    yield
    scheduler.shutdown()
    await get_db.close_db()


app = FastAPI(lifespan=lifespan)


@app.get("/health", status_code=status.HTTP_200_OK)
async def get_status():
    return {"healthy": True}


app.include_router(stocks_router)
app.include_router(tasks_router)
app.include_router(prices_router)
app.include_router(indexes_router)
app.include_router(export_router)

scheduler.add_job(create_startup_tasks, "interval", [get_db()], hours=24)
scheduler.add_job(execute_scheduled_tasks, "interval", [get_db()], hours=1)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)  # nosec B104
