#!/usr/bin/env python3
import curses
from curses import wrapper

import time
from datetime import datetime

import random
import math

# Import modułów gry
from block import Block
from player import Player

from os import get_terminal_size

# Sprawdzanie platformy (niektore części skryptu sie różnią)
from sys import platform
if platform == "linux" or platform == "linux2":
    linux = True
else:
    linux = False


"""
Klasa Tetris - odpowiada za przebieg oraz wyświetlanie gry.

Argumenty:
    FPS - liczba klatek na sekundę (im więcej tym szybciej gra się toczy)
    SIZE - wielkość planszy tetris
    board - plansza gry
    score - aktualny wynik gracza
    next - nazwa następnego bloczku
    restart - flaga, która określa czy po zakończeniu działania obiektu ma być ponownie uruchomiona gra
    scr ... help_win - okna gry
    player - obiekt gracza
    level - aktualny poziom gry
    goalPoints - punkty zniszczenia warstw (na ich podstawie zwiększa się poziom gry)
    prev - flaga określająca czy ma być wyświetlany podgląd opadającego bloczku na samym dole
    speeds - prędkości w zależności od poziomu (1-15)
    i - licznik klatek
    move_every - co ile klatek blok gracza ma pójść w dół (ta wartość z mniejsza się wraz ze wzrostem poziomu)
"""
class Tetris:
    def __init__(self):
        self.FPS = 60
        self.TERM_SIZE = [0, 0]
        self.SIZE = (10, 20)  # szerokosc, wysokosc
        self.board = self.init_board()
        self.score = 0
        self.next = "o"
        self.restart = False
        self.scr, self.win, self.score_win, self.next_win, self.help_win, self.player = [None]*6
        self.level = 1
        self.goalPoints = 0
        self.prev = True
        
        self.speeds = [0.01667,0.021017, 0.026977, 0.035256, 0.04693, 0.06361, 0.0879, 0.1236, 0.1775, 0.2598, 0.388, 0.59, 0.92, 1.46, 2.36]

        self.setup_screen()
        self.update_size()
        self.move_every = int(round(1/self.speeds[self.level-1], 0))
        self.i = 0

        self.main()
    
    # Funkcja z główną pętlą gry
    def main(self):
        # Powtarzanie dopóki gra się nie skończy
        while not self.check_end():
            self.player = Player(Player.TYPES[self.next], self.SIZE)
            self.update_next() # Aktualizacja następnego bloczku (podgląd po prawej)
           
            # Powtarzanie dopóki gracz nie dotknął ziemi lub innych bloczkóœ
            while not self.player.is_on_ground(self.board, inside=True):
                output = self.player_action() # Sterowanie graczem
                if output == "STOP": # gracz wcisnął stop
                    return
                if output == "SKIP": # gracz wcisnął szybkie zrzucenie
                    break

            self.player.move(-1) # Cofamy gracza, gdyż aktualnie znajduje się w innym bloku/ścianie

            self.display() # Wyświetlamy planszę
            self.board = self.player.put_player(self.board, no_prev=True) # Wrzucamy gracza na planszę położonych bloków
            self.check_lines() # Sprawdzamy czy nie ułożono pełnych warstw do usunięcia (oraz naliczamy punkty)

        self.display() # Wyświetlamy planszę końcową

        self.win.addstr(1, 1, "GAME OVER!") # Informacja ,że gra dobiegła końca

        # Pętla po zakończeniu gry, która pozwala na oglądanie planszy oraz restart gry lub wyjście
        while True:
            try:
                inp = self.win.getkey()
                curses.flushinp()
                if str(inp) == "q":
                    curses.endwin()
                    return
                elif str(inp) == "r":
                    self.restart = True
                    curses.endwin()
                    return
            except:
                time.sleep(0.5)

        # Końcowe wyłączenie curses (bez tego terminal nie będzie dobrze działał po wyjściu z programu)
        curses.flushinp()
        self.score_win.getch()
        curses.echo()
        curses.endwin()

    # Funkcja odpowada za akcje gracza
    def player_action(self):
        # Sprawdzamy czy wielkość terminala została zmnieniona
        if curses.is_term_resized(self.TERM_SIZE[0], self.TERM_SIZE[1]):
            self.update_size() # Uaktualniamy wielkość terminala

        # Wyświetlamy planszę razem z graczem oraz podglądem jeżeli self.prev == True
        self.display(self.player.put_player(self.board, no_prev=not self.prev))

        time.sleep(1/self.FPS) # Utrzymujemy klatkarz (dla prostoty nie odejmujemy czasu, jaki został zajęty przez działanie algorytmu)

        # Wczytujemy klawisz gracza
        action = None
        try:
            action = self.win.getkey()
        except:
            pass

        curses.flushinp()
        response = self.player.action(action, self.board) # Przekazujemy klawisz do obiektu gracza, oraz otrzymujemy odpowiedź

        if response == "SKIP": # Gracz wcisnął szybkie zrzucenie bloku
            return "SKIP"

        if response == "PREV": # Gracz zmienił opcję podglądu bloku
            self.prev = not self.prev

        if response == "RESTART": # Gracz wcisnął restart
            self.restart = True

        if response in ["STOP", "RESTART"]: # Gracz chce zakończyć aktualną grę
            curses.endwin()
            return "STOP"

        if response == "PAUSE": # Gracz kliknął pauzę
            # Pętla oczekująca na wyłączenie pauzy
            while True:
                self.pause_screen()
                time.sleep(1/self.FPS)
                try:
                    inp = self.win.getkey()
                    if inp == "p":
                        break
                except:
                    pass
                curses.flushinp()

        self.i += 1

        # Sprawdzamy czy jest czas na przemieszczenie bloku gracza w dół
        if self.i >= self.move_every or action == "KEY_DOWN":
            self.player.move()
            self.i = 0

    # Wyczyszczenie danego okienka
    def clear_win(self, win):
        win.clear()
        win.border(0, 0, 0, 0, 0, 0, 0, 0)

    # Funkcja ustawiająca wszystkie okna gry
    def setup_screen(self):
        self.TERM_SIZE = list(get_terminal_size())
        if self.TERM_SIZE[0] < self.SIZE[0] or self.TERM_SIZE[1] < self.SIZE[1]:
            print("Terminal too small!")
            exit(1)
            
        # Główne okno
        self.scr = curses.initscr()

        # Włączenie kolorów
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            try:
                curses.init_pair(i + 1, i, -1)
            except:
                pass

        # Ustawienia okna globalnego
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        self.scr.keypad(True)

        # curses.newwin(wysokosc, szerokosc, y, x)
        # Ustawienia okna planszy tetris
        self.win = curses.newwin(self.SIZE[1]+2, self.SIZE[0]*2+2, 0, 0)
        self.win.keypad(True)
        self.win.nodelay(True)
        self.clear_win(self.win)
        self.win.refresh()

        # Ustawienia okna punktacji
        self.score_win = curses.newwin(4, 20, 0, self.SIZE[0]*2+3)
        self.update_score(0)

        # Ustawienia okna kolejnego bloku
        self.next_win = curses.newwin(7, 14, 4, self.SIZE[0]*2+6)
        self.update_next()

        # Ustawienia okna pomocy
        self.help_win = curses.newwin(11, 20, 7+3+1, self.SIZE[0]*2+3)
        self.help_win.border(0, 0, 0, 0, 0, 0, 0, 0)
        help_content = [
            "Help:",
            "q\t- quit",
            "r\t- restart",
            "p\t- pause",
            "←/→\t- move",
            "↑\t- rotate",
            "↓\t- faster",
            "space\t- drop",
            "v\t- preview"
        ]
        for i, content in enumerate(help_content):
            self.help_win.addstr(i+1, 1, content)
        self.help_win.refresh()
    
    # Funkcja ekranu pauzy na planszy tetris
    def pause_screen(self):
        for y in range(self.SIZE[1]):
            row = " "*self.SIZE[0]*2
            self.win.addstr(y+1, 1, row)
        self.win.addstr(self.SIZE[1]//2, self.SIZE[0]//2*2-2, "PAUSE")

    # Akutalizacja rozmiaru terminala (ewentualna informacja, że terminal jest za mały)
    def update_size(self):
        while True:
            self.TERM_SIZE = list(self.scr.getmaxyx())  # Height, width
            if linux:
                curses.resizeterm(self.TERM_SIZE[0], self.TERM_SIZE[1])
            try:
                if self.TERM_SIZE[1] < (self.SIZE[0]*2+2)+20+2 or self.TERM_SIZE[0] < self.SIZE[1]+2:
                        self.win.addstr(0, 0, "Terminal too small!")
                        curses.flushinp()
                        self.win.getch()
                else:
                    # Wyczyszczenie wszystkich okien
                    self.clear_win(self.win)
                    self.score_win.border(0, 0, 0, 0, 0, 0, 0, 0)
                    self.next_win.border(0, 0, 0, 0, 0, 0, 0, 0)
                    self.help_win.border(0, 0, 0, 0, 0, 0, 0, 0)
                    self.win.refresh()
                    self.score_win.refresh()
                    self.next_win.refresh()
                    self.help_win.refresh()
                    break
            except:
                break

    # Funkcja aktualizująca punkację oraz wyświetlająca poziom
    def update_score(self, delta: int):
        self.clear_win(self.score_win)
        self.score += delta
        self.score_win.addstr(1, 2, f"Score: {self.score}", curses.A_BOLD)
        self.score_win.addstr(2, 2, f"Level: {self.level} / {self.goalPoints}", curses.A_BOLD)
        self.score_win.refresh()

    # Funkcja aktualizująca poziom
    def update_level(self):
        goalPointsRequired = (self.level + 1) * 5
        if self.goalPoints >= goalPointsRequired:
            if self.level < 15: # 15 to maksymalny poziom
                self.level += 1
                self.goalPoints -= goalPointsRequired
                self.move_every = int(round(1/self.speeds[self.level-1], 0))
                self.update_score(0)

    # Funkcja aktualizująca (losująca) kolejny klocek oraz wyświetlająca okno następnego klocka
    def update_next(self):
        self.clear_win(self.next_win)
        rand = random.randint(1, 57)
        if rand not in [1, 2]:
            keys = list(Player.TYPES.keys())
            keys.remove(self.next)
            self.next = random.choice(keys)
        self.next_win.addstr(1, 3, f"Next: {self.next}", curses.A_BOLD)
        shape, color = Player.TYPES[self.next]
        for y, row in enumerate(shape.split()):
            for x, block in enumerate(row):
                char = Block.CHARS['block'] if block == "x" else " "
                self.next_win.addstr(y+3, x*2+3, char*2, curses.color_pair(color))
        self.next_win.refresh()

    # Funkcja tworząca pustą planszę tetris (wypełnioną nieaktywnymi obiektami Block)
    def init_board(self, one_row=False):
        board = []
        for y in range(self.SIZE[1]):
            row = []
            for x in range(self.SIZE[0]):
                row.append(Block(False))
            if one_row:
                return row
            board.append(row)
        return board

    # Funkcja sprawdzająca czy gracz przegrał
    def check_end(self):
        # Jeżeli jakikolwiek bloczek w najwyższej warswie jest aktywny oznacza to że gracz przegrał
        return True if any([block for block in self.board[0] if block.active]) else False
    
    # Funkcja sprawdzająca i usuwająca kompletne warstwy na planszy (oraz wyliczająca punkty)
    def check_lines(self):
        rows = 0
        for y, row in enumerate(self.board):
            if len([x for x in row if x.active]) == self.SIZE[0]:
                rows += 1
                self.board.pop(y)
                self.add_row()
        if rows == 0:
            return
        multi = [40, 100, 300, 1200]
        cur_score = multi[rows-1] * (self.level + 1)  
        self.goalPoints += rows * (self.level + 1)
        self.update_score(cur_score)
        self.update_level()

    # Funkcja dodająca nową warstwę do planszy
    def add_row(self, custom_board=None):
        board = self.board if custom_board is None else custom_board
        board.insert(0, self.init_board(one_row=True))

    # Funkcja wyświetlająca planszę tetris
    def display(self, custom_board=None):
        board = self.board if custom_board is None else custom_board
        for y, row in enumerate(board):
            for x, block in enumerate(row):
                char = block.getch()*2 if block.active else " " + block.getch()
                self.win.addstr(y+1, x*2+1, char, curses.color_pair(block.color))
        self.win.refresh()


# Jeżeli wywoływany jest aktualny plik to tworzymy nową grę tetris
if __name__ == "__main__":
    while True:
        tetris = Tetris()
        if not tetris.restart:
            break

