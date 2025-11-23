import pytest

from app.services.extract_structured_service import get_extract_structured_service


@pytest.mark.skip
def test_extract_structured(medical_note: str) -> None:
    extract_structured_service = get_extract_structured_service()
    structured_data = extract_structured_service.extract_structured(medical_note)
    assert structured_data is not None
