from typing import cast

import faiss
import numpy as np
from openai import OpenAI
from pydantic_ai import Agent
from pydantic_ai.models.fallback import FallbackModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import AsyncSessionLocal, sync_engine
from app.models.document import Document
from app.services.document import get_document


class AnswerQuestionService:
    SYSTEM_PROMPT = """You answer questions"""

    def __init__(self):
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._index = self._create_index()
        self._agent = Agent(
            FallbackModel("gateway/openai:gpt-5.1", "gateway/gemini:gemini-3.0-flash"),
            instructions=self.SYSTEM_PROMPT,
        )

    async def answer_question(self, question: str) -> str:
        user_prompt = f"Please answer the following question:\n\n{question}"
        documents = await self._retrieve_documents(question)
        user_prompt = f"""
        Please answer the following question:
        {question}
        Here are the documents that may be relevant:
        {"\n\n".join([f"{d.title}\n\n{d.content}" for d in documents])}
        In the answer, please provide citations with the document title you may have used to answer the question.
        Place all citations at the end of the answer.
        """
        result = await self._agent.run(user_prompt=user_prompt)
        return result.output

    async def _retrieve_documents(self, question: str) -> list[Document]:
        question_embedding = self._client.embeddings.create(
            model="text-embedding-3-small", input=question
        )
        query_vector = np.array([question_embedding.data[0].embedding], dtype="float32")
        retrieve_documents: tuple[np.ndarray, np.ndarray] = self._index.search(query_vector, k=2)  # type: ignore[reportUnknownMemberType]
        retrieved_document_ids: np.ndarray = cast(np.ndarray, retrieve_documents[1][0])
        document_ids_raw: list[int] = cast(list[int], retrieved_document_ids.tolist())  # type: ignore[reportUnknownMemberType]
        async with AsyncSessionLocal() as session:
            documents = [
                await get_document(session, document_id) for document_id in document_ids_raw
            ]
        return [doc for doc in documents if doc is not None]

    def _create_index(self) -> faiss.Index:
        with Session(sync_engine) as session:
            documents = session.execute(select(Document)).scalars().all()

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
