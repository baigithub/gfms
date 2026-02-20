"""
更新角色表，添加机构层级属性
"""
from app.database import get_db
from app.models.user import Role
from sqlalchemy import text

def update_roles_with_org_level():
    """为现有角色添加机构层级属性"""
    db = next(get_db())
    
    try:
        # 添加 org_level 字段（如果不存在）
        try:
            db.execute(text("ALTER TABLE roles ADD COLUMN org_level INTEGER DEFAULT 1"))
            print("成功添加 org_level 字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("org_level 字段已存在，跳过创建")
            else:
                raise
        
        # 查询所有角色
        roles = db.query(Role).all()
        
        # 定义角色到机构层级的映射
        role_org_mapping = {
            "超级管理员": 1,  # 总行角色
            "系统管理员": 1,  # 总行角色
            "总行绿色金融管理岗": 1,  # 总行角色
            "总行绿色金融复核岗": 1,  # 总行角色
            "一级分行绿色金融管理岗": 1,  # 一级分行角色
            "一级分行绿色金融复核岗": 1,  # 一级分行角色
            "二级分行绿色金融管理岗": 2,  # 二级分行角色
            "二级分行绿色金融复核岗": 2,  # 二级分行角色
            "客户经理": 3,  # 支行角色
            "支行主管": 3,  # 支行角色
            "支行绿色金融专员": 3,  # 支行角色
        }
        
        # 更新角色的机构层级
        updated_count = 0
        for role in roles:
            if role.name in role_org_mapping:
                role.org_level = role_org_mapping[role.name]
                updated_count += 1
                print(f"更新角色: {role.name} -> 机构层级: {role.org_level}")
            else:
                # 默认设置为总行层级
                role.org_level = 1
                print(f"角色 '{role.name}' 未在映射中，设置为默认层级: 1")
        
        db.commit()
        print(f"\n成功更新 {updated_count} 个角色的机构层级属性")
        
    except Exception as e:
        db.rollback()
        print(f"更新失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_roles_with_org_level()