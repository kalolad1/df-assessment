"""Fixture loader for seeding the database with initial data."""

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.document import Document
from app.services.document import create_document


async def load_fixtures_from_json(file_path: Path) -> list[dict[str, str]]:
    """Load fixture data from a JSON file.

    Args:
        file_path: Path to the JSON file containing fixture data

    Returns:
        List of dictionaries containing document data
    """
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    return data


async def seed_documents(db: AsyncSession) -> tuple[int, int]:
    """Seed the database with document fixtures.

    Checks if documents already exist by title to avoid duplicates.

    Args:
        db: Database session

    Returns:
        Tuple of (created_count, skipped_count)
    """
    fixtures_dir = Path(__file__).parent
    documents_file = fixtures_dir / "documents.json"

    if not documents_file.exists():
        return 0, 0

    documents_data = await load_fixtures_from_json(documents_file)

    created_count = 0
    skipped_count = 0

    for doc_data in documents_data:
        title = doc_data.get("title", "")
        content = doc_data.get("content", "")

        if not title or not content:
            continue

        # Check if document with this title already exists
        result = await db.execute(select(Document).where(Document.title == title))
        existing_doc = result.scalar_one_or_none()

        if existing_doc is None:
            await create_document(db, title=title, content=content)
            created_count += 1
        else:
            skipped_count += 1

    return created_count, skipped_count


async def load_fixtures() -> None:
    """Load all fixtures into the database.

    This function is called during application startup.
    """
    async with AsyncSessionLocal() as db:
        created, skipped = await seed_documents(db)
        if created > 0:
            print(f"✓ Loaded {created} fixture document(s)")
        if skipped > 0:
            print(f"⊙ Skipped {skipped} existing document(s)")
