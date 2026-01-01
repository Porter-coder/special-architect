import pygame
import time
import random

# --- 初始化 Pygame ---
pygame.init()

# --- 定义颜色 (R, G, B) ---
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# --- 游戏窗口设置 ---
DIS_WIDTH = 600
DIS_HEIGHT = 400

dis = pygame.display.set_mode((DIS_WIDTH, DIS_HEIGHT))
pygame.display.set_caption('贪吃蛇游戏 - Python & Pygame')

# --- 游戏参数 ---
clock = pygame.time.Clock()
SNAKE_BLOCK = 10  # 蛇身每一节的大小
SNAKE_SPEED = 15  # 蛇的移动速度

# --- 字体设置 ---
font_style = pygame.font.SysFont("bahnschrift", 25) # 用于显示一般消息
score_font = pygame.font.SysFont("comicsansms", 35) # 用于显示分数

def your_score(score):
    """
    在屏幕左上角显示当前分数
    """
    value = score_font.render("得分: " + str(score), True, YELLOW)
    dis.blit(value, [0, 0])

def draw_snake(snake_block, snake_list):
    """
    绘制蛇的每一节身体
    """
    for x in snake_list:
        pygame.draw.rect(dis, GREEN, [x[0], x[1], snake_block, snake_block])

def show_message(msg, color):
    """
    在屏幕中央显示消息
    """
    mesg = font_style.render(msg, True, color)
    # 将文本矩形居中
    text_rect = mesg.get_rect(center=(DIS_WIDTH/2, DIS_HEIGHT/2))
    dis.blit(mesg, text_rect)

def gameLoop():
    """
    游戏主循环函数
    """
    game_over = False
    game_close = False

    # 蛇的初始位置（屏幕中心）
    x1 = DIS_WIDTH / 2
    y1 = DIS_HEIGHT / 2

    # 蛇的初始移动变化量
    x1_change = 0
    y1_change = 0

    # 蛇的身体列表
    snake_List = []
    Length_of_snake = 1

    # 随机生成第一个食物的位置
    # 这里的逻辑是将坐标对齐到网格上
    foodx = round(random.randrange(0, DIS_WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
    foody = round(random.randrange(0, DIS_HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0

    while not game_over:

        # --- 游戏结束等待界面 (按Q退出，按C重玩) ---
        while game_close == True:
            dis.fill(BLACK)
            show_message("游戏结束! 按 C-重新开始 或 Q-退出", RED)
            your_score(Length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        # --- 键盘输入事件处理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    # 防止直接反向移动（例如向左走时不能直接按右）
                    if x1_change != SNAKE_BLOCK:
                        x1_change = -SNAKE_BLOCK
                        y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    if x1_change != -SNAKE_BLOCK:
                        x1_change = SNAKE_BLOCK
                        y1_change = 0
                elif event.key == pygame.K_UP:
                    if y1_change != SNAKE_BLOCK:
                        y1_change = -SNAKE_BLOCK
                        x1_change = 0
                elif event.key == pygame.K_DOWN:
                    if y1_change != -SNAKE_BLOCK:
                        y1_change = SNAKE_BLOCK
                        x1_change = 0

        # --- 碰撞检测：撞墙 ---
        if x1 >= DIS_WIDTH or x1 < 0 or y1 >= DIS_HEIGHT or y1 < 0:
            game_close = True

        # 更新蛇头坐标
        x1 += x1_change
        y1 += y1_change

        # 绘制背景
        dis.fill(BLACK)

        # 绘制食物
        pygame.draw.rect(dis, RED, [foodx, foody, SNAKE_BLOCK, SNAKE_BLOCK])

        # 更新蛇身逻辑
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)

        # 如果蛇身长度超过当前分数允许的长度，删除蛇尾
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        # --- 碰撞检测：撞到自己 ---
        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        # 绘制蛇
        draw_snake(SNAKE_BLOCK, snake_List)

        # 显示分数
        your_score(Length_of_snake - 1)

        # 刷新屏幕
        pygame.display.update()

        # --- 吃到食物逻辑 ---
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, DIS_WIDTH - SNAKE_BLOCK) / 10.0) * 10.0
            foody = round(random.randrange(0, DIS_HEIGHT - SNAKE_BLOCK) / 10.0) * 10.0
            Length_of_snake += 1

        # 控制游戏速度
        clock.tick(SNAKE_SPEED)

    # 退出 Pygame
    pygame.quit()
    quit()

# 启动游戏
gameLoop()