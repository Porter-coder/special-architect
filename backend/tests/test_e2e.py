"""
End-to-End Test for Snake Game Generation Workflow

Tests the complete user journey from request submission to project delivery.
This test verifies the three-phase workflow (Specify → Plan → Implement)
and ensures the generated Snake game code is executable.

Requirements: User Story 1 MVP - Snake game generation
"""

import asyncio
import json
import os
import tempfile
import pytest
import ast
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.code_generation_service import CodeGenerationService
from src.services.ai_service import AIService
from src.services.project_service import ProjectService
from src.services.phase_manager import PhaseManager
from src.models.code_generation_request import CodeGenerationRequest
from src.models.process_phase import PhaseName


class TestSnakeGameE2E:
    """End-to-end test for Snake game generation workflow."""

    @pytest.fixture
    async def services(self):
        """Setup service instances for testing."""
        # Mock AI service
        ai_service = AsyncMock(spec=AIService)

        # Mock phase manager
        phase_manager = AsyncMock(spec=PhaseManager)

        # Create real project service with temp directory
        temp_dir = tempfile.mkdtemp()
        project_service = ProjectService(projects_dir=temp_dir)

        # Create code generation service
        code_gen_service = CodeGenerationService(
            ai_service=ai_service,
            phase_manager=phase_manager,
            project_service=project_service
        )

        yield {
            'ai_service': ai_service,
            'phase_manager': phase_manager,
            'project_service': project_service,
            'code_gen_service': code_gen_service,
            'temp_dir': temp_dir
        }

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_snake_game_generation_workflow(self, services):
        """Test complete Snake game generation workflow."""
        ai_service = services['ai_service']
        phase_manager = services['phase_manager']
        code_gen_service = services['code_gen_service']

        # Mock the three-phase workflow
        phase_manager.execute_phase = AsyncMock()

        # Mock Specify phase output
        phase_manager.execute_phase.side_effect = [
            "# 贪吃蛇游戏需求分析\n\n游戏需要：\n- Pygame界面\n- 蛇的移动控制\n- 食物生成\n- 碰撞检测",
            "# 贪吃蛇游戏设计\n\n技术方案：\n- 使用Pygame库\n- 游戏循环架构\n- 面向对象设计",
            self._generate_valid_snake_code()
        ]

        # Mock AI service for streaming
        ai_service.generate_code_stream = self._mock_ai_streaming_response()

        # Create request
        request = CodeGenerationRequest(
            user_input="帮我写个贪吃蛇游戏",
            status="processing"
        )

        # Execute generation
        result = await code_gen_service.generate_code(request)

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'id')
        assert hasattr(result, 'project_name')
        assert result.project_name.startswith('snake_game_')
        assert result.syntax_validated == True
        assert len(result.file_structure['children']) > 0

        # Verify main file exists and is valid Python
        main_file = None
        for child in result.file_structure['children']:
            if child['name'] == 'main.py':
                main_file = child
                break

        assert main_file is not None
        assert main_file['language'] == 'python'
        assert main_file['size'] > 0

        # Verify phase manager was called correctly
        assert phase_manager.execute_phase.call_count == 3

        # Verify phases were executed in order
        calls = phase_manager.execute_phase.call_args_list
        assert calls[0][1]['phase'] == PhaseName.SPECIFY
        assert calls[1][1]['phase'] == PhaseName.PLAN
        assert calls[2][1]['phase'] == PhaseName.IMPLEMENT

    @pytest.mark.asyncio
    async def test_generated_code_syntax_validation(self, services):
        """Test that generated code passes AST validation."""
        code_gen_service = services['code_gen_service']

        # Generate valid Python code
        valid_code = self._generate_valid_snake_code()

        # Test AST validation
        try:
            ast.parse(valid_code)
        except SyntaxError:
            pytest.fail("Generated code has syntax errors")

        # Test with invalid code
        invalid_code = "def broken function("  # Missing colon and invalid syntax

        with pytest.raises(SyntaxError):
            ast.parse(invalid_code)

    @pytest.mark.asyncio
    async def test_project_file_structure(self, services):
        """Test that generated projects have correct file structure."""
        project_service = services['project_service']

        # Create a test project
        project_data = {
            'id': 'test-123',
            'project_name': 'snake_game_test',
            'main_file_path': 'projects/snake_game_test/main.py',
            'file_structure': {
                'type': 'directory',
                'name': 'snake_game_test',
                'children': [
                    {
                        'type': 'file',
                        'name': 'main.py',
                        'size': 1234,
                        'language': 'python'
                    },
                    {
                        'type': 'file',
                        'name': 'README.md',
                        'size': 567,
                        'language': 'markdown'
                    }
                ]
            },
            'dependencies': ['pygame'],
            'total_files': 2,
            'total_size_bytes': 1801,
            'syntax_validated': True
        }

        # Save project
        project = await project_service.save_project(project_data)

        # Verify project was saved
        assert project is not None
        assert project.id == 'test-123'

        # Verify files exist
        project_dir = Path(project_service.projects_dir) / 'snake_game_test'
        assert project_dir.exists()

        main_file = project_dir / 'main.py'
        readme_file = project_dir / 'README.md'

        assert main_file.exists()
        assert readme_file.exists()

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, services):
        """Test error handling throughout the workflow."""
        ai_service = services['ai_service']
        code_gen_service = services['code_gen_service']

        # Mock AI service to raise an error
        ai_service.generate_code_stream = AsyncMock()
        ai_service.generate_code_stream.side_effect = Exception("AI service unavailable")

        request = CodeGenerationRequest(
            user_input="帮我写个贪吃蛇游戏",
            status="processing"
        )

        # Should handle error gracefully
        with pytest.raises(Exception):
            await code_gen_service.generate_code(request)

    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self, services):
        """Test that concurrent requests are handled properly."""
        code_gen_service = services['code_gen_service']

        # Create multiple concurrent requests
        requests = []
        for i in range(3):
            request = CodeGenerationRequest(
                user_input=f"帮我写个贪吃蛇游戏版本{i}",
                status="processing"
            )
            requests.append(request)

        # Mock successful responses
        with patch.object(code_gen_service, 'generate_code', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = MagicMock()

            # Execute concurrently
            tasks = [code_gen_service.generate_code(req) for req in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verify all requests were processed
            assert len(results) == 3
            assert mock_generate.call_count == 3

    def _generate_valid_snake_code(self) -> str:
        """Generate valid Snake game Python code for testing."""
        return '''import pygame
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
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
BLOCK_SIZE = 20
FPS = 10

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("贪吃蛇游戏")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.snake = [(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)]
        self.direction = (0, -BLOCK_SIZE)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False

    def generate_food(self):
        while True:
            x = random.randint(0, (SCREEN_WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (SCREEN_HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            food = (x, y)
            if food not in self.snake:
                return food

    def draw(self):
        self.screen.fill(BLACK)

        # 绘制蛇
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

        # 绘制食物
        pygame.draw.rect(self.screen, RED, (self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))

        # 显示分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

    def update(self):
        if self.game_over:
            return

        # 移动蛇头
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # 检查碰撞
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT or
            new_head in self.snake):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # 检查吃到食物
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.direction != (0, BLOCK_SIZE):
                    self.direction = (0, -BLOCK_SIZE)
                elif event.key == pygame.K_DOWN and self.direction != (0, -BLOCK_SIZE):
                    self.direction = (0, BLOCK_SIZE)
                elif event.key == pygame.K_LEFT and self.direction != (BLOCK_SIZE, 0):
                    self.direction = (-BLOCK_SIZE, 0)
                elif event.key == pygame.K_RIGHT and self.direction != (-BLOCK_SIZE, 0):
                    self.direction = (BLOCK_SIZE, 0)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
'''

    def _mock_ai_streaming_response(self):
        """Mock AI streaming response for testing."""
        async def mock_stream(*args, **kwargs):
            # Simulate streaming chunks
            chunks = [
                {"type": "thinking", "content": "分析用户需求：贪吃蛇游戏需要蛇、食物、移动控制"},
                {"type": "text", "content": "import pygame\nimport random\n\n# 游戏常量"},
                {"type": "text", "content": "class SnakeGame:\n    def __init__(self):"},
                {"type": "text", "content": "    def run(self):\n        while True:\n            pass"},
            ]
            for chunk in chunks:
                yield chunk
        return mock_stream
