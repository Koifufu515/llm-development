from pathlib import Path
from alembic import op
revision="0004"
down_revision="0003"
branch_labels=None
depends_on=None
def upgrade() -> None:
    sql = (Path(__file__).parent / "0004_fact_layer.sql").read_text(encoding="utf-8")
    op.get_bind().exec_driver_sql(sql)

def downgrade() -> None:
    op.get_bind().exec_driver_sql(
        "DROP TABLE IF EXISTS fact_extractions;"
        "DROP TABLE IF EXISTS fact_mentions;"
        "DROP TABLE IF EXISTS facts;"
        "ALTER TABLE collections DROP COLUMN IF EXISTS facts_enabled;"
    )
