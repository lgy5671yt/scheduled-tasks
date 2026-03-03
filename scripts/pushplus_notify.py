# encoding:utf-8
import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

PUSHPLUS_API = "http://www.pushplus.plus/send"
BEIJING_TZ = timezone(timedelta(hours=8))

# 定义重要假期日期（每年固定日期）
HOLIDAYS = [
    (1, 1, "元旦"),      # 1月1日
    (3, 8, "妇女节"),     # 3月8日
    (5, 1, "劳动节"),     # 5月1日
    (10, 1, "国庆节")     # 10月1日
]


def is_holiday_approaching(now):
    """检测是否距离假期还有一周"""
    today = now.date()
    approaching_holidays = []
    
    for month, day, name in HOLIDAYS:
        # 创建今年的假期日期
        holiday_date = datetime(now.year, month, day, tzinfo=BEIJING_TZ).date()
        # 计算距离假期的天数
        days_until = (holiday_date - today).days
        # 检查是否距离假期还有一周（7天）
        if days_until == 7:
            approaching_holidays.append((name, holiday_date))
    
    return approaching_holidays


def send_notification(token, title, content, template="markdown"):
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": template,
    }
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8")
    response = requests.post(PUSHPLUS_API, data=body, headers=headers, timeout=30)
    result = response.json()
    if result.get("code") == 200:
        print(f"推送成功: {title}")
    else:
        print(f"推送失败: {result.get('msg')}")
    return result


def main():
    token = os.environ.get("PUSHPLUS_TOKEN")
    if not token:
        print("错误: 未设置 PUSHPLUS_TOKEN")
        sys.exit(1)

    now = datetime.now(BEIJING_TZ)
    title = f"每日通知 - {now.strftime('%m月%d日')}"

    # 检查是否有即将到来的假期
    approaching_holidays = is_holiday_approaching(now)
    
    # 构建通知内容
    content = f"""## 定时任务报告

**时间**: {now.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)

**状态**: ✅ 正常运行

"""
    
    # 如果有即将到来的假期，添加提醒信息
    if approaching_holidays:
        content += "## 假期提醒\n\n"
        for holiday_name, holiday_date in approaching_holidays:
            content += f"⚠️ **{holiday_name}** 将于 {holiday_date.strftime('%Y年%m月%d日')} 到来，距离今天还有一周！\n\n"
        content += "---\n\n"
    else:
        content += "---\n\n"
    
    content += "> 此消息由 GitHub Actions 自动发送"

    send_notification(token, title, content)


if __name__ == "__main__":
    main()
