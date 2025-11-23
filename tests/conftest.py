import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.session import get_db
from app.main import app
from app.models.document import Base

TEST_DB_URL = "sqlite+aiosqlite:///./data/test.db"


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    os.makedirs("data", exist_ok=True)
    engine = create_async_engine(TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def medical_note() -> str:
    note = """
    SOAP Note - Encounter Date: 2023-10-26
    Patient: Mr. Alan Turning
    Age: 50

    S: Pt presents today for annual physical check-up. No chief complaints. Reports generally good health, denies chest pain, SOB, HA, dizziness. Family hx of elevated cholesterol (dad), no significant personal PMH issues reported. States routine exercise (~2x/wk), balanced diet but with occasional fast-food. Denies tobacco use, reports occasional ETOH socially.

    O:
    Vitals:

    BP: 128/82 mmHg
    HR: 72 bpm, regular
    RR: 16 breaths/min
    Temp: 98.2Â°F oral
    Ht: 5'10", Wt: 192 lbs, BMI: 27.5 (overweight)
    General appearance: Alert, NAD, pleasant and cooperative.
    Skin: Clear, normal moisture/turgor
    HEENT: PERRLA, EOMI, no scleral icterus. Oral mucosa moist, throat clear, no erythema
    CV: Regular rate & rhythm, no murmurs, rubs or gallops
    Lungs: CTA bilaterally, no wheezing or crackles
    ABD: Soft, NT/ND, bowel sounds normal
    Neuro: CN II-XII intact, normal strength & sensation bilat
    EXT: No edema, pulses +2 bilaterally
    Labs ordered: CBC, CMP, Lipid panel

    A:

    Adult annual health exam, generally healthy
    Possible overweight (BMI 27.5), recommend lifestyle modifications
    Family hx of hyperlipidemia, screening initiated
    Diagnosis: Hyperlipidemia
    P:

    Advised pt on healthier diet, increasing weekly exercise frequency to at least 3-4 times/week
    Scheduled follow-up visit to review lab results and cholesterol levels in approx. 5 months
    Routine annual influenza vaccine administered today - tolerated well
    Prescribed 10mg of simvastatin daily

    Signed:
    Dr. Mark Reynolds, MD
    Internal Medicine
    """
    return note
