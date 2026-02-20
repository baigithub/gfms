from sqlalchemy import create_engine, text, inspect
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

# 检查表结构
inspector = inspect(engine)
columns = inspector.get_columns('organizations')

print("organizations 表结构:")
for col in columns:
    print(f"  {col['name']}: {col['type']}")

# 查询一些数据
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, code, level, is_active FROM organizations LIMIT 5"))
    print("\norganizations 表数据:")
    for row in result:
        print(f"  {row}")