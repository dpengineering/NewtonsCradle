
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



# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()

class MyApp(App):
    def build(self):
        return sm

Builder.load_file('main.kv')
Window.clearcolor = (0.1, 0.1, 0.1, 1) # (BLACK)



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

    def move(direc, pos):
        self.stepper.getStepper().goToDir(direc, pos)
        
    def setSpeed(self, speed):
        self.stepper.getStepper().setMaxSpeed(speed)
        
    def test(self, dir1, s1):
        self.stepper.getStepper().goUntilPress(0, dir1, s1)
        
    # For homing, the port of the limit switch does not matter, for the pi(?) 
    # associates the motor port to a corresponding limit switch port on its own
    def home(self, direc, s):
        self.stepper.getStepper().goUntilPress(0, direc, s)
        self.stepper.getStepper().setAsHome()
        
class YStepper(Stepper):

    def __init__(self, port):
        self.stepper = Stepper(port)

    def move(direc, pos):
        self.stepper.goToDir(direc, pos)
    
    def setSpeed(self, speed):
        self.stepper.getStepper().setMaxSpeed(speed)
        
    def test(self, dir1, s1):
        self.stepper.getStepper().goUntilPress(0, dir1, s1)
        
    def home(self, direc, s):
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
    y1.getStepper().free()
    y2.getStepper().free()
    x1.getStepper().free()
    x2.getStepper().free()
    quit()
    
def home(speed):
    x1.home(0, speed)
    x2.home(1, speed)
    y1.home(0, speed)
    y2.home(0, speed)
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

##### UI might do this instead #####
#~ def checkVals(numRight, numLeft):
    #~ if(numRight > 5):
        #~ correctRight(numRight)
    #~ if(numLeft > 5):
        #~ correctLeft(numLeft)

#~ def correctRight(numRight):
    #~ if(numRight > 5)
        #~ error = 5 - numRight
        
#~ def correctLeft(numLeft):
    #~ if(numRight > 5)
        #~ error = 5 - numLeft
     
       
        
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
    def exitProgram(self):
                quitAll()

sm.add_widget(MainScreen(name = 'main'))



# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

#MyApp().run()
