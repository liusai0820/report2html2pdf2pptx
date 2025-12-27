import sys
import os
import logging
import argparse

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    import config
    import db
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UserPlanManager")

# 定义等级规则
PLANS = {
    "free": 3,
    "pro": 20,
    "max": 50,
    "turbo": 100
}

def set_user_plan(email, plan_name):
    """
    设置用户的等级和配额
    """
    if plan_name not in PLANS:
        logger.error(f"未知的等级: {plan_name}. 可选: {list(PLANS.keys())}")
        return False
        
    quota = PLANS[plan_name]
    client = db.get_client()
    
    if not client:
        return False
        
    try:
        # 1. 先根据 email 找到 user id
        # 假设 profiles 表有 email 字段
        res = client.table("profiles").select("id, email").eq("email", email).execute()
        
        if not res.data:
            logger.error(f"找不到用户: {email}")
            return False
            
        user = res.data[0]
        user_id = user['id']
        
        # 2. 更新 plan, quota, used
        update_data = {
            "plan": plan_name,
            "generation_quota": quota,
            "generations_used": 0 # 重置已用，让他爽
        }
        
        client.table("profiles").update(update_data).eq("id", user_id).execute()
        
        logger.info(f"✅ 用户 {email} 已设置为 [{plan_name.upper()}]")
        logger.info(f"   - 总配额: {quota}")
        logger.info(f"   - 已使用: 0 (已重置)")
        return True
        
    except Exception as e:
        logger.error(f"设置失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/set_user_plan.py <email> <plan>")
        print(f"Plans: {', '.join(PLANS.keys())}")
        sys.exit(1)
        
    email = sys.argv[1]
    plan = sys.argv[2]
    
    set_user_plan(email, plan)
