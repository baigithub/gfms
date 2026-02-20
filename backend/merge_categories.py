"""
将现有绿色认定数据的三个分类字段合并到green_project_category字段
"""
from app.database import SessionLocal
from sqlalchemy import text

def merge_green_categories():
    """合并绿色项目分类字段"""
    db = SessionLocal()
    
    try:
        # 查询所有绿色认定数据
        result = db.execute(text("""
            SELECT id, project_category_large, project_category_medium, project_category_small
            FROM green_identifications
        """)).fetchall()
        
        updated_count = 0
        for row in result:
            id_val = row[0]
            large = row[1]
            medium = row[2]
            small = row[3]
            
            # 拼接格式化名称
            parts = []
            if large:
                parts.append(large)
            if medium:
                parts.append(medium)
            if small:
                parts.append(small)
            
            formatted = '/'.join(parts)
            
            # 更新记录
            if formatted:
                db.execute(text("""
                    UPDATE green_identifications
                    SET green_project_category = :formatted
                    WHERE id = :id
                """), {"formatted": formatted, "id": id_val})
                updated_count += 1
        
        db.commit()
        print(f"成功更新 {updated_count} 条记录")
        
    except Exception as e:
        db.rollback()
        print(f"更新失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    merge_green_categories()