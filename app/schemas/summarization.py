from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    """Request schema for medical note summarization.

    Attributes:
        content: The full text of the medical note to be summarized
    """

    content: str = Field(
        min_length=1,
        description="Medical document text to summarize",
        examples=["Patient presents with acute bronchitis..."],
    )


class SummarizeResponse(BaseModel):
    """Response schema for medical note summarization.

    Attributes:
        summary: The generated summary of the medical note
    """

    summary: str = Field(description="Generated summary of the medical note")
