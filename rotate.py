#!/usr/bin/env python3

shape = ".x .x xx"

def printshape(sh):
    for row in sh.split():
        print(row)

def rotate(sh):
    new = ""
    for x in range(len(sh.split()[0]))[::-1]:
        row = ""
        for y in range(len(sh.split())):
            print(x, y)
            row += sh.split()[y][x]
        new += " " + row
    return new

printshape(shape)
printshape(rotate(shape))
