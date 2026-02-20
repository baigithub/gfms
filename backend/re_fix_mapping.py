"""
重新修正分类映射关系
"""
from app.database import SessionLocal
from sqlalchemy import text

def fix_mapping():
    """重新修正分类映射"""
    db = SessionLocal()
    
    try:
        # 创建正确的映射关系
        mapping = {
            # ID 31, 32, 34, 37: 节能降碳产业/高效节能装备制造/节能锅炉制造 (1.1.1)
            # ID 33: 环境保护产业/水污染治理 (2.3) - 只需要二级
            # ID 35, 36, 40: 资源循环利用产业/工业固体废弃物综合利用 (3.2.3)
            # ID 38, 39: 节能降碳产业/工业清洁生产改造 (1.4.2)
            
            # 具体映射
            '大气污染防治': '大气污染防治',  # 2.2.1
            '水污染治理': '水污染治理',    # 2.3.1
            '工业固体废弃物综合利用': '工业固体废弃物综合利用',  # 3.2.3.1
            '工业清洁生产改造': '工艺改进和流程优化',  # 1.4.2
            '高效节能装备制造': '高效节能装备制造',  # 1.1.1
        }
        
        # 更新 ID 33 的分类
        db.execute(text("""
            UPDATE green_identifications
            SET project_category_large = '环境保护产业',
                project_category_medium = '水污染治理',
                project_category_small = NULL
            WHERE id = 33
        """))
        
        # 更新 ID 38, 39 的分类
        db.execute(text("""
            UPDATE green_identifications
            SET project_category_medium = '工艺改进和流程优化'
            WHERE id IN (38, 39)
        """))
        
        db.commit()
        print('分类映射已修正')
        
    except Exception as e:
        db.rollback()
        print(f"更新失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_mapping()