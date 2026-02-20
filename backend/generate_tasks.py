"""
清理绿色认定任务并生成新任务
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from datetime import datetime, timedelta
import random

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def clean_and_generate_tasks():
    """清理现有任务并生成新任务"""
    db = SessionLocal()
    try:
        # 1. 清理现有的绿色认定任务（删除所有记录）
        print("清理现有绿色认定任务...")
        
        # 删除工作流任务
        db.execute(text("DELETE FROM workflow_tasks"))
        
        # 删除工作流实例
        db.execute(text("DELETE FROM workflow_instances"))
        
        # 删除绿色认定记录
        db.execute(text("DELETE FROM green_identifications"))
        
        db.commit()
        print("✓ 清理完成")
        
        # 2. 为用户1001生成10条任务
        print("\n为用户1001生成10条任务...")
        
        # 检查用户1001是否存在
        user = db.execute(text("SELECT id, username, real_name FROM users WHERE id = 1001")).fetchone()
        if not user:
            print("✗ 用户1001不存在，请先创建用户")
            return
        
        print(f"找到用户: {user[1]} ({user[2]})")
        
        # 获取客户经理角色ID
        role = db.execute(text("SELECT id FROM roles WHERE name LIKE '%客户经理%'")).fetchone()
        if not role:
            print("✗ 未找到客户经理角色")
            return
        
        role_id = role[0]
        print(f"客户经理角色ID: {role_id}")
        
        # 生成10条任务数据
        task_templates = [
            {"customer_name": "上海XX科技有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560001"},
            {"customer_name": "北京XX制造有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560002"},
            {"customer_name": "广州XX环保科技有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560003"},
            {"customer_name": "深圳XX新材料股份有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560004"},
            {"customer_name": "杭州XX新能源科技有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560005"},
            {"customer_name": "成都XX绿色科技有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560006"},
            {"customer_name": "武汉XX环保装备有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560007"},
            {"customer_name": "南京XX清洁能源科技有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560008"},
            {"customer_name": "西安XX节能环保股份有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560009"},
            {"customer_name": "重庆XX绿色材料科技有限公司", "business_type": "一般性固定资产贷款", "loan_account": "6222021001234560010"},
        ]
        
        project_categories = [
            {"large": "节能环保产业", "medium": "节能环保装备制造", "small": "高效节能装备制造"},
            {"large": "清洁生产产业", "medium": "清洁生产技术装备", "small": "工业节能技术装备"},
            {"large": "清洁能源产业", "medium": "新能源发电", "small": "风力发电"},
            {"large": "生态环境产业", "medium": "环境污染治理", "small": "水污染治理"},
        ]
        
        esg_levels = [
            {"risk": "低风险", "performance": "优秀"},
            {"risk": "中低风险", "performance": "良好"},
            {"risk": "中风险", "performance": "一般"},
        ]
        
        loan_amounts = [5000000, 8000000, 12000000, 15000000, 20000000, 30000000]
        
        for i, template in enumerate(task_templates, 1):
            # 随机生成数据
            base_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            project_cat = random.choice(project_categories)
            esg = random.choice(esg_levels)
            loan_amount = random.choice(loan_amounts)
            
            # 生成贷款编号
            loan_code = f"GL{datetime.now().strftime('%Y%m%d')}{str(i).zfill(4)}"
            
            # 插入绿色认定记录
            result = db.execute(text("""
                INSERT INTO green_identifications 
                (loan_code, customer_name, customer_id, business_type, loan_account, loan_amount, 
                 disbursement_date, project_category_large, project_category_medium, project_category_small,
                 esg_risk_level, esg_performance_level, status, initiator_id, org_id, created_at, deadline)
                VALUES 
                (:loan_code, :customer_name, :customer_id, :business_type, :loan_account, :loan_amount,
                 :disbursement_date, :project_large, :project_medium, :project_small,
                 :esg_risk, :esg_performance, :status, :initiator_id, :org_id, :created_at, :deadline)
            """), {
                "loan_code": loan_code,
                "customer_name": template["customer_name"],
                "customer_id": f"C{random.randint(100000, 999999)}",
                "business_type": template["business_type"],
                "loan_account": template["loan_account"],
                "loan_amount": loan_amount,
                "disbursement_date": base_date,
                "project_large": project_cat["large"],
                "project_medium": project_cat["medium"],
                "project_small": project_cat["small"],
                "esg_risk": esg["risk"],
                "esg_performance": esg["performance"],
                "status": "待办",
                "initiator_id": 1001,
                "org_id": 1,  # 总行
                "created_at": datetime.now(),
                "deadline": datetime.now() + timedelta(days=7)
            })
            
            identification_id = result.lastrowid
            print(f"  ✓ 任务 {i}: {template['customer_name']} (ID: {identification_id}, 贷款金额: {loan_amount:,}元)")
        
        db.commit()
        print(f"\n✓ 成功生成 {len(task_templates)} 条任务")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_and_generate_tasks()
    print("\n任务生成完成！")