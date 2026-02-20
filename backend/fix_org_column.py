from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("ALTER TABLE organizations CHANGE COLUMN org_type level INT DEFAULT 1 COMMENT '1: 总行, 2: 分行, 3: 支行'"))
    conn.commit()
    print("数据库表结构更新成功：org_type -> level")