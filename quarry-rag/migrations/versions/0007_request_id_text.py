"""保留上游任意字符串请求ID，修复原文UUID列与HTTP契约不匹配。"""
from alembic import op
revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

def upgrade():
    op.execute("ALTER TABLE query_logs ALTER COLUMN request_id TYPE text USING request_id::text")

def downgrade():
    # 已有非UUID的上游日志时让转换明确失败，不能静默删掉审计日志。
    op.execute("ALTER TABLE query_logs ALTER COLUMN request_id TYPE uuid USING request_id::uuid")
