
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

import Stepper

distUp = 3 * 25.4
distBack = 4 * 25.4

startPosition = 3.25 * 25.4
ballDiameter = 2.25 * 25.4     

liftSpeed = 30
lowerSpeed = 120

rightHorizontalStepper = Stepper.Stepper(port = 0, microSteps = 32, stepsPerUnit = 25, speed = liftSpeed)
rightVerticalStepper = Stepper.Stepper(port = 1, microSteps = 32, speed = 30)

leftHorizontalStepper = Stepper.Stepper(port = 2, microSteps = 32, stepsPerUnit = 25, speed = liftSpeed)
leftVerticalStepper = Stepper.Stepper(port = 3, microSteps = 32, speed = 30)
   

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////



def quitAll():
    rightHorizontalStepper.free()
    rightVerticalStepper.free()
    leftVerticalStepper.free()
    leftHorizontalStepper.free()
    quit()
    
def home():

    leftVerticalStepper.home(0)   
    rightVerticalStepper.home(0)
    
    leftHorizontalStepper.run(0, leftHorizontalStepper.speed)
    rightHorizontalStepper.run(0, rightHorizontalStepper.speed)
        
    leftIsHome = False
    rightIsHome = False
    while not leftIsHome or not rightIsHome:
        if not leftIsHome and leftHorizontalStepper.readSwitch() == True:
            leftHorizontalStepper.hardStop()
            leftHorizontalStepper.setAsHome()
            leftIsHome = True
        if not rightIsHome and rightHorizontalStepper.readSwitch() == True:
            rightHorizontalStepper.hardStop()
            rightHorizontalStepper.setAsHome()
            rightIsHome = True
   
    leftHorizontalStepper.startGoToPosition(startPosition)
    rightHorizontalStepper.startGoToPosition(startPosition)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue

    
    
    
    
    
def scoop(numRight, numLeft):
    
    if numRight + numLeft > 4:
        print("Collision detected")
        return
        
    #moving to x pos
    distRight = ballDiameter * numRight
    distLeft = ballDiameter * numLeft
    
    if (numLeft != 0): 
        leftHorizontalStepper.startRelativeMove(distLeft)
    if (numRight != 0): 
        rightHorizontalStepper.startRelativeMove(distRight)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
        
    #scooping
    
    if (numLeft != 0): 
       leftVerticalStepper.setSpeed(liftSpeed)
       leftVerticalStepper.startRelativeMove(distUp)

    if (numRight != 0): 
        rightVerticalStepper.setSpeed(liftSpeed)
        rightVerticalStepper.startRelativeMove(distUp)
       
    while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
        continue
        
    #moving back
    if (numLeft != 0): 
        leftHorizontalStepper.startRelativeMove(-1 * distBack)
    if (numRight != 0): 
        rightHorizontalStepper.startRelativeMove(-1 * distBack)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
        
    #letting go
    leftVerticalStepper.setSpeed(lowerSpeed)
    rightVerticalStepper.setSpeed(lowerSpeed)
    leftVerticalStepper.startGoToPosition(0)
    rightVerticalStepper.startGoToPosition(0)
    
    while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
        continue

    leftHorizontalStepper.startGoToPosition(startPosition)
    rightHorizontalStepper.startGoToPosition(startPosition)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue


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
        if(MainScreen.numBallsLeft > 4):
            MainScreen.numBallsLeft = 4
        if(MainScreen.numBallsLeft > (4 - MainScreen.numBallsRight)):
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
        if(MainScreen.numBallsRight > 4):
            MainScreen.numBallsRight = 4
        if(MainScreen.numBallsRight > (4 - MainScreen.numBallsLeft)):
            MainScreen.numBallsLeft = MainScreen.numBallsLeft - 1
        self.numBallsRightLab = str(MainScreen.numBallsRight)
        self.numBallsLeftLab = str(MainScreen.numBallsLeft)
        
    def numRightSub(self):
        MainScreen.numBallsRight = MainScreen.numBallsRight - 1
        if(MainScreen.numBallsRight < 0):
            MainScreen.numBallsRight = 0
        self.numBallsRightLab = str(MainScreen.numBallsRight)
        
    def scoopCallback(self):
        scoop(MainScreen.numBallsLeft, MainScreen.numBallsRight)

sm.add_widget(MainScreen(name = 'main'))


# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

home()

MyApp().run()
quitAll()
