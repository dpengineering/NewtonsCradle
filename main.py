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

numBallsRight = 0
numBallsLeft = 0
   
# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
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
            
    leftHorizontalStepper.startGoToPosition(leftStartPosition)
    rightHorizontalStepper.startGoToPosition(rightStartPosition)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
    
def scoop(numRight, numLeft, *largs):
    global numBallsLeft, numBallsRight
    print("scoop called")
    print(numRight)
    print(numLeft)
    print(numBallsRight)
    print(numBallsLeft)
    if numRight + numLeft > 4:
        print("Collision detected")
        return
        
    #moving to x pos
    distRight = ballDiameter * numRight
    distLeft = ballDiameter * numLeft
    
    if (numLeft != 0): 
        leftHorizontalStepper.startGoToPosition(distLeft)
    if (numRight != 0): 
        rightHorizontalStepper.startGoToPosition(distRight)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
        
    #scooping  
    if (numLeft != 0): 
       leftVerticalStepper.setSpeed(liftSpeed)
       leftVerticalStepper.startGoToPosition(distUp)

    if (numRight != 0): 
        rightVerticalStepper.setSpeed(liftSpeed)
        rightVerticalStepper.startGoToPosition(distUp)
       
    while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
        continue
        
    #moving back
    if (numLeft != 0): 
        leftHorizontalStepper.startGoToPosition(-1 * distBack)
    if (numRight != 0): 
        rightHorizontalStepper.startGoToPosition(-1 * distBack)
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
    
def scoop_balls_thread(*largs):
    global numBallsLeft, numBallsRight
    Thread(target = partial(scoop, numBallsLeft, numBallsRight)).start()

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
# //        MainScreen Class                                    //
# ////////////////////////////////////////////////////////////////
    
class MainScreen(Screen):
    global numBallsLeft
    numBallsLeftLab = StringProperty(str(numBallsLeft))
    global numBallsRight
    numBallsRightLab = StringProperty(str(numBallsRight))
    
    def exitProgram(self):
        quitAll()
    
    def stopBallsCallback(self):
        pause('Stopping the balls', 5, 'main')
        Clock.schedule_once(stop_balls_thread, 0)
        self.resetAllWidgets()
    
    def scoopCallback(self):
        pause('Scooping!', 5, 'main')
        Clock.schedule_once(scoop_balls_thread, 0)
        #self.resetAllWidgets()
    
    def resetAllWidgets(self):
        self.ids.rightScooperSlider.value = 5
        self.ids.leftScooperSlider.value = 0
            
        self.ids.rightScooperLabel.text = "Control The Right Scooper"
        self.ids.leftScooperLabel.text = "Control The Left Scooper"
        
    def leftScooperSliderChange(self, value):
        global numBallsLeft
        numBallsLeft = int(value)
        self.ids.leftScooperLabel.text = str(int(numBallsLeft)) + " Balls Left Side"
        
    def rightScooperSliderChange(self, value):
        global numBallsRight
        numBallsRight = int(value)
        self.ids.rightScooperLabel.text = str(int(numBallsRight)) + " Balls Right Side"
        
class PauseScene(Screen):
    pass

sm.add_widget(MainScreen(name = 'main'))
sm.add_widget(PauseScene(name = 'pauseScene'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

#home all of the hardware
home()

MyApp().run()
quitAll()
