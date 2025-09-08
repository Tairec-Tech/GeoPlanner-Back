"""fix_notificaciones_table_drop

Revision ID: 37f558928a24
Revises: 3bd34d39b328
Create Date: 2025-09-08 14:22:27.842854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37f558928a24'
down_revision: Union[str, Sequence[str], None] = '3bd34d39b328'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Verificar si la tabla notificaciones existe antes de intentar eliminarla
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    if 'notificaciones' in inspector.get_table_names():
        op.drop_table('notificaciones')
        print("✅ Tabla 'notificaciones' eliminada exitosamente")
    else:
        print("ℹ️ Tabla 'notificaciones' no existe, saltando eliminación")


def downgrade() -> None:
    """Downgrade schema."""
    pass
