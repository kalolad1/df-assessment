import faiss
import numpy as np
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import sync_engine
from app.models.question_answer import QuestionAnswer


class AnswerQuestionCacheService:
    def __init__(self):
        dim = 1536
        base_index = faiss.IndexFlatIP(dim)
        self._index = faiss.IndexIDMap(base_index)
        self._client = OpenAI(api_key=settings.openai_api_key)

        # Load existing cached questions from database
        self._load_cached_questions()

    def _load_cached_questions(self) -> None:
        """Load all cached questions from database and populate FAISS index."""
        with Session(sync_engine) as session:
            cached_qa_pairs = session.query(QuestionAnswer).all()

            if not cached_qa_pairs:
                print("No cached questions found in database")
                return

            questions = [qa.question for qa in cached_qa_pairs]
            embeddings_response = self._client.embeddings.create(model="text-embedding-3-small", input=questions)
            vectors = np.array([emb.embedding for emb in embeddings_response.data], dtype="float32")
            ids = np.array([qa.id for qa in cached_qa_pairs], dtype=np.int64)

            self._index.add_with_ids(vectors, ids)  # type: ignore

    def get_answer(self, question: str) -> str | None:
        question_embedding = self._client.embeddings.create(model="text-embedding-3-small", input=question)
        query_vector = np.array([question_embedding.data[0].embedding], dtype="float32")
        similarities, ids = self._index.search(query_vector, k=1)  # type: ignore
        if ids[0][0] == -1:
            return None

        threshold = 0.9
        similarity_score = similarities[0][0]
        if similarity_score < threshold:
            return None

        question_id = int(ids[0][0])  # type: ignore
        with Session(sync_engine) as session:
            question_answer = session.get(QuestionAnswer, question_id)
            if question_answer:
                print(f"Cache hit! Question: {question_answer.question}")
                return question_answer.answer

        return None

    async def set_answer(self, question: str, answer: str, db: AsyncSession) -> None:
        question_embedding = self._client.embeddings.create(model="text-embedding-3-small", input=question)
        query_vector = np.array([question_embedding.data[0].embedding], dtype="float32")
        question_answer = QuestionAnswer(question=question, answer=answer)
        db.add(question_answer)
        await db.commit()
        await db.refresh(question_answer)
        question_answer_id = question_answer.id
        self._index.add_with_ids(query_vector, np.array([question_answer_id], dtype=np.int64))  # type: ignore
