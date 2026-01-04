"""
Supabase 数据库交互模块

@input:  config (SUPABASE_SERVICE_ROLE_KEY, VITE_SUPABASE_URL)
@output: add_generation_quota(user_id, amount) -> 更新用户配额
@output: get_daily_report() -> 包含各项运营数据的字典
@pos:    后端管理员级数据库操作，被 server.py 反馈处理调用

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/_FOLDER.md
"""

from supabase import create_client, Client
import config
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Client = None

def get_client() -> Client:
    """Get or create Supabase client"""
    global supabase
    if supabase is None:
        if not config.VITE_SUPABASE_URL or not config.SUPABASE_SERVICE_ROLE_KEY:
            logger.error("Supabase credentials missing!")
            return None
        try:
            supabase = create_client(
                config.VITE_SUPABASE_URL,
                config.SUPABASE_SERVICE_ROLE_KEY
            )
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            return None
    return supabase

def add_generation_quota(user_id: str, amount: int = 1) -> bool:
    """Add generation quota to a user's profile"""
    client = get_client()
    if not client:
        return False
        
    try:
        # 1. Get current quota
        res = client.table("profiles").select("generation_quota").eq("id", user_id).single().execute()
        if not res.data:
            logger.error(f"User {user_id} not found")
            return False
            
        current_quota = res.data.get("generation_quota", 0)
        
        # 2. Update quota
        new_quota = current_quota + amount
        client.table("profiles").update({"generation_quota": new_quota}).eq("id", user_id).execute()
        
        logger.info(f"Updated quota for {user_id}: {current_quota} -> {new_quota}")
        return True
    except Exception as e:
        logger.error(f"Error updating quota: {e}")
        return False, 0

def check_quota_valid(user_id: str) -> tuple[bool, int, str]:
    """检查用户额度是否有效（包含有效期检查）
    
    Returns: (is_valid, remaining_quota, message)
    """
    client = get_client()
    if not client:
        return False, 0, "数据库连接失败"
    
    try:
        res = client.table("profiles").select(
            "generation_quota, generations_used, quota_expires_at, plan_type"
        ).eq("id", user_id).single().execute()
        
        if not res.data:
            return False, 0, "用户不存在"
        
        data = res.data
        quota = data.get("generation_quota", 0)
        used = data.get("generations_used", 0)
        remaining = quota - used
        expires_at = data.get("quota_expires_at")
        plan_type = data.get("plan_type", "free")
        
        # 检查有效期
        if expires_at:
            from datetime import datetime
            exp_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.now(exp_date.tzinfo) > exp_date:
                return False, 0, f"您的{plan_type}套餐已于{exp_date.strftime('%Y-%m-%d')}过期"
        
        if remaining <= 0:
            return False, 0, "生成额度已用完"
        
        return True, remaining, f"剩余{remaining}次"
        
    except Exception as e:
        logger.error(f"Error checking quota: {e}")
        return False, 0, str(e)

def set_user_plan(user_id: str, plan_type: str, quota: int, validity_days: int = None) -> tuple[bool, str]:
    """设置用户套餐
    
    Args:
        user_id: 用户ID
        plan_type: 套餐类型 (free, deadline, pass, team)
        quota: 额度次数
        validity_days: 有效期天数，None表示永久
    
    Returns: (success, message)
    """
    client = get_client()
    if not client:
        return False, "数据库连接失败"
    
    try:
        update_data = {
            "plan_type": plan_type,
            "generation_quota": quota,
            "generations_used": 0,  # 重置已用次数
            "plan_purchased_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if validity_days:
            expires_at = datetime.now() + timedelta(days=validity_days)
            update_data["quota_expires_at"] = expires_at.isoformat()
        else:
            update_data["quota_expires_at"] = None  # 永久有效
        
        client.table("profiles").update(update_data).eq("id", user_id).execute()
        
        exp_msg = f"，有效期{validity_days}天" if validity_days else "，永久有效"
        logger.info(f"Set plan for {user_id}: {plan_type}, quota={quota}{exp_msg}")
        return True, f"已设置{plan_type}套餐，{quota}次额度{exp_msg}"
        
    except Exception as e:
        logger.error(f"Error setting plan: {e}")
        return False, str(e)

def get_all_users(limit: int = 100) -> list:
    """获取所有用户列表（用于管理后台，查询 admin_users 视图）"""
    client = get_client()
    if not client:
        return []
    
    try:
        # 查询 admin_users 视图 (包含 email)
        res = client.table("admin_users").select("*").limit(limit).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []

def get_daily_report() -> dict:
    """
    聚合今日运营数据：
    1. 新增用户数
    2. 总生成次数
    3. 用户反馈概况
    """
    client = get_client()
    if not client:
        return {}
        
    stats = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "new_users": 0,
        "total_generations": 0,
        "feedbacks": [],
        "avg_rating": 0.0
    }
    
    try:
        # 获取今天的起始时间 (ISO format)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        # 1. 新增用户 (Profiles created_at >= today)
        # 注意：Supabase API 的 count 需要 count='exact'
        res_users = client.table("profiles") \
            .select("id", count="exact") \
            .gte("created_at", today_start) \
            .execute()
        stats["new_users"] = res_users.count if res_users.count is not None else len(res_users.data)

        # 2. 今日生成 (Generations table)
        # 假设表名为 'generations'
        try:
            res_gens = client.table("generations") \
                .select("id", count="exact") \
                .gte("created_at", today_start) \
                .execute()
            stats["total_generations"] = res_gens.count if res_gens.count is not None else len(res_gens.data)
        except Exception as e:
            logger.warning(f"Could not query generations table: {e}")

        # 3. 反馈统计 (Feedbacks table)
        # 假设表名为 'feedbacks' 或 'user_feedback'
        # 我们用 server.py 里的反馈逻辑推断，可能是 'feedbacks' (根据 notify-feedback 端点)
        try:
            res_feedbacks = client.table("feedback") \
                .select("rating,comment,created_at") \
                .gte("created_at", today_start) \
                .execute()
            
            feedbacks = res_feedbacks.data
            if feedbacks:
                total_rating = sum(f.get("rating", 0) for f in feedbacks)
                stats["avg_rating"] = round(total_rating / len(feedbacks), 1)
                # 只保留有评论的反馈
                stats["feedbacks"] = [f for f in feedbacks if f.get("comment")]
        except Exception as e:
             logger.warning(f"Could not query feedbacks table: {e}")
             
        return stats
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        return stats

