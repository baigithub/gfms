"""
数据库迁移脚本：更新机构表的 level 字段为 org_type
执行命令：python -m migrations.update_org_level
"""

from sqlalchemy import text
from app.database import SessionLocal, engine


def migrate():
    """执行数据库迁移"""
    db = SessionLocal()
    
    try:
        print("开始迁移：将 organizations 表的 level 字段重命名为 org_type")
        
        # 检查字段是否存在
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'organizations' 
            AND column_name = 'level'
        """))
        
        if result.fetchone():
            # 重命名字段
            db.execute(text("""
                ALTER TABLE organizations 
                RENAME COLUMN level TO org_type
            """))
            print("✓ 已将 level 字段重命名为 org_type")
        else:
            print("⚠ level 字段不存在，可能已经迁移过")
        
        # 更新注释
        db.execute(text("""
            COMMENT ON COLUMN organizations.org_type IS '机构类型：1=总行, 2=分行, 3=支行'
        """))
        print("✓ 已更新 org_type 字段注释")
        
        # 提交事务
        db.commit()
        print("\n✓ 迁移完成！")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ 迁移失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()