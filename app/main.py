from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.routes import router
from app.db.session import async_engine
from app.fixtures import load_fixtures
from app.models.document import Base

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await load_fixtures()
    yield


app = FastAPI(title="Deerfield Assessment API Backend", lifespan=lifespan)

app.include_router(router)
