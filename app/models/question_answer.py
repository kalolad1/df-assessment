from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.document import Base


class QuestionAnswer(Base):
    __tablename__ = "question_answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
