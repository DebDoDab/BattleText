from PIL import ImageGrab
import win32gui
import pyautogui
import threading
from time import sleep
import random
import json

class DataBase:

    def __init__(self):
        self.testing = {}
        self.approved = {}
        self.load()

    def getWord(self, start, ban):
        tries = 0
        while True:
            go = True
            if len(self.testing[start]) > 0 and tries < 2:
                it = random.randint(0, len(self.testing[start])-1)
                word = self.testing[start][it]
                for char in ban:
                    if char in word:
                        go = False
                if go:
                    self.testing[start].remove(word)
                    return word
            else:
                word = self.approved[start][random.randint(0, len(self.approved[start])-1)]
                for char in ban:
                    if char in word:
                        go = False
                if go:
                    return word

    def save(self):
        f = open("testingWords.txt", 'w')
        f.write(json.dumps(self.testing))
        f.close()
        f = open("approvedWords.txt", 'w')
        f.write(json.dumps(self.approved))
        f.close()

    def load(self):
        f = open("testingWords.txt", 'r')
        self.testing = json.loads(f.read())
        f.close()
        f = open("approvedWords.txt", 'r')
        self.approved = json.loads(f.read())
        f.close()



class KeyBoard:

    def __init__(self, currentResolution):
        self.res = (480, 941)
        self.ban = []
        self.start = ''
        self.keys = {
            'q':(33, 682),
            'w':(78, 682),
            'e':(123, 682),
            'r':(168, 682),
            't':(213, 682),
            'y':(258, 682),
            'u':(303, 682),
            'i':(348, 682),
            'o':(393, 682),
            'p':(438, 682),
            'a':(55, 745),
            's':(100, 745),
            'd':(145, 745),
            'f':(190, 745),
            'g':(235, 745),
            'h':(280, 745),
            'j':(325, 745),
            'k':(370, 745),
            'l':(415, 745),
            'z':(93, 806),
            'x':(138, 806),
            'c':(183, 806),
            'v':(228, 806),
            'b':(273, 806),
            'n':(318, 806),
            'm':(363, 806),
            'OK':(438, 608),
            'ERASE':(424, 790),
            'ENDGAME':(30, 850),
            'BACKTOLOBBY':(235, 635),
            'QUICKMATCH':(304, 425),
            'BACK':(30, 910)
        }
        for key in self.keys:
            self.keys[key] = (int(self.keys[key][0] * currentResolution[0] / self.res[0]), int(self.keys[key][1] * currentResolution[1] / self.res[1]))

    def analyze(self, pixels):
        self.start = ''
        self.ban = []
        for key in self.keys:
            if len(key) != 1:
                continue
            if pixels[self.keys[key][0], self.keys[key][1]] == (133, 196, 59):
                self.start = key
            elif pixels[self.keys[key][0], self.keys[key][1]] == (145, 146, 152):
                self.ban.append(key)

class Game:

    def __init__(self):
        hwnd = win32gui.FindWindow(None, "BlueStacks")
        win32gui.SetForegroundWindow(hwnd)
        dimensions = win32gui.GetWindowRect(hwnd)

        self.x = dimensions[0]
        self.y = dimensions[1]
        self.w = dimensions[2] - self.x
        self.h = dimensions[3] - self.y
        self.enemyTurn = True
        self.keyboard = KeyBoard((self.w, self.h))
        self.database = DataBase()

        print(dimensions)
        print((self.x, self.y, self.x + self.w, self.y + self.h))

    def getImage(self):
        self.image = ImageGrab.grab((self.x, self.y, self.x + self.w, self.y + self.h))
        #self.image.show()
        self.pixels = self.image.load()

    def whoseMove(self):
        if self.pixels[self.w//2, 65] == (45, 48, 71):
            self.enemyTurn = True
        elif self.pixels[self.w//2, 65] == (232, 72, 85) and self.pixels[self.keyboard.keys['OK'][0], self.keyboard.keys['OK'][1]] == (133, 196, 59):
            self.enemyTurn = False
        else:
            self.enemyTurn = True

    def grind(self):
        while True:
            self.playGame()
            self.newGame()

    def playGame(self):
        gameIsOn = True
        while gameIsOn:
            print("EnemyTurn")
            while self.enemyTurn:
                self.getImage()
                self.whoseMove()
                if self.pixels[self.keyboard.keys['ENDGAME'][0], self.keyboard.keys['ENDGAME'][1]] == (255, 255, 255):
                    gameIsOn = False
                    print("Game Ended")
                    break
                sleep(1)
            if not gameIsOn:
                break
            print("OurTurn")
            self.doTurn()
            self.enemyTurn = True

    def newGame(self):
        self.database.save()
        sleep(1)
        self.database.load()
        sleep(3)
        self.press('BACK')
        sleep(7)
        self.getImage()
        if self.pixels[self.keyboard.keys['QUICKMATCH'][0], self.keyboard.keys['QUICKMATCH'][1]] != (255, 253, 130):
            self.press('BACK')
            sleep(3)
        self.press('QUICKMATCH')
        sleep(3)

    def press(self, char):
        pyautogui.click((self.x + self.keyboard.keys[char][0], self.y + self.keyboard.keys[char][1]))

    def doTurn(self):
        self.getImage()
        self.keyboard.analyze(self.pixels)
        while True:
            word = self.database.getWord(self.keyboard.start, self.keyboard.ban)
            for char in word:
                self.press(char)
            self.press('OK')

            sleep(0.4)
            self.getImage()
            if self.pixels[self.keyboard.keys['OK'][0], self.keyboard.keys['OK'][1]] != (133, 196, 59):
                self.database.approved[self.keyboard.start].append(word)
                break
            for i in range(len(word)):
                self.press('ERASE')

        sleep(5)



from pynput import keyboard
import os

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


if __name__ == '__main__':
    BattleText = Game()
    Game = threading.Thread(target=BattleText.grind)
    Game.start()
    listener = keyboard.Listener(
        on_press=on_press)
    listener.start()
