from pathlib import Path
from alembic import op
revision="0006"
down_revision="0005"
branch_labels=None
depends_on=None
def upgrade() -> None:
    sql = (Path(__file__).parent / "0006_api.sql").read_text(encoding="utf-8")
    op.get_bind().exec_driver_sql(sql)

def downgrade() -> None:
    op.get_bind().exec_driver_sql(
        "DROP TABLE IF EXISTS query_logs;"
        "DROP TABLE IF EXISTS api_keys;"
    )
