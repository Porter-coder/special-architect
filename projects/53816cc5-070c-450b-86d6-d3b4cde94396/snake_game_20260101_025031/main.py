class Snake:
    def __init__(self):
        self.direction = pygame.K_RIGHT
        self.body = [ [100, 50], [90, 50], [80, 50], [70, 50] ]
        self.score = 0
        self.grow_pending = False

    def change_direction(self, key):
        if key == pygame.K_LEFT and self.direction != pygame.K_RIGHT:
            self.direction =

以下是完整的贪吃蛇游戏Python代码，使用Pygame实现所有功能：