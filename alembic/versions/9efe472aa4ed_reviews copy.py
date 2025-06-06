"""reviews

Revision ID: 9efe472aa4ed
Revises: 
Create Date: 2025-05-05 10:43:58.433269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey

# revision identifiers, used by Alembic.
revision: str = '9efe472aa4ed'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("published", sa.Boolean, server_default=sa.sql.expression.literal(False), nullable=False),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("game_id", sa.Integer, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String, nullable=False),
    )
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("value", sa.Integer, nullable=False)
    )
    op.create_table(
        "friends",
        sa.Column("user_adding_id", sa.Integer, primary_key=True),
        sa.Column("user_added_id", sa.Integer, primary_key=True),
    )
    op.create_table(
        "games",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("game", sa.String, nullable=False),
        sa.Column("genre_id", sa.Integer, nullable=False),
    )
    op.create_table(
        "genres",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("genre", sa.String, nullable=False),
    )

    #Optional reviews for reviewing different aspects of a game. Each review can have multiple optional reviews extending.
    op.create_table(
        "optional_reviews",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("review_name", sa.String, nullable=False),
        sa.Column("optional_rating", sa.Integer, nullable=False),
        sa.Column("review_id", sa.Integer, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),

    )
    op.create_table(
        "history",
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("game_id", sa.Integer, primary_key=True),
        sa.Column("time_played", sa.Float, nullable=False),
        sa.Column("last_played", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_table(
        "comments",
        sa.Column("comment_id", sa.Integer, primary_key=True),
        sa.Column("review_id", sa.Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("reviews")
    op.drop_table("users")
    op.drop_table("friends")
    op.drop_table("games")
    op.drop_table("genres")
    op.drop_table("optional_reviews")
    op.drop_table("history")
    op.drop_table("comments")
