import pygame
import random
import sys
import os

# 初始化pygame
pygame.init()

# 设置中文字体支持
pygame.font.init()
font_path = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
if os.path.exists(font_path):
    font = pygame.font.Font(font_path, 40)
    small_font = pygame.font.Font(font_path, 20)
else:
    font = pygame.font.SysFont(['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC'], 40)
    small_font = pygame.font.SysFont(['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC'], 20)

# 游戏常量
SIZE = 400
GRID_SIZE = SIZE // 4
GRID_PADDING = 10
BACKGROUND_COLOR = (187, 173, 160)
EMPTY_CELL_COLOR = (205, 193, 180)
FONT_COLOR = (119, 110, 101)
SCORE_COLOR = (255, 255, 255)

# 方块颜色映射
CELL_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

# 数字颜色映射（浅色数字用深色字体，反之亦然）
NUMBER_COLORS = {
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242),
}


class Game2048:
    def __init__(self):
        self.screen = pygame.display.set_mode((SIZE, SIZE + 100))  # 额外空间显示分数
        pygame.display.set_caption("2048游戏")
        self.reset_game()

    def reset_game(self):
        """重置游戏状态"""
        self.board = [[0 for _ in range(4)] for _ in range(4)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()
        self.game_over = False
        self.win = False

    def add_new_tile(self):
        """在空白位置随机添加一个2或4"""
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def draw_board(self):
        """绘制游戏面板"""
        self.screen.fill(BACKGROUND_COLOR)

        # 绘制分数
        score_text = small_font.render(f"分数: {self.score}", True, SCORE_COLOR)
        self.screen.blit(score_text, (20, SIZE + 20))

        # 绘制游戏说明
        help_text = small_font.render("使用方向键移动，R键重新开始", True, SCORE_COLOR)
        self.screen.blit(help_text, (20, SIZE + 50))

        # 绘制格子
        for i in range(4):
            for j in range(4):
                value = self.board[i][j]
                color = CELL_COLORS.get(value, EMPTY_CELL_COLOR)
                number_color = NUMBER_COLORS.get(value, FONT_COLOR)

                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        j * GRID_SIZE + GRID_PADDING,
                        i * GRID_SIZE + GRID_PADDING,
                        GRID_SIZE - 2 * GRID_PADDING,
                        GRID_SIZE - 2 * GRID_PADDING
                    ),
                    border_radius=5
                )

                if value != 0:
                    # 根据数字大小调整字体大小
                    font_size = 40 if value < 1000 else 30 if value < 10000 else 20
                    num_font = pygame.font.SysFont(['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC'], font_size)
                    text = num_font.render(str(value), True, number_color)
                    text_rect = text.get_rect(
                        center=(
                            j * GRID_SIZE + GRID_SIZE // 2,
                            i * GRID_SIZE + GRID_SIZE // 2
                        )
                    )
                    self.screen.blit(text, text_rect)

        # 如果游戏结束，显示游戏结束信息
        if self.game_over:
            overlay = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))

            result_text = "游戏胜利!" if self.win else "游戏结束!"
            text = font.render(result_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SIZE // 2, SIZE // 2 - 30))
            self.screen.blit(text, text_rect)

            restart_text = small_font.render("按R键重新开始", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(SIZE // 2, SIZE // 2 + 30))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.update()

    def move(self, direction):
        """根据方向移动方块"""
        if self.game_over:
            return False

        moved = False

        # 根据方向调整处理顺序
        if direction in ('left', 'right'):
            for i in range(4):
                row = self.board[i][:]
                new_row, row_score = self.merge_row(row, direction)
                if new_row != row:
                    moved = True
                    self.board[i] = new_row
                    self.score += row_score
        else:  # up or down
            for j in range(4):
                column = [self.board[i][j] for i in range(4)]
                new_col, col_score = self.merge_row(column, direction)
                if new_col != column:
                    moved = True
                    for i in range(4):
                        self.board[i][j] = new_col[i]
                    self.score += col_score

        # 如果有移动，则添加新方块并检查游戏状态
        if moved:
            self.add_new_tile()
            self.check_game_state()

        return moved

    def merge_row(self, row, direction):
        """合并行或列中的方块"""
        # 移除0值
        filtered = [num for num in row if num != 0]

        # 根据方向反转列表以便统一处理
        if direction in ('right', 'down'):
            filtered = filtered[::-1]

        merged = []
        score = 0
        i = 0

        # 合并相同的数字
        while i < len(filtered):
            if i + 1 < len(filtered) and filtered[i] == filtered[i + 1]:
                merged.append(filtered[i] * 2)
                score += filtered[i] * 2
                i += 2
            else:
                merged.append(filtered[i])
                i += 1

        # 填充0到长度4
        merged += [0] * (4 - len(merged))

        # 恢复原方向
        if direction in ('right', 'down'):
            merged = merged[::-1]

        return merged, score

    def check_game_state(self):
        """检查游戏是否结束或胜利"""
        # 检查是否达到2048（胜利）
        for row in self.board:
            if 2048 in row:
                self.win = True
                self.game_over = True
                return

        # 检查是否还有空位置
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return

        # 检查是否还有可能合并的方块
        for i in range(4):
            for j in range(4):
                current = self.board[i][j]
                # 检查右侧和下侧是否有相同方块
                if j < 3 and self.board[i][j + 1] == current:
                    return
                if i < 3 and self.board[i + 1][j] == current:
                    return

        # 如果以上都不满足，游戏结束
        self.game_over = True

    def check_game_state(self):
        """检查游戏是否结束或胜利"""
        # 检查是否达到2048（胜利）
        for row in self.board:
            if 2048 in row:
                self.win = True
                self.game_over = True
                return

        # 检查是否还有空位置
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == 0:
                    return

        # 检查是否还有可能合并的方块
        for i in range(4):
            for j in range(4):
                current = self.board[i][j]
                # 检查右侧和下侧是否有相同方块
                if j < 3 and self.board[i][j + 1] == current:
                    return
                if i < 3 and self.board[i + 1][j] == current:
                    return

        # 如果以上都不满足，游戏结束
        self.game_over = True

    def run(self):
        """运行游戏主循环"""
        clock = pygame.time.Clock()

        while True:
            self.draw_board()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # 重置游戏
                        self.reset_game()
                    elif event.key == pygame.K_UP:
                        self.move('up')
                    elif event.key == pygame.K_DOWN:
                        self.move('down')
                    elif event.key == pygame.K_LEFT:
                        self.move('left')
                    elif event.key == pygame.K_RIGHT:
                        self.move('right')
                    elif event.key == pygame.K_ESCAPE:  # 退出游戏
                        pygame.quit()
                        sys.exit()

            clock.tick(60)


# 启动游戏
if __name__ == "__main__":
    game = Game2048()
    game.run()
