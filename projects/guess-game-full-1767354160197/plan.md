# 实现计划

## 用户需求
一个猜数字游戏，1-100之间随机生成数字，用户输入猜测，程序提示太大或太小，猜对后显示用了几次

## 详细计划
# 猜数字游戏 - 技术实现计划

## Phase 2: 详细技术规划文档

---

## 1. 总体架构与设计模式

### 1.1 架构概述

本项目采用**模块化单例架构**，基于面向过程编程范式实现，保持代码简洁性和可维护性。整体架构分为四个核心层次：

```
┌─────────────────────────────────────────────────────────────────┐
│                        表示层 (Presentation)                    │
│              游戏界面输出、用户交互提示、信息格式化               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        控制层 (Control)                         │
│              游戏主循环、流程控制、状态管理                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        业务逻辑层 (Business Logic)               │
│              随机数生成、猜测比较、输入验证、计数统计             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        基础设施层 (Infrastructure)               │
│              Python标准库、随机数模块、输入输出系统               │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 设计模式选择

| 模式 | 应用场景 | 优势 |
|------|---------|------|
| **顺序执行模式** | 游戏主流程控制 | 逻辑清晰、易于理解和调试 |
| **输入-处理-输出 (IPO)** | 每次用户交互 | 符合命令行程序的交互特性 |
| **状态机模式** | 游戏状态转换（进行中/结束/重玩） | 状态管理清晰、扩展性好 |
| **验证器模式** | 用户输入校验 | 输入处理逻辑内聚、复用性强 |

### 1.3 文件结构规划

```
number_guessing_game/
├── requirements.txt          # 依赖声明（标准库，无需外部依赖）
├── README.md                 # 项目说明文档
├── src/
│   ├── __init__.py          # 包初始化
│   ├── game_engine.py       # 核心游戏逻辑
│   ├── validator.py         # 输入验证模块
│   ├── display.py           # 界面输出模块
│   └── main.py              # 程序入口
└── tests/
    ├── __init__.py
    ├── test_validator.py    # 验证器单元测试
    └── test_game.py         # 游戏逻辑单元测试
```

---

## 2. 核心组件与职责

### 2.1 组件清单

| 组件名称 | 文件路径 | 职责 | 依赖 |
|---------|---------|------|------|
| **GameEngine** | `src/game_engine.py` | 游戏核心逻辑：生成目标数字、管理猜测次数、控制游戏状态 | Validator, Display |
| **InputValidator** | `src/validator.py` | 输入验证：类型检查、范围校验、空值处理 | 无外部依赖 |
| **DisplayManager** | `src/display.py` | 界面输出：欢迎信息、提示信息、结果展示 | 无外部依赖 |
| **MainEntry** | `src/main.py` | 程序入口：初始化游戏、处理命令行参数 | GameEngine |

### 2.2 组件详细设计

#### 2.2.1 InputValidator 组件

```python
# src/validator.py

class InputValidator:
    """
    输入验证器 - 负责所有用户输入的有效性校验
    
    核心职责：
    1. 检查输入是否为空
    2. 验证输入是否为有效整数
    3. 检查输入是否在指定范围内
    4. 返回标准化的验证结果
    """
    
    MIN_RANGE = 1
    MAX_RANGE = 100
    
    @classmethod
    def validate(cls, user_input: str) -> ValidationResult:
        """
        验证用户输入
        
        Args:
            user_input: 用户原始输入字符串
            
        Returns:
            ValidationResult: 包含验证状态、解析数值、错误消息
        """
        pass
    
    @staticmethod
    def is_integer(value: str) -> bool:
        """检查字符串是否为有效整数"""
        pass
```

**ValidationResult 数据结构**：

```python
@dataclass
class ValidationResult:
    """验证结果数据类"""
    is_valid: bool          # 是否通过验证
    value: Optional[int]   后的整 # 解析数值（失败时为None）
    message: str           # 验证消息（成功或错误描述）
```

#### 2.2.2 GameEngine 组件

```python
# src/game_engine.py

class GameEngine:
    """
    游戏引擎 - 猜数字游戏的核心逻辑控制器
    
    核心职责：
    1. 管理游戏状态（目标数字、猜测次数、游戏阶段）
    2. 生成符合要求的目标随机数
    3. 执行猜测比较逻辑
    4. 控制游戏流程（开始、进行、结束、重玩）
    """
    
    class GameState(Enum):
        """游戏状态枚举"""
        READY = "ready"           # 准备就绪
        PLAYING = "playing"       # 进行中
        WON = "won"               # 已胜利
        QUIT = "quit"             # 已退出
    
    def __init__(self, min_val: int = 1, max_val: int = 100):
        """初始化游戏引擎"""
        self.min_range = min_val
        self.max_range = max_val
        self.target_number = None
        self.guess_count = 0
        self.state = self.GameState.READY
    
    def start_new_game(self) -> None:
        """开始新游戏，重置所有状态"""
        pass
    
    def make_guess(self, number: int) -> GuessResult:
        """
        执行一次猜测
        
        Args:
            number: 玩家猜测的数字
            
        Returns:
            GuessResult: 包含比较结果和反馈信息
        """
        pass
    
    def get_statistics(self) -> GameStatistics:
        """获取当前游戏统计信息"""
        pass
    
    def should_continue(self) -> bool:
        """检查游戏是否继续进行"""
        pass
```

**GuessResult 数据结构**：

```python
@dataclass
class GuessResult:
    """猜测结果数据类"""
    is_correct: bool       # 是否猜中
    comparison: Comparison # 比较结果（小于/大于/等于）
    guess_number: int     # 猜测的数字
    total_attempts: int   # 当前总猜测次数
    hint_message: str     # 提示信息
```

#### 2.2.3 DisplayManager 组件

```python
# src/display.py

class DisplayManager:
    """
    界面显示管理器 - 处理所有与用户的文本交互
    
    核心职责：
    1. 显示游戏欢迎信息和规则说明
    2. 输出各种提示和反馈信息
    3. 格式化显示游戏结果和统计信息
    """
    
    WELCOME_TEMPLATE = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                   猜数字游戏 v1.0                          ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  规则：我想了一个 {min} 到 {max} 之间的数字，请猜猜看！      ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    
    @classmethod
    def show_welcome(cls) -> None:
        """显示欢迎信息"""
        pass
    
    @classmethod
    def show_prompt(cls, min_val: int, max_val: int) -> None:
        """显示输入提示"""
        pass
    
    @classmethod
    def show_hint(cls, comparison: Comparison, guess: int) -> None:
        """显示猜测提示"""
        pass
    
    @classmethod
    def show_success(cls, attempts: int) -> None:
        """显示胜利信息"""
        pass
    
    @classmethod
    def show_error(cls, message: str) -> None:
        """显示错误信息"""
        pass
    
    @classmethod
    def ask_replay(cls) -> bool:
        """询问是否再来一局"""
        pass
```

---

## 3. 数据流与处理逻辑

### 3.1 主流程数据流

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           主程序启动流程                                  │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │   创建GameEngine   │
                         │   创建DisplayMgr   │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │  Display.show
