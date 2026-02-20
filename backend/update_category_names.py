"""
更新绿色认定数据中的分类名称，使其匹配绿色金融支持项目目录标准
"""
from app.database import SessionLocal
from sqlalchemy import text

def update_category_names():
    """更新分类名称以匹配绿色金融支持项目目录"""
    db = SessionLocal()
    
    try:
        # 定义分类名称映射（根据实际数据需要调整）
        category_mapping = {
            # 节能环保相关 -> 节能降碳
            "节能环保产业": "节能降碳产业",
            "节能环保装备制造": "高效节能装备制造",
            "高效节能装备制造": "节能锅炉制造",  # 示例：可以改为更具体的小类
            
            # 生态环境相关 -> 环境保护
            "生态环境产业": "环境保护产业",
            "环境污染治理": "大气污染防治",
            "水污染治理": "水污染治理",
            
            # 清洁能源相关 -> 资源循环利用
            "清洁能源产业": "资源循环利用产业",
            "新能源发电": "资源循环利用",
            "风力发电": "工业固体废弃物综合利用",
        }
        
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
            
            # 更新分类名称
            new_large = category_mapping.get(large, large)
            new_medium = category_mapping.get(medium, medium)
            new_small = category_mapping.get(small, small)
            
            if new_large != large or new_medium != medium or new_small != small:
                db.execute(text("""
                    UPDATE green_identifications
                    SET project_category_large = :large,
                        project_category_medium = :medium,
                        project_category_small = :small
                    WHERE id = :id
                """), {"large": new_large, "medium": new_medium, "small": new_small, "id": id_val})
                updated_count += 1
                print(f'ID {id_val}: {large}/{medium}/{small} -> {new_large}/{new_medium}/{new_small}')
        
        db.commit()
        print(f'\n成功更新 {updated_count} 条记录')
        
    except Exception as e:
        db.rollback()
        print(f"更新失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_category_names()