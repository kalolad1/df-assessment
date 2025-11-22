from pydantic import BaseModel, Field


class AnswerQuestionRequest(BaseModel):
    question: str = Field(min_length=1)


class AnswerQuestionResponse(BaseModel):
    answer: str
