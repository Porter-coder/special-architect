"""
Mock Service for Development Mode

Provides mock responses for development and testing purposes.
Allows the system to run without actual AI service connections.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4
import time

from ..models.code_generation_request import CodeGenerationRequest, RequestStatus
from ..models.process_phase import ProcessPhase, PhaseName, get_phase_message
from ..models.generated_project import GeneratedProject


class MockService:
    """
    Mock service that provides development mode responses.

    This service simulates AI responses and external service calls
    for development and testing purposes.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mock_projects: Dict[UUID, GeneratedProject] = {}
        self.mock_requests: Dict[UUID, CodeGenerationRequest] = {}

    async def validate_connection(self) -> bool:
        """
        Mock connection validation - always returns True for development mode.

        Returns:
            bool: Always True in development mode
        """
        self.logger.info("Mock service: Connection validation (always True)")
        return True

    async def generate_code_stream(self, request: CodeGenerationRequest):
        """
        Mock code generation that simulates the three-phase process.

        Args:
            request: Code generation request

        Yields:
            Dict: Streaming events simulating the generation process
        """
        try:
            # Update request status to processing
            request.update_status(RequestStatus.PROCESSING)

            # Phase 1: Specify - Mock specification generation
            yield {
                "type": "phase_start",
                "phase": "specify",
                "message": "正在分析用户需求并制定规范..."
            }

            await asyncio.sleep(0.5)  # Simulate processing time

            mock_spec = f"""# 项目规范：{request.user_input}

## 功能需求
- 用户请求：{request.user_input}
- 应用类型：控制台应用
- 编程语言：Python

## 技术架构
- 主框架：标准库
- 依赖包：无额外依赖

## 验收标准
- 代码可直接运行
- 实现基本功能
- 包含错误处理
"""

            yield {
                "type": "content_chunk",
                "content_type": "markdown",
                "content": mock_spec,
                "phase": "specify"
            }

            yield {
                "type": "phase_complete",
                "phase": "specify",
                "result": "需求分析完成"
            }

            # Phase 2: Plan - Mock planning phase
            yield {
                "type": "phase_start",
                "phase": "plan",
                "message": "正在制定详细的实现计划..."
            }

            await asyncio.sleep(0.5)

            mock_plan = f"""# 实现计划：{request.user_input}

## 架构设计
- 主文件：main.py
- 辅助模块：utils.py（如果需要）

## 实现步骤
1. 创建主函数
2. 实现核心逻辑
3. 添加错误处理
4. 测试运行

## 代码结构
```
main.py
├── 函数定义
├── 主逻辑
└── 执行入口
```

## 预期结果
- 可运行的Python脚本
- 清晰的代码结构
- 基本的错误处理
"""

            yield {
                "type": "content_chunk",
                "content_type": "markdown",
                "content": mock_plan,
                "phase": "plan"
            }

            yield {
                "type": "phase_complete",
                "phase": "plan",
                "result": "实现计划制定完成"
            }

            # Phase 3: Implement - Mock code generation
            yield {
                "type": "phase_start",
                "phase": "implement",
                "message": "正在生成可执行代码..."
            }

            await asyncio.sleep(0.5)

            # Generate mock code based on user input
            mock_code = self._generate_mock_code(request.user_input)

            yield {
                "type": "content_chunk",
                "content_type": "python",
                "content": mock_code,
                "phase": "implement"
            }

            yield {
                "type": "phase_complete",
                "phase": "implement",
                "result": "代码生成完成"
            }

            # Create mock project
            project_id = request.request_id
            mock_project = GeneratedProject(
                id=project_id,
                project_name=f"mock_project_{project_id}",
                main_file="main.py",
                created_at=time.time(),
                syntax_validated=True,
                total_files=1,
                total_size_bytes=len(mock_code.encode('utf-8'))
            )

            # Store mock project
            self.mock_projects[project_id] = mock_project

            # Store project files (simplified)
            mock_project.files = {"main.py": mock_code}

            # Update request status
            request.update_status(RequestStatus.COMPLETED)

            yield {
                "type": "workflow_complete",
                "project_id": str(project_id),
                "main_file": "main.py"
            }

        except Exception as e:
            self.logger.error(f"Mock generation failed: {e}")
            request.update_status(RequestStatus.FAILED, str(e))
            yield {
                "type": "workflow_failed",
                "error": str(e)
            }

    def _generate_mock_code(self, user_input: str) -> str:
        """
        Generate mock Python code based on user input.

        Args:
            user_input: User's natural language request

        Returns:
            str: Mock Python code
        """
        # Simple pattern matching to generate appropriate mock code
        user_input_lower = user_input.lower()

        if "贪吃蛇" in user_input or "snake" in user_input_lower:
            return self._generate_snake_game()
        elif "计算器" in user_input or "calculator" in user_input_lower:
            return self._generate_calculator()
        elif "hello" in user_input_lower or "你好" in user_input:
            return self._generate_hello_world()
        else:
            return self._generate_generic_app(user_input)

    def _generate_snake_game(self) -> str:
        """Generate mock Snake game code."""
        return '''"""
贪吃蛇游戏 - 模拟版本
使用键盘方向键控制蛇移动，按ESC退出
"""

import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 游戏设置
BLOCK_SIZE = 20
FPS = 10

class SnakeGame:
    def __init__(self):
        self.width = 640
        self.height = 480
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("贪吃蛇游戏")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.snake = [(self.width//2, self.height//2)]
        self.direction = (0, -BLOCK_SIZE)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def generate_food(self):
        while True:
            x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            if (x, y) not in self.snake:
                return (x, y)

    def draw(self):
        self.screen.fill(BLACK)

        # 绘制蛇
        for x, y in self.snake:
            pygame.draw.rect(self.screen, GREEN, (x, y, BLOCK_SIZE, BLOCK_SIZE))

        # 绘制食物
        pygame.draw.rect(self.screen, RED, (self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))

        # 显示分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != (0, BLOCK_SIZE):
                        self.direction = (0, -BLOCK_SIZE)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -BLOCK_SIZE):
                        self.direction = (0, BLOCK_SIZE)
                    elif event.key == pygame.K_LEFT and self.direction != (BLOCK_SIZE, 0):
                        self.direction = (-BLOCK_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-BLOCK_SIZE, 0):
                        self.direction = (BLOCK_SIZE, 0)
                    elif event.key == pygame.K_ESCAPE:
                        self.game_over = True

            if not self.game_over:
                # 移动蛇
                head = (self.snake[0][0] + self.direction[0],
                       self.snake[0][1] + self.direction[1])

                # 检查碰撞边界
                if (head[0] < 0 or head[0] >= self.width or
                    head[1] < 0 or head[1] >= self.height or
                    head in self.snake):
                    self.game_over = True
                    continue

                self.snake.insert(0, head)

                # 检查吃到食物
                if head == self.food:
                    self.score += 1
                    self.food = self.generate_food()
                else:
                    self.snake.pop()

                self.draw()
                self.clock.tick(FPS)

        # 游戏结束显示
        font = pygame.font.Font(None, 48)
        game_over_text = font.render("游戏结束!", True, WHITE)
        score_text = font.render(f"最终分数: {self.score}", True, WHITE)

        self.screen.blit(game_over_text, (self.width//2 - 100, self.height//2 - 50))
        self.screen.blit(score_text, (self.width//2 - 100, self.height//2))
        pygame.display.flip()

        pygame.time.wait(3000)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
    pygame.quit()
    sys.exit()
'''

    def _generate_calculator(self) -> str:
        """Generate mock calculator code."""
        return '''"""
简单计算器 - 模拟版本
支持基本的四则运算
"""

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ValueError("除数不能为零")
    return x / y

def main():
    print("简单计算器")
    print("支持的操作: +, -, *, /")

    while True:
        try:
            # 获取用户输入
            expression = input("请输入表达式 (例如: 2 + 3)，或 'q' 退出: ").strip()

            if expression.lower() == 'q':
                print("谢谢使用!")
                break

            # 解析表达式
            parts = expression.split()
            if len(parts) != 3:
                print("格式错误，请使用: 数字 操作符 数字")
                continue

            num1 = float(parts[0])
            operator = parts[1]
            num2 = float(parts[2])

            # 执行计算
            if operator == '+':
                result = add(num1, num2)
            elif operator == '-':
                result = subtract(num1, num2)
            elif operator == '*':
                result = multiply(num1, num2)
            elif operator == '/':
                result = divide(num1, num2)
            else:
                print(f"不支持的操作符: {operator}")
                continue

            print(f"结果: {result}")

        except ValueError as e:
            print(f"输入错误: {e}")
        except Exception as e:
            print(f"计算错误: {e}")

if __name__ == "__main__":
    main()
'''

    def _generate_hello_world(self) -> str:
        """Generate mock hello world code."""
        return '''"""
Hello World 程序 - 模拟版本
"""

def main():
    print("Hello, World!")
    print("欢迎使用 AI Code Flow!")

    # 获取用户输入
    name = input("请输入您的名字: ")
    print(f"您好, {name}!")

    # 显示一些基本信息
    print(f"Python 版本: {__import__('sys').version}")
    print("程序运行正常!")

if __name__ == "__main__":
    main()
'''

    def _generate_generic_app(self, user_input: str) -> str:
        """Generate generic mock application code."""
        return f'''"""
通用应用程序 - 基于用户请求生成
用户请求: {user_input}
"""

def main():
    print("通用应用程序")
    print(f"用户请求: {user_input}")
    print()

    # 模拟应用程序功能
    print("应用程序正在运行...")

    # 简单的交互循环
    while True:
        command = input("请输入命令 (quit 退出): ").strip().lower()

        if command == 'quit':
            print("谢谢使用!")
            break
        elif command == 'help':
            print("可用命令: help, info, quit")
        elif command == 'info':
            print(f"应用程序信息: {user_input}")
        else:
            print(f"执行命令: {command}")

if __name__ == "__main__":
    main()
'''

    def get_mock_project(self, project_id: UUID) -> Optional[GeneratedProject]:
        """
        Get mock project by ID.

        Args:
            project_id: Project identifier

        Returns:
            GeneratedProject or None if not found
        """
        return self.mock_projects.get(project_id)

    def list_mock_projects(self) -> List[GeneratedProject]:
        """
        List all mock projects.

        Returns:
            List of GeneratedProject objects
        """
        return list(self.mock_projects.values())
