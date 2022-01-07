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
        self.SIZE = (20, 20)  # width, height
        self.board = self.init_board()

        # Setup screen and game window
        self.scr = curses.initscr()
        self.TERM_SIZE = list(self.scr.getmaxyx())  # Height, width
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        self.scr.keypad(True)
        self.win = curses.newwin(self.SIZE[1]+2, self.SIZE[0]+2, 0, 0)
        self.win.keypad(True)
        self.win.nodelay(True)
        self.win.clear()
        self.win.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.win.refresh()

        self.score_win = curses.newwin(3, 20, 0, self.SIZE[0]+3)
        self.score_win.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.score_win.addstr(1, 1, "Score: 0", curses.A_BOLD)
        self.score_win.refresh()

        while not self.check_end():
            self.display()

            player = self.Player(self.Player.TYPES[random.choice(list(self.Player.TYPES.keys()))], self.SIZE)
           
            move_every = 3
            i = 0
            last = datetime.now()
            
            while not player.is_on_ground(self.board):
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
                player.action(action)
                self.display()
                i += 1
                if i >= move_every or action == "KEY_DOWN":
                    player.move()
                    i = 0
        
            self.board = player.put_player(self.board)

        # End screen
        curses.flushinp()
        self.win.getch()
        input()
        curses.echo()
        curses.endwin()

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
                self.win.addch(y+1, x+1, block.getch())
        self.win.refresh()


    class Block:
        CHARS={"block": "█", "dot": "·"}
        def __init__(self, active: bool, color=None):
            self.active = active
            self.color = color

        def set_state(self, state: bool):
            self.active = state

        def set_color(self, color: str):
            self.color = color

        def getch(self):
            if self.active:
                return self.CHARS['block']
            else:
                return self.CHARS['dot']

    class Player:
        TYPES = {
            "o": ["o", "xx xx"],
            "l": ["l", "..x xxx"],
            "j": ["j", "x.. xxx"],
            "i": ["i", "xxxx"],
            "s": ["s", ".xx xx."],
            "t": ["t", ".x. xxx"],
            "z": ["z", "xx. .xx"],
        }
        def __init__(self, block_type: list, map_size: list):
            self.name = block_type[0]
            self.shape = block_type[1]
            self.size = map_size
            self.x = 10 - (len(self.shape.split()) // 2)
            self.y = 0
            self.on_ground = False

        def move(self, delta=1):
            self.y += delta

        def get_poses(self):
            poses = []
            for y, line in enumerate(self.shape.split()):
                for x, char in enumerate(line):
                    if char == "x":
                        poses.append((x+self.x, y+self.y))
            return poses

        def put_player(self, in_board: list):
            board = copy.deepcopy(in_board)
            for pos in self.get_poses():
                board[pos[1]][pos[0]].set_state(True)
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


        def horizontal_move(self, delta: int):
            if self.x + delta in range(0, self.size[0]-1):
                self.x += delta

        def rotate(self):
            new_shape = []
            for x in range(len(self.shape.split()[0]))[::-1]:
                row = ""
                for y in range(len(self.shape.split())):
                    row += self.shape.split()[y][x]
                new_shape.append(row)
            self.shape = " ".join(new_shape)


        def action(self, action):
            if action is None:
                return

            if str(action) == "KEY_RIGHT":
                self.horizontal_move(1)
            elif str(action) == "KEY_LEFT":
                self.horizontal_move(-1)
            elif str(action) == "KEY_UP":
                self.rotate()


if __name__ == "__main__":
    try:
        tetris = Tetris()
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        print(str(e), lineno, f)
        curses.echo()
        input()
        curses.endwin()
