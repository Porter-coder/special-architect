#!/usr/bin/env python3
"""
=======================================================================
命令行计算器应用 (CLI Calculator Application)
=======================================================================
版本: 1.0.0
作者: Python架构师
描述: 一个功能完整的命令行计算器,支持基本运算、表达式解析、
     历史记录管理和用户友好的交互体验.

架构设计模式:
- 分层架构 (Layered Architecture)
- 工厂模式 (Factory Pattern) - 用于创建运算操作
- 策略模式 (Strategy Pattern) - 用于处理不同运算策略
- 单例模式 (Singleton Pattern) - 用于历史记录管理

系统层级:
1. 表示层 (Presentation Layer) - 用户界面交互
2. 业务逻辑层 (Business Logic Layer) - 核心计算逻辑
3. 数据层 (Data Layer) - 历史记录存储

=======================================================================
"""

import sys
import re
import json
import os
from typing import Dict, List, Optional, Callable, Any, Tuple
from abc import ABC, abstractmethod
from datetime import datetime

# ============================================================================
# 第一层: 抽象基类 - 定义运算操作的统一接口
# ============================================================================

class AbstractOperation(ABC):
    """
    运算操作抽象基类

    所有具体运算操作都必须继承此类并实现execute方法.
    这确保了运算接口的一致性,便于扩展新的运算类型.
    """

    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        """执行运算操作,必须由子类实现"""
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        """获取运算符号"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取运算名称"""
        pass

# ============================================================================
# 第二层: 具体运算实现类
# ============================================================================

class AdditionOperation(AbstractOperation):
    """加法运算实现"""

    def execute(self, a: float, b: float) -> float:
        return a + b

    def get_symbol(self) -> str:
        return '+'

    def get_name(self) -> str:
        return '加法'

class SubtractionOperation(AbstractOperation):
    """减法运算实现"""

    def execute(self, a: float, b: float) -> float:
        return a - b

    def get_symbol(self) -> str:
        return '-'

    def get_name(self) -> str:
        return '减法'

class MultiplicationOperation(AbstractOperation):
    """乘法运算实现"""

    def execute(self, a: float, b: float) -> float:
        return a * b

    def get_symbol(self) -> str:
        return '*'

    def get_name(self) -> str:
        return '乘法'

class DivisionOperation(AbstractOperation):
    """除法运算实现"""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b

    def get_symbol(self) -> str:
        return '/'

    def get_name(self) -> str:
        return '除法'

class PowerOperation(AbstractOperation):
    """幂运算实现"""

    def execute(self, a: float, b: float) -> float:
        return a ** b

    def get_symbol(self) -> str:
        return '^'

    def get_name(self) -> str:
        return '幂运算'

class ModuloOperation(AbstractOperation):
    """取模运算实现"""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("除数不能为零")
        return a % b

    def get_symbol(self) -> str:
        return '%'

    def get_name(self) -> str:
        return '取模'

# ============================================================================
# 第三层: 工厂模式 - 创建运算操作实例
# ============================================================================

class OperationFactory:
    """
    运算工厂类

    使用工厂模式封装运算对象的创建过程,
    实现运算类型与调用代码的解耦.

    工厂模式优点:
    1. 集中管理运算对象的创建逻辑
    2. 便于添加新的运算类型
    3. 降低代码耦合度
    """

    _operations: Dict[str, Callable[[], AbstractOperation]] = {
        '+': lambda: AdditionOperation(),
        '-': lambda: SubtractionOperation(),
        '*': lambda: MultiplicationOperation(),
        '/': lambda: DivisionOperation(),
        '^': lambda: PowerOperation(),
        '%': lambda: ModuloOperation(),
    }

    @classmethod
    def create_operation(cls, symbol: str) -> AbstractOperation:
        """
        创建指定符号对应的运算对象

        Args:
            symbol: 运算符号 (+, -, *, /, ^, %)

        Returns:
            对应的运算操作对象

        Raises:
            ValueError: 如果运算符号不支持
        """
        creator = cls._operations.get(symbol)
        if creator is None:
            supported = ', '.join(cls._operations.keys())
            raise ValueError(f"不支持的运算符号: '{symbol}'.支持的运算: {supported}")
        return creator()

    @classmethod
    def is_valid_operator(cls, symbol: str) -> bool:
        """检查符号是否为有效的运算符"""
        return symbol in cls._operations

    @classmethod
    def get_supported_operators(cls) -> List[str]:
        """获取所有支持的运算符列表"""
        return list(cls._operations.keys())

# ============================================================================
# 第四层: 表达式解析器
# ============================================================================

class ExpressionParser:
    """
    表达式解析器

    负责将用户输入的字符串表达式解析为可计算的格式.
    支持基本的二元运算表达式,例如: "2 + 3", "10 * 5"

    解析流程:
    1. 清理空白字符
    2. 验证表达式格式
    3. 提取操作数和运算符
    4. 返回解析结果
    """

    # 匹配表达式: 数字 运算符 数字
    _pattern = re.compile(r'^\s*([+-]?\d*\.?\d+)\s*([\+\-\*/\^%])\s*([+-]?\d*\.?\d+)\s*$')

    @classmethod
    def parse(cls, expression: str) -> Tuple[float, str, float]:
        """
        解析表达式字符串

        Args:
            expression: 用户输入的表达式字符串

        Returns:
            Tuple[操作数1, 运算符, 操作数2]

        Raises:
            ValueError: 如果表达式格式无效
        """
        if not expression or not expression.strip():
            raise ValueError("表达式不能为空")

        match = cls._pattern.match(expression)
        if match is None:
            raise ValueError(
                "表达式格式无效.请使用格式: '数字 运算符 数字'\n"
                "例如: 2 + 3, 10.5 * 4, 8 / 2"
            )

        operand1_str = match.group(1)
        operator = match.group(2)
        operand2_str = match.group(3)

        # 处理省略的正号(如 "+5" -> "5")
        if operand1_str == '' or operand1_str == '+':
            operand1_str = '1'
        if operand1_str == '-':
            operand1_str = '-1'

        try:
            operand1 = float(operand1_str)
            operand2 = float(operand2_str)
        except ValueError as e:
            raise ValueError(f"数字转换失败: {e}")

        return operand1, operator, operand2

# ============================================================================
# 第五层: 历史记录管理器 - 单例模式
# ============================================================================

class HistoryManager:
    """
    历史记录管理器

    使用单例模式确保全局只有一个历史记录实例.
    负责管理计算历史记录的存储和检索.

    历史记录功能:
    - 记录每次计算
    - 查看计算历史
    - 清除历史记录
    - 持久化存储
    """

    _instance = None
    _history_file = "calculator_history.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._history = []
            cls._instance._load_history()
        return cls._instance

    def add_record(self, expression: str, result: float) -> None:
        """
        添加计算记录

        Args:
            expression: 计算表达式
            result: 计算结果
        """
        record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'expression': expression,
            'result': result
        }
        self._history.append(record)
        self._save_history()

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取历史记录

        Args:
            limit: 可选,限制返回记录数量

        Returns:
            历史记录列表
        """
        if limit is None:
            return self._history.copy()
        return self._history[-limit:].copy()

    def clear_history(self) -> None:
        """清空历史记录"""
        self._history = []
        self._save_history()

    def get_record_count(self) -> int:
        """获取历史记录总数"""
        return len(self._history)

    def _save_history(self) -> None:
        """保存历史记录到文件"""
        try:
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"警告: 无法保存历史记录: {e}")

    def _load_history(self) -> None:
        """从文件加载历史记录"""
        if os.path.exists(self._history_file):
            try:
                with open(self._history_file, 'r', encoding='utf-8') as f:
                    self._history = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"警告: 无法加载历史记录: {e}")
                self._history = []

# ============================================================================
# 第六层: 计算引擎 - 业务逻辑核心
# ============================================================================

class CalculatorEngine:
    """
    计算引擎

    应用程序的核心组件,负责协调各个模块完成计算任务.

    引擎职责:
    1. 接收用户输入
    2. 调用表达式解析器
    3. 使用工厂模式创建运算
    4. 执行计算
    5. 记录到历史
    6. 返回结果
    """

    def __init__(self):
        self.operation_factory = OperationFactory()
        self.history_manager = HistoryManager()

    def calculate(self, expression: str) -> float:
        """
        执行计算

        Args:
            expression: 用户输入的表达式

        Returns:
            计算结果

        Raises:
            ValueError: 表达式格式错误
            RuntimeError: 计算过程中发生错误
        """
        try:
            # 解析表达式
            operand1, operator, operand2 = ExpressionParser.parse(expression)

            # 创建运算操作
            operation = self.operation_factory.create_operation(operator)

            # 执行计算
            result = operation.execute(operand1, operand2)

            # 记录到历史
            self.history_manager.add_record(expression, result)

            return result

        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"计算错误: {e}")

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """获取计算历史"""
        return self.history_manager.get_history(limit)

    def clear_history(self) -> None:
        """清空历史记录"""
        self.history_manager.clear_history()

# ============================================================================
# 第七层: 命令行界面 - 表示层
# ============================================================================

class CLIInterface:
    """
    命令行界面

    负责处理所有用户交互,包括:
    - 显示欢迎信息
    - 接收用户输入
    - 显示计算结果
    - 显示帮助信息

    界面特性:
    - 彩色输出提示
    - 清晰的错误信息
    - 友好的交互体验
    """

    # 颜色代码
    COLOR_HEADER = '\033[95m'
    COLOR_BLUE = '\033[94m'
    COLOR_GREEN = '\033[92m'
    COLOR_WARNING = '\033[93m'
    COLOR_ERROR = '\033[91m'
    COLOR_END = '\033[0m'
    COLOR_BOLD = '\033[1m'

    def __init__(self):
        self.engine = CalculatorEngine()
        self.running = True

    def print_welcome(self) -> None:
        """显示欢迎信息"""
        print(f"\n{self.COLOR_HEADER}{self.COLOR_BOLD}")
        print("=" * 60)
        print("         命令行计算器 (CLI Calculator)")
        print("=" * 60)
        print(f"{self.COLOR_END}")
        print("支持的基本运算: 加(+), 减(-), 乘(*), 除(/), 幂(^), 取模(%)")
        print("输入格式示例: 2 + 3, 10.5 * 4, 8 / 2")
        print("\n可用命令:")
        print("  history - 查看计算历史")
        print("  clear   - 清空历史记录")
        print("  help    - 显示帮助信息")
        print("  quit    - 退出程序")
        print("-" * 60)

    def print_help(self) -> None:
        """显示帮助信息"""
        print(f"\n{self.COLOR_HEADER}=== 帮助信息 ==={self.COLOR_END}")
        print("使用方法:")
        print("  直接输入表达式进行计算,例如: 5 + 3")
        print("  支持浮点数,例如: 2.5 * 4.2")
        print("\n运算符说明:")
        print("  +  加法: a + b")
        print("  -  减法: a - b")
        print("  *  乘法: a * b")
        print("  /  除法: a / b (注意: 除数不能为零)")
        print("  ^  幂运算: a ^ b (计算a的b次方)")
        print("  %  取模: a % b (计算a除以b的余数)")
        print("\n历史记录命令:")
        print("  history      - 查看所有历史记录")
        print("  history 5    - 查看最近5条记录")
        print("  clear        - 清空历史记录")
        print("-" * 60)

    def print_error(self, message: str) -> None:
        """显示错误信息"""
        print(f"{self.COLOR_ERROR}错误: {message}{self.COLOR_END}")

    def print_result(self, expression: str, result: float) -> None:
        """显示计算结果"""
        print(f"{self.COLOR_GREEN}计算结果:{self.COLOR_END}")
        print(f"  {expression} = {result}")

    def print_history(self, history: List[Dict], limit: Optional[int] = None) -> None:
        """显示历史记录"""
        if not history:
            print(f"{self.COLOR_WARNING}暂无历史记录{self.COLOR_END}")
            return

        count = len(history)
        print(f"\n{self.COLOR_HEADER}=== 计算历史 (共{count}条) ==={self.COLOR_END}")

        for i, record in enumerate(history, 1):
            timestamp = record['timestamp']
            expression = record['expression']
            result = record['result']
            print(f"{i:3d}. [{timestamp}] {expression} = {result}")
        print("-" * 60)

    def get_input(self) -> str:
        """获取用户输入"""
        return input(f"\n{self.COLOR_BLUE}请输入表达式 (或输入命令): {self.COLOR_END}").strip()

    def process_command(self, command: str) -> bool:
        """
        处理特殊命令

        Args:
            command: 用户输入的命令

        Returns:
            True: 继续运行
            False: 退出程序
        """
        cmd = command.lower()

        if cmd == 'quit' or cmd == 'exit' or cmd == 'q':
            print(f"\n{self.COLOR_GREEN}感谢使用,再见！{self.COLOR_END}\n")
            return False

        elif cmd == 'help' or cmd == 'h' or cmd == '?':
            self.print_help()

        elif cmd == 'history' or cmd == 'hist':
            # 解析history命令,可能带参数
            parts = command.split()
            limit = None
            if len(parts) > 1:
                try:
                    limit = int(parts[1])
                except ValueError:
                    self.print_error("history命令参数必须是数字")
                    return True

            history = self.engine.get_history(limit)
            self.print_history(history, limit)

        elif cmd == 'clear':
            self.engine.clear_history()
            print(f"{self.COLOR_GREEN}历史记录已清空{self.COLOR_END}")

        else:
            self.print_error(f"未知命令: '{command}'")
            print("输入 'help' 查看可用命令")

        return True

    def run(self) -> None:
        """运行主程序循环"""
        self.print_welcome()

        while self.running:
            try:
                user_input = self.get_input()

                if not user_input:
                    continue

                # 检查是否为命令
                if user_input.startswith('/') or user_input.lower() in ['help', 'quit', 'exit', 'q', 'history', 'hist', 'clear', 'h', '?']:
                    should_continue = self.process_command(user_input)
                    if not should_continue:
                        self.running = False
                else:
                    # 执行计算
                    result = self.engine.calculate(user_input)
                    self.print_result(user_input, result)

            except KeyboardInterrupt:
                print(f"\n\n{self.COLOR_WARNING}检测到中断信号,正在退出...{self.COLOR_END}")
                break

            except EOFError:
                print(f"\n\n{self.COLOR_GREEN}再见！{self.COLOR_END}")
                break

# ============================================================================
# 主程序入口
# ============================================================================

def main():
    """
    程序主入口点

    创建CLI界面实例并启动程序.
    符合Python最佳实践的入口点设计.
    """
    try:
        interface = CLIInterface()
        interface.run()
    except Exception as e:
        print(f"\n{CLIInterface.COLOR_ERROR}程序发生严重错误: {e}{CLIInterface.COLOR_END}")
        print("请尝试重新运行程序")
        sys.exit(1)

if __name__ == "__main__":
    main()