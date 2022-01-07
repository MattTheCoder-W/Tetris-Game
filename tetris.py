#!/usr/bin/env python3
import curses
from curses import wrapper
import time
import copy
from datetime import datetime
import sys
import random


class Tetris:
    def __init__(self):
        self.SIZE = (10, 20)  # width, height
        self.board = self.init_board()
        self.score = 0
        self.next = "o"

        # Setup screen and game window
        self.scr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        self.TERM_SIZE = [0, 0]
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        self.scr.keypad(True)
        self.win = curses.newwin(self.SIZE[1]+2, self.SIZE[0]*2+2, 0, 0)
        self.win.keypad(True)
        self.win.nodelay(True)
        self.win.clear()
        self.win.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.win.refresh()

        self.score_win = curses.newwin(3, 20, 1, self.SIZE[0]*2+3)
        self.update_score(0)

        self.next_win = curses.newwin(7, 14, 5, self.SIZE[0]*2+6)
        self.update_next()

        self.update_size()
        while not self.check_end():
            self.display()

            player = self.Player(self.Player.TYPES[self.next], self.SIZE)
            self.update_next()
           
            move_every = 3
            i = 0
            last = datetime.now()
            
            while not player.is_on_ground(self.board):
                if curses.is_term_resized(self.TERM_SIZE[0], self.TERM_SIZE[1]):
                    self.update_size()
                self.display(player.put_player(self.board))
                tdelta = (datetime.now() - last).total_seconds()
                tdelta = tdelta if tdelta < 0.1 else 0
                last = datetime.now()
                time.sleep(0.1 - tdelta)
                action = None
                try:
                    action = self.win.getkey()
                except:
                    pass
                curses.flushinp()
                player.action(action, self.board)
                i += 1
                if i >= move_every or action == "KEY_DOWN":
                    player.move()
                    i = 0
        
            self.board = player.put_player(self.board)

        # End screen
        curses.flushinp()
        self.score_win.getch()
        curses.echo()
        curses.endwin()

    def update_size(self):
        while True:
            self.TERM_SIZE = list(self.scr.getmaxyx())  # Height, width
            curses.resizeterm(self.TERM_SIZE[0], self.TERM_SIZE[1])
            try:
                if self.TERM_SIZE[1] < (self.SIZE[0]*2+2)+20+2 or self.TERM_SIZE[0] < self.SIZE[1]+2:
                        self.win.addstr(0, 0, "Terminal too small!")
                        curses.flushinp()
                        self.win.getch()
                else:
                    self.win.clear()
                    self.win.border(0, 0, 0, 0, 0, 0, 0, 0)
                    self.score_win.border(0, 0, 0, 0, 0, 0, 0, 0)
                    self.win.refresh()
                    self.score_win.refresh()
                    break
            except:
                break

    def update_score(self, delta: int):
        self.score_win.clear()
        self.score_win.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.score_win.addstr(1, 2, f"Score: {self.score + delta}", curses.A_BOLD)
        self.score_win.refresh()

    def update_next(self):
        self.next_win.clear()
        self.next_win.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.next = random.choice(list(self.Player.TYPES.keys()))
        self.next_win.addstr(1, 3, f"Next: {self.next}", curses.A_BOLD)
        shape = self.Player.TYPES[self.next][1]
        color = self.Player.TYPES[self.next][2]
        for y, row in enumerate(shape.split()):
            for x, block in enumerate(row):
                char = self.Block.CHARS['block'] if block == "x" else " "
                self.next_win.addstr(y+3, x*2+3, char*2, curses.color_pair(color))
        self.next_win.refresh()

    def init_board(self):
        board = []
        for y in range(self.SIZE[1]):
            row = []
            for x in range(self.SIZE[0]):
                row.append(self.Block(False))
            board.append(row)
        return board

    def check_end(self):
        for block in self.board[0]:
            if block.active:
                return True
        return False

    def display(self, custom_board=None):
        board = self.board if custom_board is None else custom_board
        for y, row in enumerate(board):
            for x, block in enumerate(row):
                char = block.getch()
                if block.active:
                    char = char*2
                else:
                    char = " " + char
                self.win.addstr(y+1, x*2+1, char, curses.color_pair(block.getcol()))
        self.win.refresh()


    class Block:
        CHARS={"block": "█", "dot": "·"}
        def __init__(self, active: bool, color=0):
            self.active = active
            self.color = color

        def set_state(self, state: bool):
            self.active = state

        def set_color(self, color: int):
            self.color = color

        def getch(self):
            if self.active:
                return self.CHARS['block']
            else:
                return self.CHARS['dot']

        def getcol(self):
            return self.color

    class Player:
        TYPES = {
            "o": ["o", "xx xx", 227],
            "l": ["l", "..x xxx", 4],
            "j": ["j", "x.. xxx", 20],
            "i": ["i", "xxxx", 7],
            "s": ["s", ".xx xx.", 3],
            "t": ["t", ".x. xxx", 6],
            "z": ["z", "xx. .xx", 2],
        }
        def __init__(self, block_type: list, map_size: list):
            self.name = block_type[0]
            self.shape = block_type[1]
            self.color = block_type[2]
            self.size = map_size
            self.x = self.size[0]//2 - (len(self.shape.split()) // 2)
            self.y = 0
            self.on_ground = False

        def move(self, delta=1):
            self.y += delta

        def get_poses(self, custom_shape=None):
            shape = custom_shape if custom_shape is not None else self.shape
            poses = []
            for y, line in enumerate(shape.split()):
                for x, char in enumerate(line):
                    if char == "x":
                        poses.append((x+self.x, y+self.y))
            return poses

        def put_player(self, in_board: list):
            board = copy.deepcopy(in_board)
            for pos in self.get_poses():
                board[pos[1]][pos[0]].set_state(True)
                board[pos[1]][pos[0]].set_color(self.color)
            return board

        def is_on_ground(self, board: list):
            under_poses = [[x[0], x[1]+1] for x in self.get_poses()]
            max_y = self.y + len(self.shape.split()) + 1
            if max_y > self.size[1]:
                self.on_ground = True
                return self.on_ground
            else:
                self.on_ground = False

            for pos in under_poses:
                if board[pos[1]][pos[0]].active:
                    self.on_ground = True
                    return self.on_ground


        def horizontal_move(self, delta: int, board: list):
            poses = self.get_poses()
            for pos in poses:
                pos = [pos[0]+delta, pos[1]]
                if pos[0] not in range(0, self.size[0]) or board[pos[1]][pos[0]].active:
                    return
            self.x += delta

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
                    return
            self.shape = new_shape

        def quick_down(self, board: list):
            while not self.is_on_ground(board):
                self.move()
            self.move(delta=-1)

        def action(self, action: str, board: list):
            if action is None:
                return

            if str(action) == "KEY_RIGHT":
                self.horizontal_move(1, board)
            elif str(action) == "KEY_LEFT":
                self.horizontal_move(-1, board)
            elif str(action) == "KEY_UP":
                self.rotate(board)
            elif str(action) == " ":
                self.quick_down(board)

    @staticmethod
    def make_color(color: list, char: str):
        # color -> (R, G, B)
        # Convert character to colored character
        R, G, B = color
        string = f"\x1b[38;2;{R};{G};{B}m{char}\x1b[0m"
        return string


if __name__ == "__main__":
    try:
        tetris = Tetris()
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        print(str(e), lineno, f)
        input()
        curses.echo()
        curses.endwin()
