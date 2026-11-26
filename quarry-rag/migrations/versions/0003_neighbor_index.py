from pathlib import Path
from alembic import op
revision="0003"
down_revision="0002"
branch_labels=None
depends_on=None
def upgrade() -> None:
    sql = (Path(__file__).parent / "0003_neighbor_index.sql").read_text(encoding="utf-8")
    op.get_bind().exec_driver_sql(sql)

def downgrade() -> None:
    op.get_bind().exec_driver_sql(
        "DROP INDEX IF EXISTS chunks_neighbors;"
        "CREATE INDEX chunks_neighbors ON chunks (document_id, heading_path, ord)"
        " WHERE level = 0;"
    )
