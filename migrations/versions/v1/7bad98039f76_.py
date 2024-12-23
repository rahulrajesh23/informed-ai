"""add_admin_users

Revision ID: 7bad98039f76
Revises: 2c0320a83ec8
Create Date: 2024-12-22 22:58:27.690019+00:00

"""

from typing import Sequence

import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "7bad98039f76"
down_revision: str | None = "2c0320a83ec8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # Update foreign key references to users.user_id
    op.drop_constraint("user_details_user_id_fkey", "user_details", type_="foreignkey")
    op.create_foreign_key(
        "user_details_user_id_fkey", "user_details", "users", ["user_id"], ["user_id"]
    )

    op.drop_constraint(
        "user_medical_details_user_id_fkey", "user_medical_details", type_="foreignkey"
    )
    op.create_foreign_key(
        "user_medical_details_user_id_fkey",
        "user_medical_details",
        "users",
        ["user_id"],
        ["user_id"],
    )

    # Update foreign key for queries table
    op.drop_constraint("queries_user_id_fkey", "queries", type_="foreignkey")
    op.create_foreign_key(
        "queries_user_id_fkey", "queries", "users", ["user_id"], ["user_id"]
    )

    # Change primary key of user table to user_id
    op.alter_column("users", "id", new_column_name="user_id")

    # Add TAGALOG to language enum
    op.execute("ALTER TYPE language ADD VALUE 'TAGALOG'")

    # Add chat_thread table
    op.create_table(
        "chat_thread",
        sa.Column("chat_thread_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
        ),
        sa.PrimaryKeyConstraint("chat_thread_id"),
    )

    # Add message table
    op.create_table(
        "message",
        sa.Column("message_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("chat_thread_id", sa.Uuid(), nullable=False),
        sa.Column("source", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            "presentation_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("query_id", sa.Uuid(), nullable=True),
        sa.Column("acknowledged", sa.Boolean(), nullable=False),
        sa.Column(
            "requested_response_type",
            sa.Enum("TEXT", "TEXT_SHORT", "AUDIO", name="messagepresentationtype"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["chat_thread_id"], ["chat_thread.chat_thread_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index(
        op.f("ix_message_chat_thread_id"), "message", ["chat_thread_id"], unique=False
    )

    # Update queries table
    op.add_column(
        "queries",
        sa.Column("answer", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.drop_column("queries", "findings")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE user_details ALTER COLUMN language DROP DEFAULT")
    op.execute(
        "UPDATE user_details SET language = 'ENGLISH' WHERE language = 'TAGALOG'"
    )

    language_enum_old = sa.Enum(
        "ENGLISH",
        "SPANISH",
        name="language_old",
        create_type=True,
    )
    language_enum_old.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "user_details",
        "language",
        existing_type=sa.Enum(
            "ENGLISH",
            "SPANISH",
            "TAGALOG",
            name="language",
        ),
        type_=language_enum_old,
        postgresql_using="language::text::language_old",
    )

    op.execute("DROP TYPE language")
    op.execute("ALTER TYPE language_old RENAME TO language")

    op.add_column(
        "queries",
        sa.Column(
            "findings",
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_column("queries", "answer")
    op.drop_index(op.f("ix_message_chat_thread_id"), table_name="message")
    op.drop_table("message")
    op.drop_table("chat_thread")

    # Restore foreign key references to users.id
    op.drop_constraint("user_details_user_id_fkey", "user_details", type_="foreignkey")
    op.create_foreign_key(
        "user_details_user_id_fkey", "user_details", "users", ["user_id"], ["id"]
    )

    op.drop_constraint(
        "user_medical_details_user_id_fkey", "user_medical_details", type_="foreignkey"
    )
    op.create_foreign_key(
        "user_medical_details_user_id_fkey",
        "user_medical_details",
        "users",
        ["user_id"],
        ["id"],
    )

    # Restore foreign key for queries table
    op.drop_constraint("queries_user_id_fkey", "queries", type_="foreignkey")
    op.create_foreign_key(
        "queries_user_id_fkey", "queries", "users", ["user_id"], ["id"]
    )

    # Change primary key of user table back to id
    op.alter_column("users", "user_id", new_column_name="id")
    # ### end Alembic commands ###
