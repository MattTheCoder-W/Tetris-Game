#!/usr/bin/env python3

"""
Klasa Block - odpowiada za pojedynczy bloczek na planszy tetris

Atrybuty:
    active - (bool) czy blok jest aktywny?
        True -> Jest przedstawiany jako █
        False -> Jest przedstawiany jako ·
    color - (int) Numer koloru bloku (zgodnie z kolorami terminala UNIXowego)
        domyślnie: 0 -> biały
    is_prev - (bool) czy blok jest podglądem upadku
        True -> Jest przedstawiany jako ░
        False -> Jest przedstawiany jako █

Autor: MattTheCoder-W
"""

class Block:
    CHARS={"block": "█", "dot": "·", "prev": "░"}
    def __init__(self, active: bool, color=0):
        self.active = active
        self.color = color
        self.is_prev = False


    # funkcje ustawiające parametry
    def set_state(self, state: bool):
        self.active = state

    def set_color(self, color: int):
        self.color = color

    def set_prev(self, prev: bool):
        self.is_prev = prev


    # Funkcja zwracająca odpowiedni znak w zależności od typu bloku
    def getch(self):
        if self.is_prev:
            return self.CHARS['prev']
        elif self.active:
            return self.CHARS['block']
        else:
            return self.CHARS['dot']

