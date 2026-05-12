"""create extraction workbench tables

Revision ID: 20260512_0002
Revises: 20260508_0001
Create Date: 2026-05-12 00:00:00
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "20260512_0002"
down_revision: str | Sequence[str] | None = "20260508_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=512), nullable=False),
        sa.Column("document_type", sa.String(length=128), nullable=True),
        sa.Column("status", sa.Enum("uploaded", "processing", "extracted", "failed", name="document_status"), nullable=False),
        sa.Column("upload_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "document_extractions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("structured_json", sa.JSON(), nullable=False),
        sa.Column("extraction_metadata", sa.JSON(), nullable=False),
        sa.Column("extraction_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("extraction_id", sa.UUID(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("section_name", sa.String(length=255), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("chunk_type", sa.String(length=64), nullable=False),
        sa.Column("extraction_method", sa.String(length=64), nullable=True),
        sa.Column("embedding", Vector(dim=1536), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["extraction_id"], ["document_extractions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_chunks_embedding", "document_chunks", ["embedding"], postgresql_using="ivfflat")


def downgrade() -> None:
    op.drop_index("ix_document_chunks_embedding", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_table("document_extractions")
    op.drop_table("documents")
    sa.Enum("uploaded", "processing", "extracted", "failed", name="document_status").drop(op.get_bind(), checkfirst=False)
