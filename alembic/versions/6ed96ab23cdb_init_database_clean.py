"""init_database_clean

Revision ID: 6ed96ab23cdb
Revises: 37f558928a24
Create Date: 2025-09-08 14:23:52.293933

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from models.models import Base


# revision identifiers, used by Alembic.
revision: str = '6ed96ab23cdb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Crear todas las tablas desde cero."""
    # Crear todas las tablas usando los modelos SQLAlchemy
    Base.metadata.create_all(bind=op.get_bind())
    print("✅ Todas las tablas creadas exitosamente")


def downgrade() -> None:
    """Downgrade schema."""
    pass
