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
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from threading import Thread

import Stepper

distUp = 2 * 25.4
distBack = 4 * 25.4
stopDistLeft = 2.25 * 25.4
stopDistRight = 2.5 * 25.4

rightStartPosition = 2.05 * 25.4
leftStartPosition = 2.45* 25.4
ballDiameter = 2.25 * 25.4     

liftSpeed = 40
lowerSpeed = 120
horizontalSpeed = 30

rightHorizontalStepper = Stepper.Stepper(port = 2, microSteps = 32, stepsPerUnit = 25, speed = horizontalSpeed)
rightVerticalStepper = Stepper.Stepper(port = 3, microSteps = 32, speed = liftSpeed)

leftHorizontalStepper = Stepper.Stepper(port = 0, microSteps = 32, stepsPerUnit = 25, speed = horizontalSpeed)
leftVerticalStepper = Stepper.Stepper(port = 1, microSteps = 32, speed = liftSpeed)
   

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////
 
def quitAll():
    rightHorizontalStepper.free()
    rightVerticalStepper.free()
    leftVerticalStepper.free()
    leftHorizontalStepper.free()
    print("tried quitting")
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

def move_thread():
    Thread(target=partial(polygon, sides)).start()
    
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

    leftHorizontalStepper.startGoToPosition(leftStartPosition)
    rightHorizontalStepper.startGoToPosition(rightStartPosition)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
    
    transitionBack('main')
        
def stopBalls():
    #bring the vertical steppers down
    leftVerticalStepper.startGoToPosition(0)   
    rightVerticalStepper.startGoToPosition(0)
    
    while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
        continue
    
    #move the horizontal steppers back to the home position
    leftHorizontalStepper.startGoToPosition(0)
    rightHorizontalStepper.startGoToPosition(0)
       
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
       
    #move the vertical steppers up    
    leftVerticalStepper.setSpeed(liftSpeed)
    rightVerticalStepper.setSpeed(liftSpeed)
    
    leftVerticalStepper.startRelativeMove(distUp)
    rightVerticalStepper.startRelativeMove(distUp)
       
    while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
        continue
        
    #move the horizontal steppers in to the middle
    leftHorizontalStepper.startRelativeMove(1 * stopDistLeft)
    rightHorizontalStepper.startRelativeMove(1 * stopDistRight)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
    
    #bring the vertical steppers down
    leftVerticalStepper.startGoToPosition(0)   
    rightVerticalStepper.startGoToPosition(0)
    
    while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
        continue
    
    #bring the horizontal steppers back to their starting position
    leftHorizontalStepper.startGoToPosition(leftStartPosition)
    rightHorizontalStepper.startGoToPosition(rightStartPosition)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
        
    transitionBack('main')


def pause(text, sec, originalScene):
    sm.transition.direction = 'left'
    sm.current = 'pauseScene'
    sm.current_screen.ids.pauseText.text = text
    load = Animation(size = (10, 10), duration = 0) + Animation(size = (150, 10), duration = sec)
    load.start(sm.current_screen.ids.progressBar)

def transitionBack(originalScene, *largs):
    sm.transition.direction = 'right'
    sm.current = originalScene
    
    
def stop_balls_thread(*largs):
    Thread(target = stopBalls).start()
    
def scoopBallsThread(numBalls, *largs):
	print("tried threading")
	Thread(target= partial(scoop, MainScreen.numBallsLeft, MainScreen.numBallsRight)).start()
    

# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()

class MyApp(App):
    def build(self):
        return sm

Builder.load_file('main.kv')
Builder.load_file('PauseScene.kv')
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
        MainScreen.numBallsRight = MainScreen.numBallsRight - 1
        if(MainScreen.numBallsRight < 0):
            MainScreen.numBallsRight = 0
        self.numBallsRightLab = str(MainScreen.numBallsRight)
        
    def stopBallsCallback(self):
        pause('Stopping the balls', 5, 'main')
        Clock.schedule_once(stop_balls_thread, 0)
    
    def scoopCallback(self):
        scoop(MainScreen.numBallsLeft, MainScreen.numBallsRight)


    def leftScooperSliderChange(self, value):
        if(value == 0):
            self.ids.leftScooperLabel.text = "0 Balls Left Side"
            MainScreen.numBallsLeft = 0
        elif(value > 0 and value <=1):
            self.ids.leftScooperLabel.text = "1 Ball Left Side"
            MainScreen.numBallsLeft = 1
        elif(value > 1 and value <= 2):
            self.ids.leftScooperLabel.text = "2 Balls Left Side"
            MainScreen.numBallsLeft = 2
        elif(value > 2 and value <= 3):
            self.ids.leftScooperLabel.text = "3 Balls Left Side"
            MainScreen.numBallsLeft = 3
        elif(value >3 and value <= 4):
            self.ids.leftScooperLabel.text = "4 Balls Left Side"
            MainScreen.numBallsLeft = 4
        else:
            self.ids.leftScooperLabel.text = "5 Balls Left Side"
            MainScreen.numBallsLeft = 5
        
        
    def rightScooperSliderChange(self, value):
        #adjust for default vaue being maximum
        newValue = self.ids.rightScooperSlider.max - value
        
        if(newValue == 0):
            self.ids.rightScooperLabel.text = "0 Balls Right Side"
            MainScreen.numBallsRight = 0
        elif(newValue > 0 and newValue <=1):
            self.ids.rightScooperLabel.text = "1 Ball Right Side"
            self.ids.ballOne.color = (100, 100, 100, 0.66)
            MainScreen.numBallsRight = 1
        elif(newValue > 1 and newValue <= 2):
            self.ids.rightScooperLabel.text = "2 Balls Right Side"
            MainScreen.numBallsLeft = 3
        elif(value > 3 and value <= 4):
            MainScreen.numBallsRight = 2
        elif(newValue >2 and newValue <= 3):
            self.ids.rightScooperLabel.text = "3 Balls Right Side"
            MainScreen.numBallsRight = 3
        elif(newValue > 3 and newValue <= 4):
            self.ids.rightScooperLabel.text = "4 Balls Right Side"
            MainScreen.numBallsRight = 4
        else:
            self.ids.rightScooperLabel.text = "5 Balls Right Side"
            MainScreen.numBallsRight = 5
        
        
class PauseScene(Screen):
    pass

sm.add_widget(MainScreen(name = 'main'))
sm.add_widget(PauseScene(name = 'pauseScene'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

#home all of the hardware
#home()

MyApp().run()
quitAll()
