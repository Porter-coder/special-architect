#!/usr/bin/env python3
"""
Sleep Reminder Clock - 睡眠提醒时钟

一个轻量级应用程序,用于显示当前系统时间并根据用户配置的
睡眠作息时间自动判断是否应该休息.

功能特性:
- 实时时钟显示
- 可配置的睡眠时间表
- 视觉状态指示器
- 自动睡眠建议

作者: AI助手
版本: 1.0.0
"""

import sys
import time
from datetime import datetime, timedelta

# 应用配置常量
APP_NAME = "Sleep Reminder Clock"
APP_VERSION = "1.0.0"

# 默认睡眠时间配置 (24小时制)
DEFAULT_BEDTIME_HOUR = 22    # 默认就寝时间: 22:00 (晚上10点)
DEFAULT_WAKE_HOUR = 7        # 默认起床时间: 07:00 (早上7点)

def get_current_time_info():
    """
    获取当前系统时间的详细信息.

    返回包含当前日期时间的各个组成部分的字典,
    方便后续格式化显示和睡眠判断逻辑使用.

    返回:
        dict: 包含年、月、日、时、分、秒、星期几信息的字典
    """
    now = datetime.now()
    return {
        'year': now.year,
        'month': now.month,
        'day': now.day,
        'hour': now.hour,
        'minute': now.minute,
        'second': now.second,
        'weekday': now.weekday(),  # 0=Monday, 6=Sunday
        'timestamp': now
    }

def get_weekday_name(weekday_number):
    """
    将星期几的数字转换为中文名称.

    参数:
        weekday_number: 0-6之间的整数,0代表星期一

    返回:
        str: 星期几的中文名称
    """
    weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    return weekday_names[weekday_number]

def format_time_12h(hour, minute):
    """
    将24小时制时间转换为12小时制格式.

    参数:
        hour: 0-23之间的小时数
        minute: 0-59之间的分钟数

    返回:
        str: 12小时制时间字符串,格式如 "上午10:30" 或 "下午8:45"
    """
    if hour == 0:
        display_hour = 12
        period = "上午"
    elif hour < 12:
        display_hour = hour
        period = "上午"
    elif hour == 12:
        display_hour = 12
        period = "下午"
    else:
        display_hour = hour - 12
        period = "下午"

    return f"{period}{display_hour}:{minute:02d}"

def format_time_24h(hour, minute):
    """
    格式化24小时制时间为标准显示格式.

    参数:
        hour: 0-23之间的小时数
        minute: 0-59之间的分钟数

    返回:
        str: 24小时制时间字符串,格式如 "14:30"
    """
    return f"{hour:02d}:{minute:02d}"

def determine_sleep_status(current_hour, bedtime_hour, wake_hour):
    """
    根据当前时间和配置的睡眠时间判断睡眠状态.

    该函数使用智能判断逻辑来确定用户当前是否应该睡觉、
    是否已经睡过头、或者还剩多少时间需要准备睡觉.

    参数:
        current_hour: 当前小时 (0-23)
        bedtime_hour: 就寝时间小时 (0-23)
        wake_hour: 起床时间小时 (0-23)

    返回:
        tuple: (状态代码, 状态描述)
        状态代码: 
            0 = 应该睡觉了
            1 = 可以准备睡觉了(快到就寝时间)
            2 = 正常清醒状态
            3 = 睡过头了(超过起床时间)
    """
    if current_hour >= bedtime_hour or current_hour < wake_hour:
        return (0, "应该睡觉了")
    elif current_hour >= bedtime_hour - 2:
        return (1, "快到就寝时间了")
    elif current_hour >= wake_hour and current_hour < wake_hour + 2:
        return (3, "睡过头了,该起床了！")
    else:
        return (2, "保持清醒,好好利用时间")

def get_sleep_emoji(status_code):
    """
    根据睡眠状态代码返回对应的表情符号.

    参数:
        status_code: 0-3之间的状态代码

    返回:
        str: 代表当前状态的表情符号
    """
    emojis = {
        0: "😴",  # 应该睡觉
        1: "🛏️",  # 快到就寝时间
        2: "☀️",  # 清醒状态
        3: "⏰"   # 睡过头了
    }
    return emojis.get(status_code, "❓")

def calculate_hours_until(target_hour):
    """
    计算距离目标时间还有多少小时.

    参数:
        target_hour: 目标小时 (0-23)

    返回:
        int: 距离目标时间的小时数
    """
    current_hour = datetime.now().hour

    if current_hour <= target_hour:
        return target_hour - current_hour
    else:
        return 24 - current_hour + target_hour

def display_welcome():
    """
    显示程序欢迎信息和当前配置.
    """
    print("=" * 50)
    print(f"  {APP_NAME} v{APP_VERSION}")
    print("=" * 50)
    print()
    print("程序功能:")
    print("  - 实时显示当前系统时间")
    print("  - 自动判断是否应该睡觉")
    print("  - 提供睡眠建议")
    print()
    print(f"当前配置:")
    print(f"  - 就寝时间: {DEFAULT_BEDTIME_HOUR:02d}:00")
    print(f"  - 起床时间: {DEFAULT_WAKE_HOUR:02d}:00")
    print()
    print("-" * 50)

def display_time_and_status():
    """
    主显示函数,展示当前时间和睡眠状态.

    这是程序的核心显示函数,每次调用都会清空控制台
    并重新显示最新的时间信息和睡眠状态.
    """
    time_info = get_current_time_info()

    current_hour = time_info['hour']
    current_minute = time_info['minute']
    current_second = time_info['second']

    status_code, status_text = determine_sleep_status(
        current_hour, 
        DEFAULT_BEDTIME_HOUR, 
        DEFAULT_WAKE_HOUR
    )

    time_24h = format_time_24h(current_hour, current_minute)
    time_12h = format_time_12h(current_hour, current_minute)
    weekday = get_weekday_name(time_info['weekday'])
    date_str = f"{time_info['year']}年{time_info['month']}月{time_info['day']}日"

    emoji = get_sleep_emoji(status_code)

    print("\n" * 2)
    print("┌" + "─" * 48 + "┐")
    print("│" + " " * 48 + "│")
    print(f"│     当前时间                    {time_24h}     │")
    print(f"│     {date_str} {weekday}              │")
    print("│" + " " * 48 + "│")
    print("├" + "─" * 48 + "┤")
    print("│" + " " * 48 + "│")
    print(f"│     {emoji}  睡眠状态: {status_text}       │")
    print("│" + " " * 48 + "│")

    if status_code == 1:
        hours_left = calculate_hours_until(DEFAULT_BEDTIME_HOUR)
        print(f"│     还有 {hours_left} 小时就可以睡觉了        │")
    elif status_code == 2:
        hours_to_bed = calculate_hours_until(DEFAULT_BEDTIME_HOUR)
        hours_to_wake = calculate_hours_until(DEFAULT_WAKE_HOUR)
        print(f"│     距就寝还有 {hours_to_bed} 小时,距起床还有 {hours_to_wake} 小时    │")
    elif status_code == 0:
        hours_to_wake = calculate_hours_until(DEFAULT_WAKE_HOUR)
        print(f"│     距离起床还有 {hours_to_wake} 小时,好好休息    │")

    print("│" + " " * 48 + "│")
    print("└" + "─" * 48 + "┘")
    print()
    print(f"12小时制: {time_12h}  |  24小时制: {time_24h}  |  秒: {current_second:02d}")
    print()

def run_demo():
    """
    运行演示模式,展示程序的各种状态.

    演示模式会依次显示不同的睡眠状态,
    让用户了解程序在不同情况下的显示效果.
    """
    display_welcome()

    print("\n演示模式 - 展示不同状态下的显示效果:\n")

    demo_hours = [
        (21, "接近就寝时间 (21:00)"),
        (22, "应该睡觉了 (22:00)"),
        (2, "深夜熟睡中 (02:00)"),
        (7, "起床时间 (07:00)"),
        (12, "清醒工作时间 (12:00)")
    ]

    for demo_hour, description in demo_hours:
        print(f"\n{description}:")
        print("-" * 40)

        time_info = get_current_time_info()
        original_hour = time_info['hour']

        status_code, status_text = determine_sleep_status(
            demo_hour,
            DEFAULT_BEDTIME_HOUR,
            DEFAULT_WAKE_HOUR
        )

        print(f"睡眠状态: {status_text} {get_sleep_emoji(status_code)}")
        print()

    print("\n" + "=" * 50)
    print("实时时钟模式启动中...")
    print("(按 Ctrl+C 退出程序)")
    print("=" * 50)

def run_live_clock():
    """
    运行实时时钟模式,持续更新显示.

    在循环中每秒更新一次时间显示,
    使用清屏和重绘的方式实现动态效果.
    """
    try:
        while True:
            display_time_and_status()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n程序已退出.祝您生活愉快！\n")

def main():
    """
    程序主入口函数.

    根据命令行参数决定运行模式:
    - 无参数: 运行实时时钟模式
    - --demo: 运行演示模式

    默认显示欢迎信息,然后启动实时时钟.
    """
    display_welcome()

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        print("实时时钟运行中 (按 Ctrl+C 退出):\n")
        run_live_clock()

if __name__ == "__main__":
    main()