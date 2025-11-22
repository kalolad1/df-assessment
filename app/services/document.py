"""Document service layer.

This module provides business logic for document operations,
wrapping the database layer for document management.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


async def create_document(db: AsyncSession, title: str, content: str) -> Document:
    """Create a new document in the database.

    Args:
        db: Database session
        title: Document title
        content: Document content

    Returns:
        The created Document instance
    """
    new_doc = Document(title=title, content=content)
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return new_doc


async def get_document(db: AsyncSession, document_id: int) -> Document | None:
    """Retrieve a document from the database."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    return result.scalar_one_or_none()


async def get_all_documents(db: AsyncSession) -> list[Document]:
    """Retrieve all documents from the database.

    Args:
        db: Database session

    Returns:
        List of all Document instances
    """
    result = await db.execute(select(Document))
    return list(result.scalars().all())
