import pytest

from app.services.extract_structured_service import get_extract_structured_service


@pytest.mark.asyncio
@pytest.mark.skip
async def test_extract_structured(medical_note: str) -> None:
    extract_structured_service = get_extract_structured_service()
    structured_data = await extract_structured_service.extract_structured(medical_note)
    assert structured_data is not None
