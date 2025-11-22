import pytest

from app.fixtures import load_fixtures
from app.services.answer_question_service import get_answer_question_service


@pytest.mark.asyncio
@pytest.mark.skip
async def test_answer_question() -> None:
    await load_fixtures()

    answer_question_service = get_answer_question_service()
    answer = await answer_question_service.answer_question(
        "What is the difference between Crohn's disease and ulcerative colitis?"
    )
    assert answer is not None
