
# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.clock import Clock


#////////////////////////////////////////////////////////////////
#//                     CUSTOM CLASS SETUP                     //
#////////////////////////////////////////////////////////////////

import Slush
b = Slush.sBoard()

class Stepper(Slush.Motor):

    def __init__(self, port, runCurrent=20, accelCurrent=20, deaccelCurrent=20, holdCurrent=20):
        super().__init__(port)
        self.resetDev()
        self.setCurrent(runCurrent, accelCurrent, deaccelCurrent, holdCurrent)

    def getStepper(self):
        return self

    def home(self):
        self.goUntilPress(1, 1, 200)
        self.setAsHome()
        
class XStepper(Stepper):

    def __init__(self, port1, port2):
        self.stepper1 = Stepper(port1)
        self.stepper2 = Stepper(port2)

    def move1(direc, pos):
        self.stepper1.goToDir(direc, pos)
    
    def move2(direc, pos):
        self.stepper2.goToDir(direc, pos)
        
    def test(self, dir1, s1, dir2, s2):
        self.stepper1.getStepper().goUntilPress(0, dir1, s1)
        self.stepper2.getStepper().goUntilPress(0, dir2, s2)

    def getStepper2():
        return self.stepper2
        
    # For homing, the port of the limit switch does not matter, for the pi(?) 
    # associates the motor port to a corresponding limit switch port on its own
    def home1(self, direc, s):
        self.stepper1.getStepper().goUntilPress(0, direc, s)
        
    def home2(self, direc, s):
        self.stepper2.getStepper().goUntilPress(0, direc, s)
        
class YStepper(Stepper):

    def __init__(self, port1, port2):
        self.stepper1 = Stepper(port1)
        self.stepper2 = Stepper(port2)

    def move1(direc, pos):
        self.stepper1.goToDir(direc, pos)
    
    def move2(direc, pos):
        self.stepper2.goToDir(direc, pos)
        
    def test(self, dir1, s1, dir2, s2):
        self.stepper1.getStepper().goUntilPress(0, dir1, s1)
        self.stepper2.getStepper().goUntilPress(0, dir2, s2)

    def getStepper2():
        return self.stepper2
        
    # For homing, the port of the limit switch does not matter, for the pi(?) 
    # associates the motor port to a corresponding limit switch port on its own
    def home1(self, direc, s):
        self.stepper1.getStepper().goUntilPress(0, direc, s)
        
    def home2(self, direc, s):
        self.stepper2.getStepper().goUntilPress(0, direc, s)
