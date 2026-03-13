#!/usr/bin/env python3
"""
杭州亲子游玩地点推荐 - 随机推荐脚本

使用方法:
    python3 recommend.py [--app-token TOKEN] [--table-id TABLE_ID] [--test]
"""

import random
import json
from datetime import datetime, timedelta

# 默认配置（从飞书表格获取）
DEFAULT_APP_TOKEN = "Alo1b4mgzaZcR5sjivOcYVUbn5b"
DEFAULT_TABLE_ID = "tblXAZVb60foglbc"


def get_current_season():
    """根据当前月份返回季节"""
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "春季"
    elif month in [6, 7, 8]:
        return "夏季"
    elif month in [9, 10, 11]:
        return "秋季"
    else:
        return "冬季"


def get_season_tags(season):
    """根据季节返回推荐的特色标签"""
    season_map = {
        "春季": ["花海", "自然风光", "户外探险"],
        "夏季": ["室内活动", "购物中心", "自然风光"],
        "秋季": ["自然风光", "花海", "户外探险"],
        "冬季": ["室内活动", "购物中心", "亲子餐厅"]
    }
    return season_map.get(season, [])


def calculate_priority(record, current_date):
    """计算推荐优先级（基于上次游玩时间）"""
    fields = record.get("fields", {})
    last_visit = fields.get("上次游玩时间")
    
    if not last_visit:
        return 100  # 没去过，优先级最高
    
    # 计算多少天没去了
    days_since_visit = (current_date - datetime.fromtimestamp(last_visit / 1000)).days
    
    if days_since_visit > 60:
        return 100  # 超过 2 个月没去，优先级最高
    elif days_since_visit > 30:
        return 80   # 超过 1 个月没去
    elif days_since_visit > 14:
        return 50   # 超过 2 周没去
    elif days_since_visit > 7:
        return 30   # 超过 1 周没去
    else:
        return 10   # 最近刚去过，优先级最低


def recommend_spot(records, child_age=None, indoor_preference=None):
    """
    推荐一个地点
    
    Args:
        records: 所有地点记录
        child_age: 孩子年龄（可选）
        indoor_preference: 是否偏好室内（True/False/None）
    
    Returns:
        推荐的地点记录
    """
    current_date = datetime.now()
    season = get_current_season()
    season_tags = get_season_tags(season)
    
    # 计算每个地点的优先级
    scored_records = []
    for record in records:
        fields = record.get("fields", {})
        score = calculate_priority(record, current_date)
        
        # 季节匹配加分
        spot_tags = fields.get("特色标签", [])
        for tag in season_tags:
            if tag in spot_tags:
                score += 20
        
        # 年龄匹配
        if child_age:
            age_range = fields.get("适合年龄", "")
            # 简单匹配逻辑
            if "0 岁" in age_range or str(child_age) in age_range:
                score += 10
        
        # 室内/室外偏好
        if indoor_preference is True:
            if "室内活动" in spot_tags or "购物中心" in spot_tags:
                score += 30
            else:
                score -= 20
        elif indoor_preference is False:
            if "自然风光" in spot_tags or "户外探险" in spot_tags:
                score += 30
            else:
                score -= 20
        
        scored_records.append((score, record))
    
    # 按优先级排序
    scored_records.sort(key=lambda x: x[0], reverse=True)
    
    # 从前 50% 中随机选择（增加随机性）
    top_count = max(1, len(scored_records) // 2)
    top_records = scored_records[:top_count]
    
    # 随机选择一个
    selected = random.choice(top_records)
    
    return selected[1]


def format_recommendation(record):
    """格式化推荐结果"""
    fields = record.get("fields", {})
    
    spot_name = fields.get("杭州亲子游玩地点库", "未知地点")
    area = fields.get("区域", "")
    age_range = fields.get("适合年龄", "")
    tags = fields.get("特色标签", [])
    reason = fields.get("推荐理由", "")
    rating = fields.get("推荐指数", "")
    drive_time = fields.get("距未来科技城车程", "")
    review = fields.get("游玩评价", "")
    
    # 生成小贴士
    tips = generate_tips(fields)
    
    output = f"""
🎡 本周末推荐：**{spot_name}**

📍 区域：{area}
🚗 距未来科技城：{drive_time}
👶 适合年龄：{age_range}
🏷️ 特色：{' '.join(tags)}
⭐ 推荐指数：{rating}

💡 推荐理由：
{reason}

📝 游玩评价：
{review}

📋 小贴士：
{tips}
"""
    return output.strip()


def generate_tips(fields):
    """根据地点特色生成小贴士"""
    tags = fields.get("特色标签", [])
    tips = []
    
    if "大草坪" in tags:
        tips.append("- 可以带野餐垫和玩具，让孩子尽情奔跑")
    if "亲子餐厅" in tags:
        tips.append("- 室内用餐方便，适合天气不好时")
    if "自然风光" in tags:
        tips.append("- 建议穿舒适的鞋子，适合徒步")
    if "购物中心" in tags:
        tips.append("- 停车方便，周边配套设施完善")
    if "花海" in tags:
        tips.append("- 最佳观赏季节，适合拍照")
    if "室内活动" in tags:
        tips.append("- 不受天气影响，四季皆宜")
    if "户外探险" in tags:
        tips.append("- 注意安全，建议家长全程陪同")
    
    # 默认小贴士
    if not tips:
        tips.append("- 建议提前查看天气")
        tips.append("- 周末人可能较多，建议早点出发")
    
    # 通用提示
    tips.append("- 记得带水和小零食")
    
    return "\n".join(tips)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="杭州亲子游玩地点推荐")
    parser.add_argument("--app-token", default=DEFAULT_APP_TOKEN, help="飞书多维表格 App Token")
    parser.add_argument("--table-id", default=DEFAULT_TABLE_ID, help="飞书多维表格 Table ID")
    parser.add_argument("--test", action="store_true", help="测试模式（使用模拟数据）")
    parser.add_argument("--age", type=int, help="孩子年龄")
    parser.add_argument("--indoor", action="store_true", help="偏好室内活动")
    parser.add_argument("--outdoor", action="store_true", help="偏好户外活动")
    
    args = parser.parse_args()
    
    if args.test:
        # 测试模式：使用模拟数据
        print("=== 测试模式 ===")
        print(f"当前季节：{get_current_season()}")
        print(f"推荐标签：{get_season_tags(get_current_season())}")
        
        test_records = [
            {
                "fields": {
                    "杭州亲子游玩地点库": "闲林老街",
                    "区域": "余杭区",
                    "适合年龄": "0 岁以上",
                    "特色标签": ["大草坪", "亲子餐厅", "购物中心"],
                    "推荐理由": "大草坪可以野餐奔跑，有盒马 NB 购物方便",
                    "推荐指数": "⭐⭐⭐⭐"
                }
            },
            {
                "fields": {
                    "杭州亲子游玩地点库": "中泰枫岭村 - 乌龟山",
                    "区域": "余杭区",
                    "适合年龄": "2 岁以上",
                    "特色标签": ["自然风光", "茶山", "小公园"],
                    "推荐理由": "茶山 + 小公园组合，自然风光好",
                    "推荐指数": "⭐⭐⭐⭐"
                }
            }
        ]
        
        indoor_pref = None
        if args.indoor:
            indoor_pref = True
        elif args.outdoor:
            indoor_pref = False
        
        selected = recommend_spot(test_records, child_age=args.age, indoor_preference=indoor_pref)
        print("\n" + format_recommendation(selected))
    else:
        # 实际模式：需要从飞书 API 获取数据
        print("实际使用请通过 OpenClaw 的 feishu_bitable_list_records 工具获取数据")
        print(f"App Token: {args.app_token}")
        print(f"Table ID: {args.table_id}")
        print("\n示例命令:")
        print(f"  feishu_bitable_list_records --app-token {args.app_token} --table-id {args.table_id}")


if __name__ == "__main__":
    main()
