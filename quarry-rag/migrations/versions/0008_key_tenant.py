"""将API Key绑定租户，保留旧key默认demo的兼容行为。"""
from alembic import op
revision='0008'
down_revision='0007'
branch_labels=None
depends_on=None

def upgrade():
 op.execute('ALTER TABLE api_keys ADD COLUMN tenant_id uuid REFERENCES tenants(id)')
 op.execute("UPDATE api_keys SET tenant_id=(SELECT id FROM tenants WHERE slug='demo')WHERE tenant_id IS NULL")

def downgrade():
 op.execute("""DO $$ BEGIN IF EXISTS(SELECT 1 FROM api_keys WHERE tenant_id IS NOT NULL AND tenant_id<>(SELECT id FROM tenants WHERE slug='demo')) THEN RAISE EXCEPTION '存在非demo租户Key，回退会丢失隔离语义，须先迁移这些Key'; END IF; END $$""")
 op.execute('ALTER TABLE api_keys DROP COLUMN tenant_id')
