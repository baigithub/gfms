"""
根据实际银行业务层级关系修正角色配置
"""
from app.database import get_db
from app.models.user import Role
from sqlalchemy import text

def fix_roles_by_level():
    """修正角色配置，符合实际银行业务层级"""
    db = next(get_db())
    
    try:
        # 先清理不需要的角色
        roles_to_delete = [
            "总行绿色金融管理岗",      # 总行不需要这个角色
            "总行绿色金融复核岗",      # 总行不需要这个角色
            "总行超级管理员",          # 改用"系统管理员"
            "普通用户"                  # 不需要的角色
        ]
        
        deleted_count = 0
        for role_name in roles_to_delete:
            role = db.query(Role).filter(Role.name == role_name).first()
            if role:
                db.delete(role)
                deleted_count += 1
                print(f"删除角色: {role_name}")
        
        if deleted_count > 0:
            db.commit()
            print(f"删除了 {deleted_count} 个不需要的角色\n")
        
        # 定义正确的角色体系
        correct_roles = [
            # 总行角色 (org_level=1)
            {
                "name": "系统管理员",
                "description": "总行系统管理员，拥有所有权限",
                "org_level": 1
            },
            
            # 一级分行角色 (org_level=1) - 实际上是一级分行，但层级编码仍为1
            {
                "name": "一级分行客户经理",
                "description": "一级分行客户经理，负责绿色贷款认定的发起",
                "org_level": 1
            },
            {
                "name": "一级分行绿色金融管理岗",
                "description": "一级分行绿色金融管理岗，负责分行绿色金融业务审核",
                "org_level": 1
            },
            {
                "name": "一级分行绿色金融复核岗",
                "description": "一级分行绿色金融复核岗，负责分行绿色贷款最终审批（只能在一级行）",
                "org_level": 1
            },
            
            # 二级分行角色 (org_level=2)
            {
                "name": "二级分行客户经理",
                "description": "二级分行客户经理，负责绿色贷款认定的发起",
                "org_level": 2
            },
            {
                "name": "二级分行绿色金融管理岗",
                "description": "二级分行绿色金融管理岗，负责二级分行绿色金融业务审核（只能在二级分行，不能在总行和支行）",
                "org_level": 2
            },
            {
                "name": "二级分行主管",
                "description": "二级分行主管，负责二级分行业务管理",
                "org_level": 2
            },
            
            # 支行角色 (org_level=3)
            {
                "name": "支行客户经理",
                "description": "支行客户经理，负责绿色贷款认定的发起（支行和分行都可以有客户经理）",
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
        
        # 检查并更新/添加角色
        added_count = 0
        updated_count = 0
        
        for role_data in correct_roles:
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
        
        print(f"\n角色修正完成:")
        print(f"- 新增角色: {added_count} 个")
        print(f"- 更新角色: {updated_count} 个")
        
        # 显示最终的角色列表
        print(f"\n最终角色列表:")
        print("=" * 80)
        all_roles = db.query(Role).order_by(Role.org_level, Role.name).all()
        
        current_level = None
        level_names = {1: "一级分行/总行", 2: "二级分行", 3: "支行"}
        
        for role in all_roles:
            if role.org_level != current_level:
                current_level = role.org_level
                print(f"\n【{level_names.get(current_level, '未知层级')}】")
            
            print(f"  ID: {role.id:2d} | 名称: {role.name:25s} | {role.description}")
        
        print("\n" + "=" * 80)
        print("角色配置说明:")
        print("- 系统管理员: 总行角色，拥有所有权限")
        print("- 绿色金融管理岗: 只能在分行（一级或二级），不能在总行和支行")
        print("- 绿色金融复核岗: 只能在一级行，负责最终审批")
        print("- 客户经理: 既可以在分行也可以在支行")
        print("- 二级分行绿色金融管理岗: 只能在二级分行，不能在总行和支行")
        
    except Exception as e:
        db.rollback()
        print(f"修正失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_roles_by_level()