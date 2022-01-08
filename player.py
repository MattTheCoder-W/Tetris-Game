#!/bin/usr/env python3
from copy import deepcopy
from sys import platform
if platform == "linux" or platform == "linux2":
    linux = True
else:
    linux = False

"""
Klasa Player - odpowiada za bloczek gracza, czyli spadający klocek, którym gracz może poruszać, obracać go oraz kontrolować prędkość updaku

Atrybuty:
    block_type - (list) Typ bloku, wyciągnięty z słownika TYPES
        składnia: [kształt, kolor]
            kształt ma postać tekstu, w którym wiersze kształtu są oddzielone spacjami, x odpowiada za element kształtu, a . za puste miejsce.
            Np. dla kształtu z -> xx. .xx, czyli
                xx.
                .xx
    map_size - (list) Wielkość mapy tetris
        składnia: [szerokość, wysokość]

Autor: MattTheCoder-W
"""

class Player:
    # Typy bloków
    TYPES = {
        "o": ["xx xx", 227],
        "l": ["..x xxx", 4],
        "j": ["x.. xxx", 20],
        "i": ["xxxx", 7],
        "s": [".xx xx.", 3],
        "t": [".x. xxx", 6],
        "z": ["xx. .xx", 2],
    }
    def __init__(self, block_type: list, map_size: list):
        self.shape = block_type[0]
        self.color = block_type[1]
        self.size = map_size
        self.x = self.size[0]//2 - (len(self.shape.split()) // 2)
        self.y = 0
        self.on_ground = False

    # Funkcja przemieszczająca gracza o wartość delta (def. 1)
    def move(self, delta=1):
        self.y += delta

    # Funkcja zwracająca wszystkie pozycje bloków z jakich składa się gracz
    def get_poses(self, custom_shape=None, custom_pos=None):
        px, py = [self.x, self.y] if custom_pos is None else custom_pos
        shape = custom_shape if custom_shape is not None else self.shape
        poses = []
        for y, line in enumerate(shape.split()):
            for x, char in enumerate(line):
                if char == "x":
                    poses.append((x+px, y+py))
        return poses

    # Funkcja zwracająca podgląd gracza na samym dole planszy
    def get_preview(self, board: list):
        py = self.y
        while not self.is_on_ground(board, custom_pos=[self.x, py]):
            py += 1
        end_poses = self.get_poses(custom_pos=[self.x, py])
        for pos in end_poses:
            board[pos[1]][pos[0]].set_state(True)
            board[pos[1]][pos[0]].set_color(self.color)
            board[pos[1]][pos[0]].set_prev(True)

    # Funkcja zwracająca planszę z wstawionym w nią graczem
    def put_player(self, in_board: list, no_prev=False):
        board = deepcopy(in_board)
        if not no_prev:
            self.get_preview(board)
        for pos in self.get_poses():
            board[pos[1]][pos[0]].set_state(True)
            board[pos[1]][pos[0]].set_color(self.color)
            board[pos[1]][pos[0]].set_prev(False)
        return board

    # Funkcja sprawdzająca czy gracz jest na ziemi/innym bloku
    def is_on_ground(self, board: list, custom_pos=None, inside=False):
        under_poses = [[x[0], x[1]+1] for x in self.get_poses(custom_pos=custom_pos)] if not inside else self.get_poses(custom_pos=custom_pos)
        y = self.y if custom_pos is None else custom_pos[1]
        max_y = y + len(self.shape.split()) + 1
        max_h = self.size[1] if not inside else self.size[1] + 1
        if max_y > max_h:
            if custom_pos is None:
                self.on_ground = True
            return True
        else:
            if custom_pos is None:
                self.on_ground = False

        for pos in under_poses:
            if board[pos[1]][pos[0]].active and not board[pos[1]][pos[0]].is_prev:
                if custom_pos is None:
                    self.on_ground = True
                return True
        return False

    # Funkcja przemieszczająca gracza w osi poziomej (wraz ze sprawdzeniem czy jest to możliwe)
    def horizontal_move(self, delta: int, board: list):
        poses = self.get_poses()
        for pos in poses:
            pos = [pos[0]+delta, pos[1]]
            if pos[0] not in range(0, self.size[0]) or board[pos[1]][pos[0]].active:
                return
        self.x += delta

    # Funkcja obracająca gracza (Wraz ze sprawdzeniem czy jest to możliwe)
    def rotate(self, board: list):
        new_shape = []
        for x in range(len(self.shape.split()[0]))[::-1]:
            row = ""
            for y in range(len(self.shape.split())):
                row += self.shape.split()[y][x]
            new_shape.append(row)
        new_shape = " ".join(new_shape)
        poses = self.get_poses(custom_shape=new_shape)
        for pos in poses:
            if pos[0] not in range(0, self.size[0]) or board[pos[1]][pos[0]].active:
                if pos[0] < self.x:
                    self.x+=1
                else:
                    self.x-=1
        self.shape = new_shape

    # Funkcja sprawdzająca czy pozycja gracza jest dozwolona
    def check_pos(self):
        max_y = self.y + len(self.shape.split())
        if max_y not in range(0, self.size[1]):
            return False
        return True

    # Funkcja szybkiego zrzucenia gracza
    def quick_down(self, board: list):
        while not self.is_on_ground(board, inside=True):
            self.move()

    # Funkcja zarządzająca wciśniętymi klawiszami
    def action(self, action: str, board: list):
        if action is None: # Jeżeli gracz nie wcisnął żadnego przycisku
            return None

        if str(action) == "KEY_RIGHT":
            self.horizontal_move(1, board)
        elif str(action) == "KEY_LEFT":
            self.horizontal_move(-1, board)
        elif str(action) == "KEY_UP":
            self.rotate(board)
        elif str(action) == " ":
            self.quick_down(board)
            return "SKIP"
        elif str(action) == "q":
            return "STOP" 
        elif str(action) == "r":
            return "RESTART"
        elif str(action) == "p":
            return "PAUSE"
        elif str(action) == "v":
            return "PREV" 

