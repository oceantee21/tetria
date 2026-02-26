from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import random

Window.clearcolor = (0.07, 0.07, 0.12, 1)

# Константы
FIELD_W, FIELD_H = 10, 20
CELL_SIZE = 30

# Цвета для фигур
COLORS = {
    'I': (0, 1, 1),
    'J': (0, 0, 1),
    'L': (1, 0.5, 0),
    'O': (1, 1, 0),
    'S': (0, 1, 0),
    'T': (0.5, 0, 0.5),
    'Z': (1, 0, 0),
}

# фигуры
TETROMINOES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]],
}

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(FIELD_W)] for _ in range(FIELD_H)]

    def collision(self, shape, ox, oy):
        for y, row in enumerate(shape):
            for x, v in enumerate(row):
                if v:
                    gx = ox + x
                    gy = oy + y
                    if gx < 0 or gx >= FIELD_W or gy >= FIELD_H:
                        return True
                    if gy >=0 and self.grid[gy][gx] is not None:
                        return True
        return False

    def place(self, shape, ox, oy, color):
        for y, row in enumerate(shape):
            for x, v in enumerate(row):
                if v:
                    gx = ox + x
                    gy = oy + y
                    if 0<=gy<FIELD_H and 0<=gx<FIELD_W:
                        self.grid[gy][gx] = color

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        lines_cleared = FIELD_H - len(new_grid)
        for _ in range(lines_cleared):
            new_grid.insert(0, [None]*FIELD_W)
        self.grid = new_grid
        return lines_cleared

class Piece:
    def __init__(self, kind=None):
        self.kind = kind or random.choice(list(TETROMINOES.keys()))
        self.shape = [row[:] for row in TETROMINOES[self.kind]]
        self.x = FIELD_W // 2 - len(self.shape[0]) // 2
        self.y = 0  # Начинается сверху

    def rotate(self):
        self.shape = rotate(self.shape)

class TetrisWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board = Board()
        self.current_piece = None
        self.game_clock = None
        self.paused = False
        self.game_over = False
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def start_game(self):
        self.board = Board()
        self.spawn_piece()
        self.game_over = False
        self.paused = False
        if self.game_clock:
            self.game_clock.cancel()
        self.game_clock = Clock.schedule_interval(self.tick, 0.5)

    def spawn_piece(self):
        self.current_piece = Piece()
        # Запускаем в верхней части поля
        self.current_piece.x = FIELD_W // 2 - len(self.current_piece.shape[0]) // 2
        self.current_piece.y = 0  # Начинается сверху
        if self.board.collision(self.current_piece.shape, self.current_piece.x, self.current_piece.y):
            self.end_game()

    def end_game(self):
        if self.game_clock:
            self.game_clock.cancel()
        self.game_over = True
        print("Игра окончена! Попробуйте снова.")  # Сообщение

    def tick(self, dt):
        if self.game_over or self.paused:
            return
        if self.current_piece:
            moved = self.move(self.current_piece, 0, 1)
            if not moved:
                self.lock_and_spawn()

    def lock_and_spawn(self):
        if self.current_piece:
            self.board.place(self.current_piece.shape, self.current_piece.x, self.current_piece.y, self.get_color())
        self.board.clear_lines()
        self.spawn_piece()

    def move(self, piece, dx, dy):
        if not piece:
            return False
        old_x, old_y = piece.x, piece.y
        new_x = old_x + dx
        new_y = old_y + dy
        if not self.board.collision(piece.shape, new_x, new_y):
            piece.x = new_x
            piece.y = new_y
            self.update_canvas()
            return True
        return False

    def rotate_piece(self):
        if not self.current_piece:
            return
        old_shape = [row[:] for row in self.current_piece.shape]
        self.current_piece.rotate()
        if self.board.collision(self.current_piece.shape, self.current_piece.x, self.current_piece.y):
            self.current_piece.shape = old_shape
        else:
            self.update_canvas()

    def get_color(self):
        return COLORS[self.current_piece.kind]

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Рисуем поле
            for y in range(FIELD_H):
                for x in range(FIELD_W):
                    cell_color = self.board.grid[y][x]
                    color = cell_color if cell_color else (0.2, 0.2, 0.2)
                    Color(*color)
                    Rectangle(pos=(x * CELL_SIZE, y * CELL_SIZE),
                              size=(CELL_SIZE, CELL_SIZE))
            # Рисуем текущую фигуру
            if self.current_piece:
                for y, row in enumerate(self.current_piece.shape):
                    for x, v in enumerate(row):
                        if v:
                            gx = self.current_piece.x + x
                            gy = self.current_piece.y + y
                            if gy >= 0:
                                Color(*self.get_color())
                                Rectangle(pos=(gx * CELL_SIZE, gy * CELL_SIZE),
                                          size=(CELL_SIZE, CELL_SIZE))

    def on_touch_down(self, touch):
        if self.game_over:
            return
        if not self.current_piece:
            return
        if touch.x < self.center_x:
            self.move(self.current_piece, -1, 0)
        else:
            self.move(self.current_piece, 1, 0)

    def on_key_down(self, key):
        if self.game_over:
            return
        if not self.current_piece:
            return
        if key == 'left':
            self.move(self.current_piece, -1, 0)
        elif key == 'right':
            self.move(self.current_piece, 1, 0)
        elif key == 'up':
            self.rotate_piece()
        elif key == 'space':
            # быстрая опускка
            while self.move(self.current_piece, 0, 1):
                pass
            self.lock_and_spawn()

class TetrisApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')
        self.game = TetrisWidget(size_hint=(1, 0.9))
        btn_start = Button(text='Начать игру', size_hint=(1, 0.1))
        btn_start.bind(on_release=lambda *args: self.start_game())

        root.add_widget(self.game)
        root.add_widget(btn_start)

        # Можно подключить обработку клавиш
        from kivy.core.window import Window
        Window.bind(on_key_down=self._on_key_down)

        return root

    def start_game(self):
        self.game.start_game()

    def _on_key_down(self, window, keycode, *args):
        key = keycode[1]
        self.game.on_key_down(key)

if __name__ == '__main__':
    TetrisApp().run()