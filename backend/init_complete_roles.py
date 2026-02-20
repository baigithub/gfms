"""
初始化完整的角色体系，包括不同机构层级的角色
"""
from app.database import get_db
from app.models.user import Role
from sqlalchemy import text

def init_complete_roles():
    """初始化完整的角色体系"""
    db = next(get_db())
    
    try:
        # 定义完整的角色体系
        roles_data = [
            # 总行角色 (org_level=1)
            {
                "name": "总行超级管理员",
                "description": "总行系统超级管理员，拥有所有权限",
                "org_level": 1
            },
            {
                "name": "总行绿色金融管理岗",
                "description": "总行绿色金融管理岗，负责全行绿色金融业务管理",
                "org_level": 1
            },
            {
                "name": "总行绿色金融复核岗",
                "description": "总行绿色金融复核岗，负责最终审批",
                "org_level": 1
            },
            
            # 一级分行角色 (org_level=1，但属于分行层级)
            {
                "name": "一级分行绿色金融管理岗",
                "description": "一级分行绿色金融管理岗，负责分行绿色金融业务管理",
                "org_level": 1
            },
            {
                "name": "一级分行绿色金融复核岗",
                "description": "一级分行绿色金融复核岗，负责分行最终审批",
                "org_level": 1
            },
            
            # 二级分行角色 (org_level=2)
            {
                "name": "二级分行绿色金融管理岗",
                "description": "二级分行绿色金融管理岗，负责二级分行绿色金融业务管理",
                "org_level": 2
            },
            {
                "name": "二级分行绿色金融复核岗",
                "description": "二级分行绿色金融复核岗，负责二级分行最终审批",
                "org_level": 2
            },
            
            # 支行角色 (org_level=3)
            {
                "name": "支行客户经理",
                "description": "支行客户经理，负责绿色贷款认定的发起",
                "org_level": 3
            },
            {
                "name": "支行主管",
                "description": "支行主管，负责支行业务管理",
                "org_level": 3
            },
            {
                "name": "支行绿色金融专员",
                "description": "支行绿色金融专员，协助客户经理进行绿色认定",
                "org_level": 3
            },
        ]
        
        # 检查并添加角色
        added_count = 0
        updated_count = 0
        
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            
            if existing_role:
                # 更新现有角色
                existing_role.description = role_data["description"]
                existing_role.org_level = role_data["org_level"]
                updated_count += 1
                print(f"更新角色: {role_data['name']} -> 机构层级: {role_data['org_level']}")
            else:
                # 添加新角色
                new_role = Role(**role_data)
                db.add(new_role)
                added_count += 1
                print(f"添加角色: {role_data['name']} -> 机构层级: {role_data['org_level']}")
        
        db.commit()
        
        print(f"\n角色初始化完成:")
        print(f"- 新增角色: {added_count} 个")
        print(f"- 更新角色: {updated_count} 个")
        
        # 显示所有角色
        print(f"\n当前角色列表:")
        print("-" * 80)
        all_roles = db.query(Role).order_by(Role.org_level, Role.name).all()
        
        current_level = None
        level_names = {1: "总行/一级分行", 2: "二级分行", 3: "支行"}
        
        for role in all_roles:
            if role.org_level != current_level:
                current_level = role.org_level
                print(f"\n【{level_names.get(current_level, '未知层级')}】")
            
            print(f"  ID: {role.id} | 名称: {role.name}")
        
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_complete_roles()