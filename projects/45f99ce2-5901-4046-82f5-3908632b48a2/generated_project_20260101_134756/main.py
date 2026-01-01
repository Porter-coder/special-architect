#!/usr/bin/env python3
"""
日志文件IP地址提取脚本

功能:从指定日志文件中解析并提取所有有效的IPv4地址.
用法:python ip_extractor.py <日志文件路径>
"""

import re
import argparse
import sys
from typing import List

# 预编译正则表达式以提高性能
IP_PATTERN = re.compile(
    r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
    r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
)

def is_valid_ip(ip: str) -> bool:
    """验证IPv4地址的有效性(每个段0-255)"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        return all(0 <= int(part) <= 255 for part in parts)
    except (ValueError, AttributeError):
        return False

def extract_ips_from_log(log_file_path: str) -> List[str]:
    """
    从日志文件中提取所有有效IP地址

    Args:
        log_file_path: 日志文件路径

    Returns:
        IP地址列表(保留重复项,如需去重可修改)

    Raises:
        FileNotFoundError: 文件不存在
        PermissionError: 无读取权限
    """
    ips = []
    try:
        with open(log_file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                matches = IP_PATTERN.findall(line)
                for match in matches:
                    if is_valid_ip(match):
                        ips.append(match)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        raise e
    return ips

def main():
    """主函数:处理命令行参数并执行提取"""
    parser = argparse.ArgumentParser(
        description='从日志文件中提取有效IP地址',
        epilog='示例: python ip_extractor.py /var/log/syslog'
    )
    parser.add_argument('log_file', help='日志文件的路径')
    parser.add_argument('-u', '--unique', action='store_true', 
                        help='仅输出唯一IP地址(去重)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='显示详细处理信息')

    args = parser.parse_args()

    try:
        ips = extract_ips_from_log(args.log_file)
    except FileNotFoundError:
        sys.exit(f"错误: 文件未找到 - {args.log_file}")
    except PermissionError:
        sys.exit(f"错误: 无权限读取文件 - {args.log_file}")
    except UnicodeDecodeError:
        sys.exit(f"错误: 文件编码不支持,请使用UTF-8编码的日志文件")
    except Exception as e:
        sys.exit(f"未知错误: {str(e)}")

    if not ips:
        print("未找到有效IP地址")
        return

    if args.unique:
        ips = list(set(ips))
        ips.sort()  # 排序以提高可读性

    if args.verbose:
        print(f"处理完成: 共找到 {len(ips)} 个IP地址")

    for ip in ips:
        print(ip)

if __name__ == '__main__':
    main()