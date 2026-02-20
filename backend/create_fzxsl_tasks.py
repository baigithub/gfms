"""
为申磊(fzxsl)创建10笔待办任务，使用少歌中任务战力top人名作为客户名称
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from datetime import datetime, timedelta
import random

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def create_tasks_for_fzxsl():
    """为申磊(fzxsl)创建10笔待办任务"""
    db = SessionLocal()
    try:
        # 查找申磊用户
        user = db.execute(text("SELECT id, username, real_name FROM users WHERE username = 'fzxsl'")).fetchone()
        if not user:
            print("✗ 用户 fzxsl 不存在")
            return
        
        user_id = user[0]
        print(f"找到用户: {user[1]} ({user[2]}), ID: {user_id}")
        
        # 获取客户经理角色ID
        role = db.execute(text("SELECT id FROM roles WHERE name LIKE '%客户经理%'")).fetchone()
        if not role:
            print("✗ 未找到客户经理角色")
            return
        
        role_id = role[0]
        print(f"客户经理角色ID: {role_id}")
        
        # 少歌中任务战力top的人名和对应战力值（作为放款金额，单位：万元）
        task_data = [
            {"name": "白起", "power": 99999, "account": "6222021001234560001"},
            {"name": "韩信", "power": 98765, "account": "6222021001234560002"},
            {"name": "诸葛亮", "power": 97654, "account": "6222021001234560003"},
            {"name": "赵云", "power": 96543, "account": "6222021001234560004"},
            {"name": "吕布", "power": 95432, "account": "6222021001234560005"},
            {"name": "关羽", "power": 94321, "account": "6222021001234560006"},
            {"name": "曹操", "power": 93210, "account": "6222021001234560007"},
            {"name": "周瑜", "power": 92109, "account": "6222021001234560008"},
            {"name": "马超", "power": 91098, "account": "6222021001234560009"},
            {"name": "黄忠", "power": 90087, "account": "6222021001234560010"},
        ]
        
        project_categories = [
            {"large": "节能环保产业", "medium": "节能环保装备制造", "small": "高效节能装备制造"},
            {"large": "清洁生产产业", "medium": "清洁生产技术装备", "small": "工业节能技术装备"},
            {"large": "清洁能源产业", "medium": "新能源发电", "small": "风力发电"},
            {"large": "生态环境产业", "medium": "环境污染治理", "small": "水污染治理"},
            {"large": "绿色服务产业", "medium": "绿色金融服务", "small": "绿色信贷服务"},
        ]
        
        esg_levels = [
            {"risk": "低风险", "performance": "优秀"},
            {"risk": "中低风险", "performance": "良好"},
            {"risk": "中风险", "performance": "一般"},
        ]
        
        business_types = [
            "一般性固定资产贷款",
            "绿色项目专项贷款",
            "流动资金贷款",
            "并购贷款",
            "银团贷款",
        ]
        
        print(f"\n开始为申磊创建 {len(task_data)} 笔待办任务...")
        
        for i, task in enumerate(task_data, 1):
            # 随机生成数据
            base_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            project_cat = random.choice(project_categories)
            esg = random.choice(esg_levels)
            business_type = random.choice(business_types)
            
            # 战力值转换为放款金额（战力值 * 1000）
            loan_amount = task["power"] * 1000
            
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
                "customer_name": task["name"],
                "customer_id": f"C{random.randint(100000, 999999)}",
                "business_type": business_type,
                "loan_account": task["account"],
                "loan_amount": loan_amount,
                "disbursement_date": base_date,
                "project_large": project_cat["large"],
                "project_medium": project_cat["medium"],
                "project_small": project_cat["small"],
                "esg_risk": esg["risk"],
                "esg_performance": esg["performance"],
                "status": "待办",
                "initiator_id": user_id,
                "org_id": 1,  # 总行
                "created_at": datetime.now(),
                "deadline": datetime.now() + timedelta(days=7)
            })
            
            identification_id = result.lastrowid
            print(f"  ✓ 任务 {i}: {task['name']} (ID: {identification_id}, 战力: {task['power']}, 放款金额: {loan_amount:,}元)")
        
        db.commit()
        print(f"\n✓ 成功为申磊创建 {len(task_data)} 笔待办任务")
        
        # 验证创建的任务
        print("\n验证创建的任务...")
        tasks = db.execute(text("""
            SELECT id, customer_name, loan_amount, status, created_at 
            FROM green_identifications 
            WHERE initiator_id = :user_id 
            ORDER BY created_at DESC
        """), {"user_id": user_id}).fetchall()
        
        print(f"\n申磊的待办任务列表（共 {len(tasks)} 笔）:")
        for task in tasks:
            print(f"  - {task[1]}: {task[2]:,.0f}元 ({task[3]})")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tasks_for_fzxsl()
    print("\n任务创建完成！")