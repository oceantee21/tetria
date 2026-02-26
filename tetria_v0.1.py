# tetris.py
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from random import choice

Window.clearcolor = (0.07, 0.07, 0.12, 1)

NES_COLORS = {
    'I': (0.0, 0.8, 0.8),
    'J': (0.0, 0.0, 0.8),
    'L': (0.9, 0.5, 0.0),
    'O': (0.9, 0.9, 0.0),
    'S': (0.0, 0.8, 0.0),
    'T': (0.7, 0.0, 0.7),
    'Z': (0.8, 0.0, 0.0),
    'G': (0.15, 0.15, 0.2)
}

TETROMINOES = {
    'I': [[1,1,1,1]],
    'J': [[1,0,0],[1,1,1]],
    'L': [[0,0,1],[1,1,1]],
    'O': [[1,1],[1,1]],
    'S': [[0,1,1],[1,1,0]],
    'T': [[0,1,0],[1,1,1]],
    'Z': [[1,1,0],[0,1,1]],
}

FIELD_W = 10
FIELD_H = 20
CELL = 18

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

class Board:
    def __init__(self, w=FIELD_W, h=FIELD_H):
        self.w, self.h = w, h
        self.grid = [[None for _ in range(w)] for __ in range(h)]

    def collision(self, shape, ox, oy):
        for y, row in enumerate(shape):
            for x, v in enumerate(row):
                if v:
                    gx, gy = ox + x, oy + y
                    if gy >= self.h or gx < 0 or gx >= self.w or (gy >= 0 and self.grid[gy][gx] is not None):
                        return True
        return False

    def place(self, shape, ox, oy, color):
        for y, row in enumerate(shape):
            for x, v in enumerate(row):
                if v:
                    gx, gy = ox + x, oy + y
                    if 0 <= gy < self.h and 0 <= gx < self.w:
                        self.grid[gy][gx] = color

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell is None for cell in row)]
        lines = self.h - len(new_grid)
        for _ in range(lines):
            new_grid.insert(0, [None for _ in range(self.w)])
        self.grid = new_grid
        return lines

class Piece:
    def __init__(self, kind=None):
        self.kind = kind or choice(list(TETROMINOES.keys()))
        self.shape = [row[:] for row in TETROMINOES[self.kind]]
        self.x = FIELD_W // 2 - len(self.shape[0]) // 2
        self.y = -len(self.shape)
        self.color = NES_COLORS[self.kind]

    def rotate(self):
        self.shape = rotate(self.shape)

class TetrisWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cell = CELL
        self.board = Board()
        self.piece = Piece()
        self.next_piece = Piece()
        self.drop_interval = 0.5
        self.acc = 0.0
        self.paused = False
        self.score = 0
        self.game_over = False
        Clock.schedule_interval(self._tick, 1/60)
        if not hasattr(Window, '_tetris_bound'):
            Window._tetris_bound = True
            Window.bind(on_key_down=self._on_key_down_safe)
        self._touch_start = None
        Clock.schedule_once(lambda dt: self.spawn(), 0)

    def spawn(self):
        self.piece = self.next_piece
        self.next_piece = Piece()
        self.piece.x = FIELD_W // 2 - len(self.piece.shape[0]) // 2
        self.piece.y = -len(self.piece.shape)
        if self.board.collision(self.piece.shape, self.piece.x, self.piece.y):
            self.game_over = True

    def _tick(self, dt):
        if self.game_over or self.paused:
            self._update_canvas()
            return
        self.acc += dt
        if self.acc >= self.drop_interval:
            self.acc = 0.0
            self._drop()
        self._update_canvas()

    def _drop(self):
        if not self.board.collision(self.piece.shape, self.piece.x, self.piece.y + 1):
            self.piece.y += 1
        else:
            self.board.place(self.piece.shape, self.piece.x, self.piece.y, self.piece.color)
            lines = self.board.clear_lines()
            self.score += [0,40,100,300,1200][min(lines,4)]
            self.spawn()

    def move(self, dx):
        if not self.board.collision(self.piece.shape, self.piece.x + dx, self.piece.y):
            self.piece.x += dx

    def rotate_piece(self):
        old = self.piece.shape
        self.piece.rotate()
        for ox in (0, -1, 1, -2, 2):
            if not self.board.collision(self.piece.shape, self.piece.x + ox, self.piece.y):
                self.piece.x += ox
                return
        self.piece.shape = old

    def hard_drop(self):
        while not self.board.collision(self.piece.shape, self.piece.x, self.piece.y + 1):
            self.piece.y += 1
        self._drop()

    def toggle_pause(self):
        self.paused = not self.paused

    def _on_key_down_safe(self, window, key, scancode, codepoint, modifiers):
        try:
            keycode = key if isinstance(key, int) else (key[0] if isinstance(key, (list, tuple)) else key)
        except Exception:
            keycode = key
        if keycode in (276, 'left'):
            self.move(-1)
        elif keycode in (275, 'right'):
            self.move(1)
        elif keycode in (273, 'up'):
            self.rotate_piece()
        elif keycode in (274, 'down'):
            self._drop()
        elif keycode == 32 or keycode == 'spacebar':
            self.hard_drop()
        elif keycode == 112 or keycode == 'p':
            self.toggle_pause()

    def on_touch_down(self, touch):
        self._touch_start = (touch.x, touch.y)
        return True

    def on_touch_up(self, touch):
        if not self._touch_start:
            return True
        sx, sy = self._touch_start
        dx = touch.x - sx
        dy = touch.y - sy
        ax, ay = abs(dx), abs(dy)
        self._touch_start = None
        if ax > 40 and ax > ay:
            self.move(1 if dx > 0 else -1)
        elif ay > 40 and ay > ax:
            if dy < 0:
                self._drop()
            else:
                self.hard_drop()
        else:
            self.rotate_piece()
        return True

    def _draw_cell(self, gx, gy, color, canvas, vx, vy):
        px = vx + gx * self.cell
        py = vy + (FIELD_H - 1 - gy) * self.cell
        with canvas:
            c = color
            Color(max(0, c[0]-0.12), max(0, c[1]-0.12), max(0, c[2]-0.12))
            Rectangle(pos=(px, py), size=(self.cell, self.cell))
            inner = 0.14 * self.cell
            Color(c[0], c[1], c[2])
            Rectangle(pos=(px+inner, py+inner), size=(self.cell-2*inner, self.cell-2*inner))

    def _update_canvas(self, *a):
        self.canvas.clear()
        total_w = self.cell * FIELD_W
        total_h = self.cell * FIELD_H
        vx = (self.width - total_w) / 2
        vy = (self.height - total_h) / 2
        for gy in range(FIELD_H):
            for gx in range(FIELD_W):
                self._draw_cell(gx, gy, NES_COLORS['G'], self.canvas, vx, vy)
        for y, row in enumerate(self.board.grid):
            for x, c in enumerate(row):
                if c:
                    self._draw_cell(x, y, c, self.canvas, vx, vy)
        for y, row in enumerate(self.piece.shape):
            for x, v in enumerate(row):
                if v:
                    self._draw_cell(self.piece.x + x, self.piece.y + y, self.piece.color, self.canvas, vx, vy)

class TetrisApp(App):
    def build(self):
        root = FloatLayout()
        root.add_widget(TetrisWidget(size_hint=(1,1)))
        return root

if __name__ == '__main__':
    TetrisApp().run()