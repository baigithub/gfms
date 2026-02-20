"""
按照绿色金融支持项目目录标准格式更新green_project_category字段
"""
from app.database import SessionLocal
from sqlalchemy import text

def fix_category_format():
    """修复分类格式，按照绿色金融支持项目目录标准格式"""
    db = SessionLocal()
    
    try:
        # 获取绿色项目目录的映射
        categories_map = {}
        result = db.execute(text("""
            SELECT large_code, large_name, medium_code, medium_name, 
                   small_code, small_name, formatted_name
            FROM green_project_categories
        """)).fetchall()
        
        for row in result:
            large_code = row[0]
            large_name = row[1]
            medium_code = row[2]
            medium_name = row[3]
            small_code = row[4]
            small_name = row[5]
            formatted_name = row[6]
            
            key = (large_code, medium_code, small_code)
            categories_map[key] = formatted_name
        
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
            
            # 查找匹配的标准格式
            # 尝试匹配完整的三级分类
            formatted = None
            for key in categories_map:
                if key[0] == large and key[1] == medium and key[2] == small:
                    formatted = categories_map[key]
                    break
            
            # 如果没有找到三级分类，尝试匹配二级分类
            if not formatted:
                for key in categories_map:
                    if key[0] == large and key[1] == medium and not key[2]:
                        formatted = categories_map[key]
                        break
            
            # 如果还是没有，使用原始拼接
            if not formatted:
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
    fix_category_format()