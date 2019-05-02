from PIL import ImageGrab
import win32gui
import pyautogui
import threading
from time import sleep
import random
import json
import datetime

class DataBase:

    def __init__(self):
        self.testing = {}
        self.approved = {}
        self.load()


    def getWord(self, start, ban):
        if not start in self.testing:
            print('Error400')
            return ''

        tries = 0
        while True:
            go = True
            if (len(self.testing[start]) > 0 and tries < 2) or len(self.approved[start]) == 0:
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
            'ENDGAME':(33, 867),
            'BACKTOLOBBY':(235, 635),
            'QUICKMATCH':(304, 425),
            'BACK':(30, 910),
            'MULTIPLAYER':(355, 510),
            'CONTINUEASAGUEST':(244, 686),
            'ENEMYFACE':(360, 260)
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
        self.hwnd = win32gui.FindWindow(None, "BlueStacks")
        win32gui.SetForegroundWindow(self.hwnd)
        dimensions = win32gui.GetWindowRect(self.hwnd)

        self.x = dimensions[0]
        self.y = dimensions[1]
        self.w = dimensions[2] - self.x
        self.h = dimensions[3] - self.y
        self.enemyTurn = True
        self.keyboard = KeyBoard((self.w, self.h))
        self.database = DataBase()
        self.searchingTime = 0

        #print(dimensions)


    def getImage(self):
        win32gui.SetForegroundWindow(self.hwnd)
        self.image = ImageGrab.grab((self.x, self.y, self.x + self.w, self.y + self.h))
        #self.image.show()
        self.pixels = self.image.load()


    def detectScreen(self):
        self.getImage()
        keyPixels = [(self.w // 2 - 10, 65), (self.w // 2 + 10, 65), self.keyboard.keys['ENDGAME'], self.keyboard.keys['ENEMYFACE']]
        keyPixelsColor = []
        for pixel in keyPixels:
            keyPixelsColor.append(self.pixels[pixel[0], pixel[1]])
        print(keyPixelsColor)

        windows = {
            'MainScreen': [(232, 72, 85), (45, 48, 71), (255, 221, 103), (255, 255, 255)],
            'NeedToContinueAsAGuest': [(73, 23, 27), (14, 15, 22), (80, 69, 32), (255, 255, 255)],
            'MultiplayerScreen': [(232, 72, 85), (232, 72, 85), (45, 48, 71), (232, 72, 85)],
            'SearchingScreen': [(232, 72, 85), (45, 48, 71), (232, 72, 85), (45, 48, 71)],
            'EnemyFound': [(232, 72, 85), (45, 48, 71), (232, 72, 85)],
            'EnemyTurn': [(45, 48, 71), (45, 48, 71), (224, 226, 242)],
            'MyTurn': [(232, 72, 85), (232, 72, 85), (224, 226, 242)],
            'OopsUsedWord': [(236, 60, 74), (236, 60, 74), (230, 185, 202)],#
            'NeedToReturn': [(-1, -1, -1)],#
            'GameEndedWin': [(232, 72, 85), (232, 72, 85), (255, 255, 255)],
            'GameEndedLose': [(45, 48, 71), (45, 48, 71), (255, 255, 255)],
            'BlueStacksBroke': [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
            'LoadingScreen': [(224, 12, 12), (224, 12, 12), (224, 12, 12), (224, 12, 12)]
        }

        for window in windows:
            similar = True
            for obj in range(len(windows[window])):
                if windows[window][obj] != keyPixelsColor[obj]:
                    similar = False
            if similar:
                return window
        return 'Ad'


    def grind(self):
        while True:
            self.whatToDo()


    def whatToDo(self):
        currentScreen = self.detectScreen()
        print(datetime.datetime.now(), "\t:\t\t", currentScreen, "\n")
        if currentScreen == 'MainScreen':
            self.press('MULTIPLAYER')
            sleep(1)
        elif currentScreen == 'NeedToContinueAsAGuest':
            self.press('CONTINUEASAGUEST')
            sleep(5)
        elif currentScreen == 'MultiplayerScreen':
            self.press('QUICKMATCH')
            sleep(5)
        elif currentScreen == 'SearchingScreen' and self.searchingTime >= 15:
            self.press('BACK')
            self.searchingTime = 0
            sleep(1)
        elif currentScreen == 'SearchingScreen':
            self.searchingTime += 1
            sleep(2)
        elif currentScreen == 'EnemyTurn':
            self.searchingTime = 0
            sleep(1)
        elif currentScreen == 'MyTurn':
            self.doTurn()
            sleep(5)
        elif currentScreen == 'OopsUsedWord':
            self.press('BACK')
            sleep(1)
        elif currentScreen.startswith('GameEnded'):
            self.database.save()
            sleep(1)
            self.database.load()
            self.press('BACK')
            sleep(5)
        elif currentScreen == 'Ad':
            self.press('BACK')
            sleep(3)
        elif currentScreen == 'EnemyFound':
            sleep(3)
        elif currentScreen == 'BlueStacksBroke':
            print('Error401')
            exit()
        elif currentScreen == 'LoadingScreen':
            sleep(5)



    def getPixelByKey(self, char):
        self.getImage()
        return self.pixels[self.keyboard.keys[char][0], self.keyboard.keys[char][1]]


    def press(self, char):
        pyautogui.click((self.x + self.keyboard.keys[char][0], self.y + self.keyboard.keys[char][1]))


    def doTurn(self):
        self.getImage()
        self.keyboard.analyze(self.pixels)

        while True:
            word = self.database.getWord(self.keyboard.start, self.keyboard.ban)

            if word == '':
                break

            for char in word:
                self.press(char)
            self.press('OK')

            sleep(0.4)

            if self.detectScreen() == 'OopsUsedWord':
                self.press('BACK')
                sleep(0.3)

            if self.getPixelByKey('OK') != (133, 196, 59):
                if not word in self.database.approved[self.keyboard.start]:
                    self.database.approved[self.keyboard.start].append(word)
                break

            for i in range(len(word)):
                self.press('ERASE')



from pynput import keyboard

def screenSave():
    hwnd = win32gui.FindWindow(None, 'BlueStacks')
    win32gui.SetForegroundWindow(hwnd)
    dimensions = win32gui.GetWindowRect(hwnd)

    image = ImageGrab.grab(dimensions)
    image.show()
    image.save("opaf5.jpg", "JPEG")


def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
        if key.char == 'p':
            screenSave()
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


if __name__ == '__main__':
    BattleText = Game()
    #Game = threading.Thread(target=BattleText.grind)
    #Game.start()
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    BattleText.grind()
