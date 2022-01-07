#!/usr/bin/env python3
import curses
from curses import wrapper
import time
import copy
from datetime import datetime


class Tetris:
    def __init__(self):
        self.SIZE = (20, 20)  # width, height
        self.board = self.init_board()

        # Setup screen and game window
        self.scr = curses.initscr()
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

        self.display()

        time.sleep(1)

        player = self.Player(self.Player.TYPES['l'], self.SIZE)
       
        move_every = 10
        i = 0
        last = datetime.now()
        
        while not player.is_on_ground():
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
            print(action)
            player.action(action)
            self.display()
            i += 1
            if i >= move_every:
                player.move()
                i = 0

        # End screen
        self.win.getch()
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
            "box": ["BOX", "xx xx"],
            "l": ["L", "x. x. xx"],
            "rl": ["RL", ".x .x xx"],
        }
        def __init__(self, block_type: list, map_size: list):
            self.name = block_type[0]
            self.shape = block_type[1]
            self.size = map_size
            self.x = 10 - (len(self.shape.split()) // 2)
            self.y = 0

        def move(self):
            self.y += 1

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

        def is_on_ground(self):
            max_y = self.y + len(self.shape.split())
            if max_y > self.size[1]:
                return True
            else:
                return False

        def horizontal_move(self, delta: int):
            if self.x + delta in range(0, self.size[0]-1):
                self.x += delta
            print(self.x)

        def action(self, action):
            if action is None:
                return

            if str(action) == "KEY_RIGHT":
                self.horizontal_move(1)
            elif str(action) == "KEY_LEFT":
                self.horizontal_move(-1)


if __name__ == "__main__":
    try:
        tetris = Tetris()
    except Exception as e:
        print(str(e))
        curses.echo()
        input()
        curses.endwin()
