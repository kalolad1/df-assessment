from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.main import app
from app.services.answer_question_service import AnswerQuestionService, get_answer_question_service
from app.services.summarization_service import SummarizationService, get_summarization_service


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_documents_empty(client: AsyncClient) -> None:
    response = await client.get("/documents")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_and_get_documents(client: AsyncClient) -> None:
    # Create a document
    create_payload = {"title": "Test Document", "content": "This is test content"}
    create_response = await client.post("/documents", json=create_payload)

    assert create_response.status_code == 201
    body = create_response.json()
    assert body["id"] > 0
    assert body["title"] == create_payload["title"]
    assert body["content"] == create_payload["content"]

    # Get all documents
    list_response = await client.get("/documents")
    assert list_response.status_code == 200
    ids = list_response.json()
    assert body["id"] in ids


@pytest.mark.asyncio
async def test_create_document_validation_empty_title(client: AsyncClient) -> None:
    response = await client.post("/documents", json={"title": "", "content": "content"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_document_validation_empty_content(client: AsyncClient) -> None:
    response = await client.post("/documents", json={"title": "title", "content": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_document_validation_missing_field(client: AsyncClient) -> None:
    response = await client.post("/documents", json={"title": "title"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_summarize_note_success(client: AsyncClient) -> None:
    """Test successful medical note summarization."""
    mock_summary = (
        "Patient diagnosed with acute bronchitis. "
        "Prescribed antibiotics and rest. Follow-up in 1 week."
    )
    mock_summarization_service = AsyncMock(spec=SummarizationService)
    mock_summarization_service.summarize.return_value = mock_summary
    app.dependency_overrides[get_summarization_service] = lambda: mock_summarization_service

    response = await client.post(
        "/summarize_note",
        json={
            "content": (
                "Patient presents with persistent cough, fever, and chest discomfort. "
                "Physical examination reveals wheezing and crackling sounds in lungs. "
                "Diagnosed with acute bronchitis. "
                "Prescribed azithromycin 500mg daily for 5 days and advised bed rest."
            )
        },
    )
    assert response.status_code == 200
    assert response.json()["summary"] == mock_summary


@pytest.mark.asyncio
async def test_answer_question_success(client: AsyncClient) -> None:
    """Test successful question answering."""
    mock_answer = "Crohn's disease is a chronic inflammatory bowel disease that can affect any part of the digestive system. Ulcerative colitis is a chronic inflammatory bowel disease that only affects the large intestine."
    mock_answer_question_service = AsyncMock(spec=AnswerQuestionService)
    mock_answer_question_service.answer_question.return_value = mock_answer
    app.dependency_overrides[get_answer_question_service] = lambda: mock_answer_question_service

    response = await client.post(
        "/answer_question",
        json={"question": "What is the difference between Crohn's disease and ulcerative colitis?"},
    )
    assert response.status_code == 200
    assert response.json()["answer"] == mock_answer
