from typing import cast

import faiss
import numpy as np
from openai import OpenAI
from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.singleton import SingletonMeta
from app.db.session import get_db_sync
from app.models.document import Document
from app.services.answer_question_cache_service import AnswerQuestionCacheService
from app.services.document_service import get_document


class AnswerQuestionService(metaclass=SingletonMeta):
    SYSTEM_PROMPT = """You answer questions"""

    def __init__(self):
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._index = self._create_index()
        self._cache_service = AnswerQuestionCacheService()
        self._agent = Agent(
            FallbackModel("gateway/openai:gpt-5.1", "gateway/gemini:gemini-3.0-flash"),
            instructions=self.SYSTEM_PROMPT,
        )

    async def answer_question(self, question: str, db: AsyncSession) -> str:
        cached_answer = self._cache_service.get_answer(question=question)
        if cached_answer is not None:
            return cached_answer

        documents = await self._retrieve_documents(question=question, db=db)
        user_prompt = self._get_user_prompt(question=question, documents=documents)
        result = await self._agent.run(user_prompt=user_prompt)

        await self._cache_service.set_answer(question=question, answer=result.output, db=db)
        return result.output

    def _get_user_prompt(self, question: str, documents: list[Document]) -> str:
        return f"""
        Please answer the following question:
        {question}
        Here are the documents that may be relevant:
        {"\n\n".join([f"{d.title}\n\n{d.content}" for d in documents])}
        In the answer, please provide citations with the document title you may have used to answer the question.
        Place all citations at the end of the answer.
        """

    async def _retrieve_documents(self, question: str, db: AsyncSession) -> list[Document]:
        question_embedding = self._client.embeddings.create(model="text-embedding-3-small", input=question)
        query_vector = np.array([question_embedding.data[0].embedding], dtype="float32")
        retrieve_documents: tuple[np.ndarray, np.ndarray] = self._index.search(query_vector, k=2)  # type: ignore[reportUnknownMemberType]
        retrieved_document_ids: np.ndarray = cast(np.ndarray, retrieve_documents[1][0])
        document_ids_raw: list[int] = cast(list[int], retrieved_document_ids.tolist())  # type: ignore[reportUnknownMemberType]
        documents = [await get_document(db, document_id) for document_id in document_ids_raw]
        return [doc for doc in documents if doc is not None]

    def _create_index(self) -> faiss.Index:
        db = next(get_db_sync())

        documents = db.execute(select(Document)).scalars().all()
        texts = [f"{d.title}\n\n{d.content}" for d in documents]
        ids = np.array([d.id for d in documents], dtype=np.int64)

        resp = self._client.embeddings.create(model="text-embedding-3-small", input=texts)
        vectors = np.array([item.embedding for item in resp.data], dtype="float32")
        dim = vectors.shape[1]

        base_index = faiss.IndexFlatIP(dim)
        index = faiss.IndexIDMap(base_index)
        index.add_with_ids(vectors, ids)  # type: ignore[arg-type]
        return index


def get_answer_question_service() -> AnswerQuestionService:
    return AnswerQuestionService()
