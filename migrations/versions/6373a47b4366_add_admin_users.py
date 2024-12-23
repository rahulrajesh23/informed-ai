"""add_admin_users

Revision ID: 6373a47b4366
Revises: aff80a3ceea8
Create Date: 2024-12-22 23:44:50.974847+00:00

"""

from typing import Sequence
from uuid import uuid4

import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6373a47b4366"
down_revision: str | None = "aff80a3ceea8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # First create the users
    op.execute(
        f"""
        INSERT INTO users (user_id, email, is_active, account_type)
        VALUES
            ('{uuid4()}', 'superadmin@informed.org', true, 'SUPERADMIN'),
            ('{uuid4()}', 'admin@informed.org', true, 'ADMIN')
        ON CONFLICT (email) DO NOTHING
        RETURNING user_id, email;
    """
    )

    # Then add their details with zip code and language
    op.execute(
        """
        INSERT INTO user_details (id, user_id, first_name, last_name, zip_code, language)
        SELECT
            gen_random_uuid(),
            users.user_id,
            CASE
                WHEN users.email = 'superadmin@informed.org' THEN 'Super'
                ELSE 'System'
            END,
            CASE
                WHEN users.email = 'superadmin@informed.org' THEN 'Admin'
                ELSE 'Admin'
            END,
            '12345',
            'ENGLISH'
        FROM users
        WHERE users.email IN ('superadmin@informed.org', 'admin@informed.org')
        AND NOT EXISTS (
            SELECT 1 FROM user_details WHERE user_details.user_id = users.user_id
        );
        """
    )

    # Add empty medical details
    op.execute(
        """
        INSERT INTO user_medical_details (id, user_id)
        SELECT
            gen_random_uuid(),
            users.user_id
        FROM users
        WHERE users.email IN ('superadmin@informed.org', 'admin@informed.org')
        AND NOT EXISTS (
            SELECT 1 FROM user_medical_details WHERE user_medical_details.user_id = users.user_id
        );
        """
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###