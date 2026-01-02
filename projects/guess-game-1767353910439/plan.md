# 实现计划

## 用户需求
一个猜数字游戏，1-100之间随机生成数字，用户输入猜测，程序提示太大或太小，猜对后显示用了几次

## 详细计划
# PHASE 2: 猜数字游戏 - 技术规划与系统设计

## 1. 总体架构设计

### 1.1 架构概述

本项目采用**分层架构模式**，将用户交互层、游戏逻辑层和数据持久层进行清晰分离。这种设计确保了代码的可维护性、可扩展性和可测试性。整体架构遵循"关注点分离"原则，使得各层之间通过明确定义的接口进行通信，降低模块间的耦合度。

```
┌─────────────────────────────────────────────────────────────────┐
│                      表示层 (Presentation Layer)                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   GameUI (用户界面模块)                  │   │
│  │  ├── display_welcome()    - 显示欢迎信息                 │   │
│  │  ├── display_hint()       - 显示提示信息                 │   │
│  │  ├── display_result()     - 显示游戏结果                 │   │
│  │  └── get_user_input()     - 获取用户输入                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      业务逻辑层 (Business Logic Layer)           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                GuessNumberGame (核心游戏类)              │   │
│  │  ├── __init__()         - 初始化游戏状态                 │   │
│  │  ├── start_game()       - 启动游戏流程                   │   │
│  │  ├── make_guess()       - 处理用户猜测                   │   │
│  │  ├── check_guess()      - 验证猜测结果                   │   │
│  │  └── reset_game()       - 重置游戏状态                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      数据访问层 (Data Access Layer)              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                GameRecordManager (记录管理器)            │   │
│  │  ├── load_best_record()  - 加载历史最佳记录             │   │
│  │  ├── save_best_record()  - 保存最佳记录                 │   │
│  │  └── update_record()     - 更新记录                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      基础设施层 (Infrastructure Layer)           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   InputValidator (输入验证器)            │   │
│  │                   DifficultyManager (难度管理器)         │   │
│  │                   GameLogger (游戏日志)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 设计模式应用

本项目采用多种经典设计模式来确保代码的灵活性和可维护性。

**策略模式 (Strategy Pattern)** 被应用于处理不同的难度级别。每个难度级别可以视为一个独立的策略，包含各自的数字范围和提示规则。这种设计使得添加新难度级别时无需修改核心游戏逻辑，只需实现统一的难度策略接口即可。

**状态模式 (State Pattern)** 用于管理游戏的不同状态，包括等待输入状态、猜测处理状态、游戏结束状态等。这种设计使得状态转换逻辑清晰可控，便于扩展和维护。

**单例模式 (Singleton Pattern)** 被应用于记录管理器，确保全局只有一个最佳记录实例，避免数据不一致问题。

**工厂模式 (Factory Pattern)** 用于创建不同类型的游戏实例，支持快速扩展游戏变体。

### 1.3 模块依赖关系

```
main.py (入口模块)
    │
    ├── GameUI (用户界面)
    │       │
    │       └── InputValidator (依赖输入验证)
    │
    ├── GuessNumberGame (核心游戏类)
    │       │
    │       ├── DifficultyManager (依赖难度管理)
    │       ├── GameRecordManager (依赖记录管理)
    │       └── GameLogger (依赖日志记录)
    │
    └── Config (配置常量)
```

---

## 2. 核心组件详细设计

### 2.1 主程序入口 (main.py)

主程序作为整个应用的入口点，负责协调各组件的初始化和运行流程。其设计遵循"最小职责原则"，仅负责程序的启动和退出处理，所有业务逻辑委托给专门的类去完成。

```python
# main.py - 程序入口
import sys
from game.ui import GameUI
from game.core import GuessNumberGame

def main():
    """程序主入口"""
    # 初始化UI和游戏核心
    ui = GameUI()
    game = GuessNumberGame()
    
    # 启动游戏循环
    try:
        while True:
            ui.display_welcome()
            difficulty = ui.select_difficulty()
            game.set_difficulty(difficulty)
            game.start_game()
            
            if not ui.ask_play_again():
                break
    except KeyboardInterrupt:
        ui.display_exit_message()
    except Exception as e:
        ui.display_error(str(e))
        sys.exit(1)
    
    ui.display_goodbye()

if __name__ == "__main__":
    main()
```

### 2.2 核心游戏类 (GuessNumberGame)

核心游戏类是整个系统的中枢，负责管理游戏状态、协调各组件工作、处理游戏核心逻辑。该类采用单例模式确保游戏状态的唯一性，同时提供清晰的公开接口供外部调用。

```python
# game/core/guess_number_game.py

import random
from typing import List, Optional, Dict
from enum import Enum

class GameState(Enum):
    """游戏状态枚举"""
    WAITING_FOR_INPUT = "waiting"
    PROCESSING_GUESS = "processing"
    GAME_WON = "won"
    GAME_ERROR = "error"

class Difficulty(Enum):
    """难度级别枚举"""
    EASY = {"name": "简单", "min": 1, "max": 100, "max_hints": 5}
    MEDIUM = {"name": "中等", "min": 1, "max": 1000, "max_hints": 8}
    HARD = {"name": "困难", "min": 1, "max": 10000, "max_hints": 10}

class GuessNumberGame:
    """
    猜数字游戏核心类
    
    Attributes:
        target_number (int): 目标数字
        guess_count (int): 当前猜测次数
        guess_history (List[int]): 猜测历史记录
        min_range (int): 范围最小值
        max_range (int): 范围最大值
        best_record (Optional[int]): 历史最佳记录
        game_state (GameState): 当前游戏状态
    """
    
    def __init__(self, record_manager=None):
        """初始化游戏状态"""
        self.target_number: int = 0
        self.guess_count: int = 0
        self.guess_history: List[int] = []
        self.min_range: int = 1
        self.max_range: int = 100
        self.best_record: Optional[int] = None
        self.game_state: GameState = GameState.WAITING_FOR_INPUT
        self.current_difficulty: Difficulty = Difficulty.EASY
        self._hint_count = 0
        
        # 依赖注入：记录管理器
        self.record_manager = record_manager
        if self.record_manager:
            self.best_record = self.record_manager.load_best_record()
    
    def set_difficulty(self, difficulty: Difficulty) -> None:
        """设置游戏难度"""
        self.current_difficulty = difficulty
        self.min_range = difficulty.value["min"]
        self.max_range = difficulty.value["max"]
    
    def start_game(self) -> None:
        """开始新游戏"""
        self._reset_game_state()
        self.target_number = random.randint(self.min_range, self.max_range)
        self.game_state = GameState.WAITING_FOR_INPUT
    
    def _reset_game_state(self) -> None:
        """重置游戏状态"""
        self.guess_count = 0
        self.guess_history = []
       
