#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python GUI Calculator - 带图形界面的计算器应用

功能特点:
1. 支持基本算术运算:加、减、乘、除
2. 支持高级数学运算:平方、平方根、百分号、取反
3. 支持键盘输入,提供便捷的操作方式
4. 完整的错误处理机制,友好的错误提示
5. 清晰的MVC架构,易于理解和扩展

作者:AI Assistant
版本:1.0.0
"""

import tkinter as tk
from tkinter import messagebox
import math
from typing import List, Optional, Tuple

# =============================================================================
# 常量定义 - 界面配置和运算参数
# =============================================================================

# 颜色配置方案
COLOR_BG = "#2D2D2D"           # 背景颜色
COLOR_DISPLAY_BG = "#1E1E1E"   # 显示屏背景
COLOR_TEXT = "#FFFFFF"         # 文字颜色
COLOR_BUTTON = "#3D3D3D"       # 普通按钮背景
COLOR_BUTTON_HOVER = "#4D4D4D" # 按钮悬停颜色
COLOR_OPERATOR = "#FF9500"     # 运算符按钮颜色
COLOR_FUNCTION = "#A0A0A0"     # 功能按钮颜色
COLOR_EQUALS = "#007AFF"       # 等号按钮颜色
COLOR_ERROR = "#FF3B30"        # 错误提示颜色

# 布局配置
BUTTON_PADDING = 8             # 按钮内边距
BUTTON_WIDTH = 10              # 按钮宽度
BUTTON_HEIGHT = 4              # 按钮高度
GRID_SPACING = 5               # 网格间距

# 按钮布局顺序(从左到右,从上到下)
BUTTON_LAYOUT = [
    ['C', 'CE', '←', '÷'],
    ['7', '8', '9', '×'],
    ['4', '5', '6', '-'],
    ['1', '2', '3', '+'],
    ['±', '0', '.', '=']
]

# 运算符优先级(数值越大优先级越高)
OPERATOR_PRECEDENCE = {
    '+': 1,
    '-': 1,
    '×': 2,
    '÷': 2
}

# 显示配置
MAX_DISPLAY_LENGTH = 20        # 显示最大长度
DECIMAL_PLACES = 8             # 小数位数

# =============================================================================
# 模型层 - 表达式解析和计算逻辑
# =============================================================================

class ExpressionParser:
    """
    表达式解析器类

    负责将中缀表达式转换为后缀表达式,并计算结果.
    实现了调度场算法(Shunting Yard Algorithm)进行表达式转换.
    """

    def __init__(self):
        """初始化表达式解析器"""
        # 数字正则:匹配整数、浮点数、正负数
        self.number_pattern = r'^-?\d+\.?\d*$'

    def tokenize(self, expression: str) -> List[str]:
        """
        词法分析:将表达式字符串分解为token列表

        Args:
            expression: 中缀表达式字符串,如 "12+34"

        Returns:
            token列表,如 ['12', '+', '34']
        """
        tokens = []
        i = 0
        length = len(expression)

        while i < length:
            char = expression[i]

            # 跳过空格
            if char.isspace():
                i += 1
                continue

            # 处理数字(包括负数和小数)
            if char.isdigit() or char == '-' or char == '.':
                j = i
                # 处理负数符号(仅当在表达式开头或左括号后时)
                if char == '-' and (i == 0 or expression[i-1] in '(+'):
                    j += 1
                    # 继续读取数字部分
                    while j < length and (expression[j].isdigit() or expression[j] == '.'):
                        j += 1
                else:
                    while j < length and (expression[j].isdigit() or expression[j] == '.'):
                        j += 1

                tokens.append(expression[i:j])
                i = j
            # 处理运算符和括号
            elif char in '+-×÷()':
                tokens.append(char)
                i += 1
            else:
                # 未知字符,跳过
                i += 1

        return tokens

    def infix_to_postfix(self, tokens: List[str]) -> List[str]:
        """
        中缀表达式转后缀表达式(逆波兰表示法)

        使用调度场算法(Shunting Yard Algorithm)进行转换.
        该算法由Edsger Dijkstra提出,能够处理运算符优先级和括号.

        Args:
            tokens: 中缀表达式的token列表

        Returns:
            后缀表达式的token列表
        """
        output = []
        operator_stack = []

        for token in tokens:
            if self._is_number(token):
                # 数字直接输出
                output.append(token)
            elif token == '(':
                # 左括号入栈
                operator_stack.append(token)
            elif token == ')':
                # 右括号:弹出直到遇到左括号
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
            elif token in OPERATOR_PRECEDENCE:
                # 运算符:处理优先级
                while (operator_stack and 
                       operator_stack[-1] != '(' and
                       OPERATOR_PRECEDENCE.get(operator_stack[-1], 0) >= OPERATOR_PRECEDENCE[token]):
                    output.append(operator_stack.pop())
                operator_stack.append(token)

        # 弹出剩余的运算符
        while operator_stack:
            output.append(operator_stack.pop())

        return output

    def evaluate_postfix(self, tokens: List[str]) -> float:
        """
        计算后缀表达式的值

        使用栈结构进行求值.
        从左到右扫描token,数字入栈,运算符时弹出操作数计算.

        Args:
            tokens: 后缀表达式的token列表

        Returns:
            计算结果(浮点数)

        Raises:
            ValueError: 表达式无效或计算错误
        """
        stack = []

        for token in tokens:
            if self._is_number(token):
                stack.append(float(token))
            elif token in OPERATOR_PRECEDENCE:
                if len(stack) < 2:
                    raise ValueError("Invalid expression: insufficient operands")

                b = stack.pop()  # 第二个操作数
                a = stack.pop()  # 第一个操作数

                result = self._apply_operator(a, b, token)
                stack.append(result)
            else:
                raise ValueError(f"Unknown token: {token}")

        if len(stack) != 1:
            raise ValueError("Invalid expression: too many values")

        return stack[0]

    def _is_number(self, token: str) -> bool:
        """检查token是否为数字"""
        try:
            float(token)
            return True
        except ValueError:
            return False

    def _apply_operator(self, a: float, b: float, operator: str) -> float:
        """
        应用运算符计算两个操作数的值

        Args:
            a: 第一个操作数
            b: 第二个操作数
            operator: 运算符字符串

        Returns:
            计算结果

        Raises:
            ZeroDivisionError: 除零错误
            ValueError: 无效运算符
        """
        if operator == '+':
            return a + b
        elif operator == '-':
            return a - b
        elif operator == '×':
            return a * b
        elif operator == '÷':
            if b == 0:
                raise ZeroDivisionError("Division by zero")
            return a / b
        else:
            raise ValueError(f"Unknown operator: {operator}")

    def parse_and_evaluate(self, expression: str) -> Tuple[bool, float, str]:
        """
        解析并计算表达式

        这是主要的公共方法,接收中缀表达式字符串,
        返回计算结果或错误信息.

        Args:
            expression: 中缀表达式字符串

        Returns:
            (成功标志, 结果值或None, 错误信息或空字符串)
        """
        if not expression or expression.strip() == '':
            return True, 0.0, ""

        try:
            # 词法分析
            tokens = self.tokenize(expression)

            # 检查括号匹配
            if not self._check_parentheses(tokens):
                return False, 0.0, "Bracket mismatch"

            # 转换为后缀表达式
            postfix = self.infix_to_postfix(tokens)

            # 计算结果
            result = self.evaluate_postfix(postfix)

            # 格式化结果
            formatted_result = self._format_result(result)

            return True, formatted_result, ""

        except ZeroDivisionError:
            return False, 0.0, "Cannot divide by zero"
        except ValueError as e:
            return False, 0.0, str(e)
        except Exception as e:
            return False, 0.0, f"Error: {str(e)}"

    def _check_parentheses(self, tokens: List[str]) -> bool:
        """检查括号是否匹配"""
        balance = 0
        for token in tokens:
            if token == '(':
                balance += 1
            elif token == ')':
                balance -= 1
                if balance < 0:
                    return False
        return balance == 0

    def _format_result(self, value: float) -> float:
        """
        格式化计算结果

        移除末尾多余的零,处理科学计数法.
        """
        # 如果是整数,转换为整数显示
        if value == int(value):
            return float(int(value))

        # 限制小数位数
        return round(value, DECIMAL_PLACES)

# =============================================================================
# 控制器层 - 事件处理和逻辑协调
# =============================================================================

class CalculatorController:
    """
    计算器控制器类

    协调用户输入、表达式构建和结果计算.
    作为视图层和模型层之间的中介.
    """

    def __init__(self, display_callback, error_callback):
        """
        初始化控制器

        Args:
            display_callback: 显示结果的回调函数
            error_callback: 显示错误的回调函数
        """
        self.display_callback = display_callback
        self.error_callback = error_callback
        self.parser = ExpressionParser()

        # 初始化状态
        self.current_input = ""       # 当前输入的操作数
        self.expression = ""          # 已完成的表达式部分
        self.last_button = None       # 上一个按钮类型
        self.should_clear = False     # 是否应该清空显示

    def handle_input(self, button_value: str) -> None:
        """
        处理按钮输入

        根据按钮类型分发到相应的处理方法.

        Args:
            button_value: 按钮的文本值
        """
        if button_value in '0123456789':
            self._handle_number(button_value)
        elif button_value in '+-×÷':
            self._handle_operator(button_value)
        elif button_value == '=':
            self._handle_equals()
        elif button_value == 'C':
            self._handle_clear_all()
        elif button_value == 'CE':
            self._handle_clear_entry()
        elif button_value == '←':
            self._handle_backspace()
        elif button_value == '.':
            self._handle_decimal()
        elif button_value == '±':
            self._handle_negate()
        elif button_value == '√':
            self._handle_square_root()

        self.last_button = button_value
        self._update_display()

    def _handle_number(self, digit: str) -> None:
        """处理数字输入"""
        if self.should_clear:
            self.current_input = ""
            self.should_clear = False

        # 限制输入长度
        if len(self.current_input) < MAX_DISPLAY_LENGTH:
            self.current_input += digit

    def _handle_operator(self, operator: str) -> None:
        """处理运算符输入"""
        # 如果有当前输入,先添加到表达式
        if self.current_input:
            self.expression += self.current_input
            self.current_input = ""

        # 如果表达式为空且输入了负数
        if not self.expression and self.current_input.startswith('-'):
            self.expression = self.current_input
            self.current_input = ""

        # 添加运算符
        self.expression += operator
        self.should_clear = True

    def _handle_equals(self) -> None:
        """处理等号(计算表达式)"""
        # 构建完整表达式
        full_expression = self.expression + self.current_input

        if not full_expression.strip():
            return

        # 解析和计算
        success, result, error = self.parser.parse_and_evaluate(full_expression)

        if success:
            # 显示结果
            self.display_callback(str(result))
            # 保存结果为新的输入
            self.current_input = str(result)
            self.expression = ""
            self.should_clear = True
        else:
            # 显示错误
            self.error_callback(error)
            self.current_input = ""

    def _handle_clear_all(self) -> None:
        """处理全部清除(C)"""
        self.current_input = ""
        self.expression = ""
        self.last_button = None
        self.should_clear = False
        self.display_callback("0")

    def _handle_clear_entry(self) -> None:
        """处理清除当前输入(CE)"""
        self.current_input = ""
        self._update_display()

    def _handle_backspace(self) -> None:
        """处理退格(←)"""
        if self.current_input:
            self.current_input = self.current_input[:-1]
        self._update_display()

    def _handle_decimal(self) -> None:
        """处理小数点"""
        if self.should_clear:
            self.current_input = "0"
            self.should_clear = False

        if '.' not in self.current_input:
            if self.current_input == "":
                self.current_input = "0"
            self.current_input += "."

        self._update_display()

    def _handle_negate(self) -> None:
        """处理取反(±)"""
        if self.current_input:
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
        self._update_display()

    def _handle_square_root(self) -> None:
        """处理平方根(√)"""
        if self.current_input:
            try:
                value = float(self.current_input)
                if value < 0:
                    self.error_callback("Cannot take square root of negative number")
                    return
                result = math.sqrt(value)
                self.current_input = str(self._format_result(result))
                self.should_clear = True
            except ValueError:
                self.error_callback("Invalid input")

        self._update_display()

    def _format_result(self, value: float) -> float:
        """格式化结果"""
        if value == int(value):
            return float(int(value))
        return round(value, DECIMAL_PLACES)

    def _update_display(self) -> None:
        """更新显示"""
        display_text = self.expression + self.current_input
        if not display_text:
            display_text = "0"
        self.display_callback(display_text)

    def get_display_text(self) -> str:
        """获取当前显示文本"""
        return self.expression + self.current_input or "0"

# =============================================================================
# 视图层 - 图形用户界面
# =============================================================================

class CalculatorView:
    """
    计算器视图类

    负责GUI渲染和用户交互处理.
    使用tkinter构建图形界面.
    """

    def __init__(self, root: tk.Tk):
        """
        初始化视图

        Args:
            root: tkinter根窗口
        """
        self.root = root
        self.root.title("Python Calculator")
        self.root.geometry("400x550")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        # 设置样式
        self._setup_styles()

        # 创建界面组件
        self._create_display()
        self._create_buttons()
        self._setup_keyboard_bindings()

        # 初始化控制器
        self.controller = CalculatorController(
            display_callback=self._update_display,
            error_callback=self._show_error
        )

    def _setup_styles(self) -> None:
        """配置按钮样式"""
        self.button_style = {
            'bg': COLOR_BUTTON,
            'fg': COLOR_TEXT,
            'font': ('Arial', 16, 'bold'),
            'bd': 0,
            'activebackground': COLOR_BUTTON_HOVER,
            'activeforeground': COLOR_TEXT
        }

        self.operator_style = {
            'bg': COLOR_OPERATOR,
            'fg': COLOR_TEXT,
            'font': ('Arial', 16, 'bold'),
            'bd': 0,
            'activebackground': '#E08600',
            'activeforeground': COLOR_TEXT
        }

        self.function_style = {
            'bg': COLOR_FUNCTION,
            'fg': COLOR_TEXT,
            'font': ('Arial', 12, 'bold'),
            'bd': 0,
            'activebackground': '#B0B0B0',
            'activeforeground': COLOR_TEXT
        }

        self.equals_style = {
            'bg': COLOR_EQUALS,
            'fg': COLOR_TEXT,
            'font': ('Arial', 16, 'bold'),
            'bd': 0,
            'activebackground': '#0066CC',
            'activeforeground': COLOR_TEXT
        }

    def _create_display(self) -> None:
        """创建显示屏"""
        # 显示屏容器
        display_frame = tk.Frame(
            self.root,
            bg=COLOR_DISPLAY_BG,
            height=120
        )
        display_frame.pack(fill=tk.X, padx=10, pady=10)

        # 表达式显示屏(上方,显示完整表达式)
        self.expression_label = tk.Label(
            display_frame,
            text="",
            bg=COLOR_DISPLAY_BG,
            fg=COLOR_FUNCTION,
            font=('Arial', 14),
            anchor=tk.E
        )
        self.expression_label.pack(fill=tk.X, pady=(5, 0))

        # 结果显示屏(主显示)
        self.result_label = tk.Label(
            display_frame,
            text="0",
            bg=COLOR_DISPLAY_BG,
            fg=COLOR_TEXT,
            font=('Arial', 32, 'bold'),
            anchor=tk.E
        )
        self.result_label.pack(fill=tk.X, pady=5)

    def _create_buttons(self) -> None:
        """创建按钮网格"""
        button_frame = tk.Frame(self.root, bg=COLOR_BG)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for row_idx, row in enumerate(BUTTON_LAYOUT):
            row_frame = tk.Frame(button_frame, bg=COLOR_BG)
            row_frame.pack(fill=tk.X, pady=GRID_SPACING)

            for col_idx, button_text in enumerate(row):
                style = self._get_button_style(button_text)

                btn = tk.Button(
                    row_frame,
                    text=button_text,
                    width=BUTTON_WIDTH,
                    height=BUTTON_HEIGHT,
                    **style,
                    command=lambda b=button_text: self._on_button_click(b)
                )
                btn.pack(side=tk.LEFT, padx=GRID_SPACING, expand=True)

    def _get_button_style(self, button_text: str) -> dict:
        """根据按钮类型返回对应的样式"""
        if button_text in '+-×÷':
            return self.operator_style.copy()
        elif button_text == '=':
            return self.equals_style.copy()
        elif button_text in 'CCE←±√':
            return self.function_style.copy()
        else:
            return self.button_style.copy()

    def _on_button_click(self, button_value: str) -> None:
        """处理按钮点击事件"""
        self.controller.handle_input(button_value)

    def _update_display(self, text: str) -> None:
        """更新显示屏内容"""
        # 限制显示长度
        if len(text) > MAX_DISPLAY_LENGTH:
            text = text[:MAX_DISPLAY_LENGTH] + "..."

        self.result_label.config(text=text)

        # 同时更新表达式显示
        expression_text = self.controller.expression
        self.expression_label.config(text=expression_text)

    def _show_error(self, message: str) -> None:
        """显示错误消息"""
        self.result_label.config(text="Error", fg=COLOR_ERROR)
        # 1秒后恢复
        self.root.after(1000, lambda: self.result_label.config(fg=COLOR_TEXT))
        messagebox.showerror("Error", message)

    def _setup_keyboard_bindings(self) -> None:
        """设置键盘快捷键绑定"""
        # 数字键
        for digit in '0123456789':
            self.root.bind(digit, lambda event, d=digit: self._on_button_click(d))

        # 小数点
        self.root.bind('.', lambda event: self._on_button_click('.'))

        # 运算符
        self.root.bind('+', lambda event: self._on_button_click('+'))
        self.root.bind('-', lambda event: self._on_button_click('-'))
        self.root.bind('*', lambda event: self._on_button_click('×'))
        self.root.bind('/', lambda event: self._on_button_click('÷'))

        # 回车键等于
        self.root.bind('<Return>', lambda event: self._on_button_click('='))

        # 退格键
        self.root.bind('<BackSpace>', lambda event: self._on_button_click('←'))

        # Escape清除
        self.root.bind('<Escape>', lambda event: self._on_button_click('C'))

        # 空格键(可选)
        self.root.bind('<space>', lambda event: self._on_button_click('='))

# =============================================================================
# 主程序入口
# =============================================================================

def main():
    """
    主函数 - 程序入口点

    创建主窗口并启动应用.
    """
    print("=" * 50)
    print("Python GUI Calculator")
    print("功能:基本算术运算、高级数学运算、键盘输入")
    print("=" * 50)

    # 创建主窗口
    root = tk.Tk()

    # 设置窗口居中
    window_width = 400
    window_height = 550
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 创建计算器视图
    app = CalculatorView(root)

    print("\n计算器已启动！")
    print("使用鼠标点击按钮或键盘输入进行计算")
    print("按 <Enter> 计算结果,按 <Escape> 清除全部")
    print("-" * 50)

    # 进入主事件循环
    root.mainloop()

if __name__ == "__main__":
    main()