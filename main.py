
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
from kivy.properties import StringProperty
#from kivy.clock import Clock



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
        
class XStepper(Stepper):

    def __init__(self, port):
        self.stepper = Stepper(port)

    def move(self, direc, pos):
        self.stepper.getStepper().goToDir(direc, pos)
        
    def setSpeed(self, speed):
        self.stepper.getStepper().setMaxSpeed(speed)
        
    def test(self, dir1, s1):
        self.stepper.getStepper().goUntilPress(0, dir1, s1)
        
    # For homing, the port of the limit switch does not matter, for the pi(?) 
    # associates the motor port to a corresponding limit switch port on its own
    def home(self, direc, s):
        self.stepper.move(-20000)
        self.stepper.getStepper().goUntilPress(0, direc, s)
        self.stepper.getStepper().setAsHome()
        
class YStepper(Stepper):

    def __init__(self, port):
        self.stepper = Stepper(port)

    def move(self, direc, pos):
        self.stepper.goToDir(direc, pos)
    
    def setSpeed(self, speed):
        self.stepper.getStepper().setMaxSpeed(speed)
        
    def test(self, dir1, s1):
        self.stepper.getStepper().goUntilPress(0, dir1, s1)
        
    def home(self, direc, s):
        self.stepper.goTo( 200 * (-direc))
        self.stepper.getStepper().goUntilPress(0, direc, s)
        self.stepper.getStepper().setAsHome()
   
   
        
# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////

x1 = XStepper(0)
x2 = XStepper(1)
y1 = YStepper(2)
y2 = YStepper(3)


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

#values are random
diameter = 1000     
distToBalls = 3000  #distance between the homing position and where the edge of the first ball is
distUp = 1000
distBack = 2000
xSpeed = 1000
ySpeed = 1500

def quitAll():
    y1.free()
    y2.free()
    x1.free()
    x2.free()
    quit()
    
def home(speed):
    x1.home(0, speed)
    x2.home(0, speed)
    #y1.home(0, speed)
    #y2.home(0, speed)
    x1.setSpeed(xSpeed)
    x2.setSpeed(xSpeed)
    y1.setSpeed(ySpeed)
    y2.setSpeed(ySpeed)
    
def scoop(numRight, numLeft):
    #moving to x pos
    distRight = distToBalls + (diameter * numRight)
    distLeft = distToBalls + (diameter * numLeft)
    x1.move(1, distLeft)
    x2.move(0, distRight)
    #scooping
    y1.move(1, distUp)
    y2.move(1, distUp)
    #moveing back
    x1.move(0, distBack)
    x2.move(1, distBack)
    #letting go
    y1.move(0, distUp)
    y2.move(0, distUp)
    home(5000)



# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()

class MyApp(App):
    def build(self):
        return sm

Builder.load_file('main.kv')
Window.clearcolor = (1, 1, 1, 1) # (WHITE)
       
        
# ////////////////////////////////////////////////////////////////
# //        DEFINE MAINSCREEN CLASS THAT KIVY RECOGNIZES        //
# //                                                            //
# //   KIVY UI CAN INTERACT DIRECTLY W/ THE FUNCTIONS DEFINED   //
# //     CORRESPONDS TO BUTTON/SLIDER/WIDGET "on_release"       //
# //                                                            //
# //   SHOULD REFERENCE MAIN FUNCTIONS WITHIN THESE FUNCTIONS   //
# //      SHOULD NOT INTERACT DIRECTLY WITH THE HARDWARE        //
# ////////////////////////////////////////////////////////////////
    
class MainScreen(Screen):
    numBallsLeft = 0
    numBallsLeftLab = StringProperty(str(numBallsLeft))
    numBallsRight = 0
    numBallsRightLab = StringProperty(str(numBallsRight))
    
    def exitProgram(self):
                quitAll()
    
    def numLeftAdd(self):
        MainScreen.numBallsLeft = MainScreen.numBallsLeft + 1
        if(MainScreen.numBallsLeft > 5):
            MainScreen.numBallsLeft = 5
        if(MainScreen.numBallsLeft > (5 - MainScreen.numBallsRight)):
            MainScreen.numBallsRight = MainScreen.numBallsRight - 1
        self.numBallsLeftLab = str(MainScreen.numBallsLeft)
        self.numBallsRightLab = str(MainScreen.numBallsRight)
        
    def numLeftSub(self):
        MainScreen.numBallsLeft = MainScreen.numBallsLeft - 1
        if(MainScreen.numBallsLeft < 0):
            MainScreen.numBallsLeft = 0
        self.numBallsLeftLab = str(MainScreen.numBallsLeft)
        
    def numRightAdd(self):
        MainScreen.numBallsRight = MainScreen.numBallsRight + 1
        if(MainScreen.numBallsRight > 5):
            MainScreen.numBallsRight = 5
        if(MainScreen.numBallsRight > (5 - MainScreen.numBallsLeft)):
            MainScreen.numBallsLeft = MainScreen.numBallsLeft - 1
        self.numBallsRightLab = str(MainScreen.numBallsRight)
        self.numBallsLeftLab = str(MainScreen.numBallsLeft)
        
    def numRightSub(self):
        MainScreen.numBallsRight = MainScreen.numBallsRight - 1
        if(MainScreen.numBallsRight < 0):
            MainScreen.numBallsRight = 0
        self.numBallsRightLab = str(MainScreen.numBallsRight)
        
    def scooop(self):
        scoop(MainScreen.numBallsLeft, MainScreen.numBallsRight)

sm.add_widget(MainScreen(name = 'main'))


# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

home(1000)

#MyApp().run()
