import pygame
import random
import sys

# 游戏常量配置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20  # 网格大小（蛇每个节的大小）
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 155, 0)
DARK_GRAY = (40, 40, 40)

# 游戏速度控制
FPS = 10
SNAKE_SPEED = 10

class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("贪吃蛇游戏 - 方向键控制")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.game_over_font = pygame.font.SysFont("arial", 40)
        self.reset_game()

    def reset_game(self):
        """初始化游戏状态"""
        self.direction = (GRID_SIZE, 0)  # 初始向右移动
        self.head = [GRID_WIDTH // 2, GRID_HEIGHT // 2]  # 蛇头位置
        self.snake = [self.head.copy(),
                      [self.head[0] - GRID_SIZE, self.head[1]],
                      [self.head[0] - 2*GRID_SIZE, self.head[1]]]
        self.score = 0
        self.food = self.generate_food()
        self.game_over = False

    def generate_food(self):
        """生成随机位置的食物"""
        while True:
            x = random.randint(0, GRID_WIDTH-1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT-1) * GRID_SIZE
            food_pos = [x, y]
            if food_pos not in self.snake:
                return food_pos

    def handle_key_events(self):
        """处理键盘输入"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                else:
                    # 防止反向移动
                    if event.key == pygame.K_LEFT and self.direction != (GRID_SIZE, 0):
                        self.direction = (-GRID_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-GRID_SIZE, 0):
                        self.direction = (GRID_SIZE, 0)
                    elif event.key == pygame.K_UP and self.direction != (0, GRID_SIZE):
                        self.direction = (0, -GRID_SIZE)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -GRID_SIZE):
                        self.direction = (0, GRID_SIZE)

    def move_snake(self):
        """移动蛇"""
        if self.game_over:
            return

        # 计算新的蛇头位置
        new_head = [self.snake[0][0] + self.direction[0], 
                   self.snake[0][1] + self.direction[1]]

        # 检查是否撞墙
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT):
            self.game_over = True
            return

        # 检查是否撞到自己
        if new_head in self.snake:
            self.game_over = True
            return

        # 移动蛇
        self.snake.insert(0, new_head)

        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
        else:
            self.snake.pop()  # 移除蛇尾

    def draw(self):
        """绘制游戏界面"""
        self.screen.fill(BLACK)

        # 绘制网格（可选，增加视觉效果）
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, DARK_GRAY, (0, y), (SCREEN_WIDTH, y))

        # 绘制蛇
        for i, part in enumerate(self.snake):
            color = GREEN if i == 0 else DARK_GREEN  # 蛇头颜色不同
            pygame.draw.rect(self.screen, color, 
                            (part[0], part[1], GRID_SIZE, GRID_SIZE))
            # 给蛇身添加边框
            pygame.draw.rect(self.screen, BLACK, 
                            (part[0], part[1], GRID_SIZE, GRID_SIZE), 1)

        # 绘制食物
        pygame.draw.rect(self.screen, RED, 
                        (self.food[0], self.food[1], GRID_SIZE, GRID_SIZE))

        # 绘制分数
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # 绘制游戏结束信息
        if self.game_over:
            game_over_text = self.game_over_font.render("游戏结束!", True, RED)
            restart_text = self.font.render("按 R 重新开始 或 Q 退出", True, WHITE)

            # 居中显示
            self.screen.blit(game_over_text, 
                            (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                             SCREEN_HEIGHT//2 - 100))
            self.screen.blit(restart_text, 
                            (SCREEN_WIDTH//2 - restart_text.get_width()//2, 
                             SCREEN_HEIGHT//2 + 50))

        pygame.display.update()

    def run(self):
        """主游戏循环"""
        while True:
            self.handle_key_events()
            self.move_snake()
            self.draw()
            self.clock.tick(SNAKE_SPEED)

if __name__ == "__main__":
    game = SnakeGame()
    game.run()