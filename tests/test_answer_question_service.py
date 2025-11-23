import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.fixtures import load_fixtures
from app.services.answer_question_service import get_answer_question_service


@pytest.mark.asyncio
@pytest.mark.skip
async def test_answer_question(db_session: AsyncSession) -> None:
    await load_fixtures()

    answer_question_service = get_answer_question_service()
    answer = await answer_question_service.answer_question(
        question="What is the difference between Crohn's disease and ulcerative colitis?", db=db_session
    )
    assert answer is not None


@pytest.mark.asyncio
@pytest.mark.skip
async def test_answer_question_cache_hit(db_session: AsyncSession) -> None:
    await load_fixtures()

    answer_question_service = get_answer_question_service()
    answer = await answer_question_service.answer_question(
        question="What is the difference between Crohn's disease and ulcerative colitis?", db=db_session
    )
    assert answer is not None

    cached_answer = await answer_question_service.answer_question(
        question="What is the difference between Crohn's disease and ulcerative colitis?", db=db_session
    )
    assert cached_answer == answer
