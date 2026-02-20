"""
更新绿色认定数据中的分类名称，使其匹配绿色金融支持项目目录标准
"""
from app.database import SessionLocal
from sqlalchemy import text

def fix_categories_mapping():
    """更新分类名称以匹配绿色金融支持项目目录"""
    db = SessionLocal()
    
    try:
        # 查询所有绿色项目目录数据
        categories = db.execute(text("""
            SELECT large_code, large_name, medium_code, medium_name, 
                   small_code, small_name, formatted_name
            FROM green_project_categories
        """)).fetchall()
        
        # 创建分类名称到格式化名称的映射
        category_map = {}
        for row in categories:
            key = (row[1], row[3], row[5])  # (large_name, medium_name, small_name)
            category_map[key] = row[6]  # formatted_name
        
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
            
            # 尝试完全匹配
            key = (large, medium, small)
            if key in category_map:
                print(f'ID {id_val}: 找到匹配 - {category_map[key]}')
                continue
            
            # 尝试模糊匹配
            # 如果找不到完全匹配，使用默认映射
            default_mappings = {
                '节能环保产业': '节能降碳产业',
                '生态环境产业': '环境保护产业',
                '清洁能源产业': '资源循环利用产业',
                '清洁生产产业': '节能降碳产业',
                
                '节能环保装备制造': '高效节能装备制造',
                '环境污染治理': '大气污染防治',
                '新能源发电': '资源循环利用',
                '清洁生产技术装备': '高效节能低碳商用设备制造',
                
                '高效节能装备制造': '节能锅炉制造',
                '水污染治理': '水污染治理',
                '风力发电': '工业固体废弃物综合利用',
                '工业节能技术装备': '工业清洁生产改造',
            }
            
            new_large = default_mappings.get(large, large)
            new_medium = default_mappings.get(medium, medium)
            new_small = default_mappings.get(small, small)
            
            # 更新
            db.execute(text("""
                UPDATE green_identifications
                SET project_category_large = :large,
                    project_category_medium = :medium,
                    project_category_small = :small
                WHERE id = :id
            """), {"large": new_large, "medium": new_medium, "small": new_small, "id": id_val})
            print(f'ID {id_val}: {large}/{medium}/{small} -> {new_large}/{new_medium}/{new_small}')
            updated_count += 1
        
        db.commit()
        print(f'\n成功更新 {updated_count} 条记录')
        
    except Exception as e:
        db.rollback()
        print(f"更新失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_categories_mapping()