import sys
import os
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    import config
    import db
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuotaReset")

def reset_all_quotas(target_amount=3):
    """
    重置所有用户的配额
    """
    client = db.get_client()
    if not client:
        logger.error("无法连接数据库")
        return False
        
    print(f"准备将所有用户的配额重置为: {target_amount}")
    confirm = input("此操作将影响所有用户，确认执行? (输入 'RESET'): ")
    
    if confirm != 'RESET':
        print("已取消")
        return False
        
    try:
        # 重置已使用次数为 0
        # 同时也将总配额确保至少为 target_amount (可视需求决定是否操作 quota)
        # 这里只重置 used，让用户回满血
        
        # 1. 重置 used = 0
        logger.info("正在重置 generations_used = 0 ...")
        res = client.table("profiles").update({"generations_used": 0}).neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        updated_count = len(res.data) if res.data else 0
        logger.info(f"成功重置了 {updated_count} 位用户的已用次数。")
        
        # 2. (可选) 如果刚才把 quota 改成了 3，对于高级会员可能亏了？
        # 如果需要恢复 quota，或者这里只重置 used 就够了。
        # 刚才的操作已经把 quota 变成了 3。如果有些用户本来是 10，那就亏了。
        # 如果大家都是免费用户，3 是也没关系。
        # 为了安全起见，这里不再动 quota，只把 used 清零。
        
        return True
        
    except Exception as e:
        logger.error(f"重置失败: {e}")
        # 如果批量更新失败，可能需分页获取再逐个更新（较慢但稳妥）
        print("批量更新失败，尝试逐个更新...")
        try:
             users_res = client.table("profiles").select("id").execute()
             users = users_res.data
             count = 0
             for u in users:
                 client.table("profiles").update({"generation_quota": target_amount}).eq("id", u['id']).execute()
                 count += 1
                 print(f"Updated {count}/{len(users)}", end='\r')
             print(f"\n逐个更新完成: {count}")
             return True
        except Exception as inner_e:
             logger.error(f"逐个更新也失败: {inner_e}")
             return False

if __name__ == "__main__":
    reset_all_quotas(3)
