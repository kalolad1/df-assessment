import pytest

from app.services.summarization_service import get_summarization_service


@pytest.mark.asyncio
@pytest.mark.skip
async def test_summarize_note() -> None:
    summarization_service = get_summarization_service()
    summary = await summarization_service.summarize(
        "Patient presents with persistent cough, fever, and chest discomfort. Physical examination reveals wheezing and crackling sounds in lungs. Diagnosed with acute bronchitis. Prescribed azithromycin 500mg daily for 5 days and advised bed rest."
    )
    assert summary is not None
