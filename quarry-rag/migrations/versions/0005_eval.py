from pathlib import Path
from alembic import op
revision="0005"
down_revision="0004"
branch_labels=None
depends_on=None
def upgrade() -> None:
    sql = (Path(__file__).parent / "0005_eval.sql").read_text(encoding="utf-8")
    op.get_bind().exec_driver_sql(sql)

def downgrade() -> None:
    op.get_bind().exec_driver_sql(
        "DROP TABLE IF EXISTS eval_results;"
        "DROP TABLE IF EXISTS eval_runs;"
        "DROP TABLE IF EXISTS eval_queries;"
    )
