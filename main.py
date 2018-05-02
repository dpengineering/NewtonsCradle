# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import sys
sys.path.insert(0, 'Libraries/')

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
import AdminScreen

import Stepper

# ////////////////////////////////////////////////////////////////
# //                       MAIN VARIABLES                       //
# ////////////////////////////////////////////////////////////////
distBack = 5 * 25.4 
distUp = 3.25 * 25.4

stopDistLeft = 2.125 * 25.4
stopDistRight = 2.625 * 25.4

leftStartPosition = stopDistLeft
rightStartPosition = stopDistRight

ballDiameter = 2.25 * 25.4     

liftSpeed = 40
dropSpeed = 200

horizontalSpeedSlow = 15
horizontalSpeed = 36

accel = 300

rightHorizontalStepper = Stepper.Stepper(port = 0, microSteps = 16, 
  stepsPerUnit = 25, speed = horizontalSpeed, accel = accel)
rightVerticalStepper = Stepper.Stepper(port = 1, microSteps = 4, 
  speed = liftSpeed, accel = accel)

leftHorizontalStepper = Stepper.Stepper(port = 2, microSteps = 16, 
  stepsPerUnit = 25, speed = horizontalSpeed, accel = accel)
leftVerticalStepper = Stepper.Stepper(port = 3, microSteps = 4, 
  speed = liftSpeed, accel = accel)

numScoop = 0

# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# ////////////////////////////////////////////////////////////////
def quitAll():
    rightHorizontalStepper.free()
    rightVerticalStepper.free()
    leftVerticalStepper.free()
    leftHorizontalStepper.free()
    quit()
    
def checkHorizontalSteppersIfBusy():
    if(rightHorizontalStepper.isBusy() or leftHorizontalStepper.isBusy()):
        return True
    else:
        return False
        
def checkVerticalSteppersIfBusy():
    if(rightVerticalStepper.isBusy() or leftVerticalStepper.isBusy()):
        return True
    else:
        return False

def changeVerticalSteppersSpeed(speed):
    leftVerticalStepper.setSpeed(speed)
    rightVerticalStepper.setSpeed(speed)
    
def changeVerticalSteppersMicroSteps(microSteps):
    leftVerticalStepper.setMicroSteps(microSteps)
    rightVerticalStepper.setMicroSteps(microSteps)

def changeHorizontalSteppersSpeed(speed):
    leftHorizontalStepper.setSpeed(speed)
    rightHorizontalStepper.setSpeed(speed)

def changeHorizontalSteppersMicroSteps(microSteps):
    leftHorizontalStepper.setMicroSteps(microSteps)
    rightHorizontalStepper.setMicroSteps(microSteps)

def releaseBalls():
    changeVerticalSteppersSpeed(dropSpeed)

    leftVerticalStepper.startGoToPosition(0)
    rightVerticalStepper.startGoToPosition(0)

    while checkVerticalSteppersIfBusy():
        continue

def pickupBalls(stoppingBalls = False):
    changeVerticalSteppersSpeed(liftSpeed)
        
    if(sm.get_screen('main').numBallsLeft != 0 or stoppingBalls):
        leftVerticalStepper.startRelativeMove(distUp)
    if(sm.get_screen('main').numBallsRight != 0 or stoppingBalls):
        rightVerticalStepper.startRelativeMove(distUp)
    
    while checkVerticalSteppersIfBusy():
        continue
        
def moveSteppersBackToDrop():
    if(sm.get_screen('main').numBallsLeft != 0):
        leftHorizontalStepper.startRelativeMove(-1 * distBack)
    if(sm.get_screen('main').numBallsRight != 0):
        rightHorizontalStepper.startRelativeMove(-1 * distBack)
    
    while checkHorizontalSteppersIfBusy():
        continue

def moveSteppersToZero():
    leftHorizontalStepper.startGoToPosition(0)
    rightHorizontalStepper.startGoToPosition(0)

    while checkHorizontalSteppersIfBusy():
        continue

def moveSteppersToPickupPositions(distRight, distLeft):
    rightHorizontalStepper.startGoToPosition(distRight)
    leftHorizontalStepper.startGoToPosition(distLeft)
    
    while checkHorizontalSteppersIfBusy():
        continue

def moveSteppersToStop():
    changeHorizontalSteppersSpeed(horizontalSpeedSlow)
   
    leftHorizontalStepper.startGoToPosition(stopDistLeft)
    rightHorizontalStepper.startGoToPosition(stopDistRight)
    
    while checkHorizontalSteppersIfBusy():
        continue
        
    changeHorizontalSteppersSpeed(horizontalSpeed)

def resetAllWidgets():
    sm.get_screen('main').ids.rightScooperSlider.value = 4
    sm.get_screen('main').ids.leftScooperSlider.value = 0
            
    sm.get_screen('main').ids.rightScooperLabel.text = "Control The Right Scooper"
    sm.get_screen('main').ids.leftScooperLabel.text = "Control The Left Scooper"

def scoopExitTasks():
    global numScoop
    
    resetAllWidgets()
    transitionBack('main')
    numScoop+=1
    
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

def scoop():
    #distances to move when picking up balls
    numLeft = sm.get_screen('main').numBallsLeft
    numRight = sm.get_screen('main').numBallsRight
    
    if(numLeft + numRight == 0):
        transitionBack('main')
        return
        
    if numLeft != 0:
        distLeft = leftStartPosition + ballDiameter * numLeft
    else:
        distLeft = 0
    
    if numRight != 0:
        distRight = rightStartPosition + ballDiameter * numRight
    else:
        distRight = 0
    
    if(numScoop > 0):
        while(stopBalls()):
            continue
    
    moveSteppersToPickupPositions(distRight, distLeft)
    
    pickupBalls()
        
    moveSteppersBackToDrop()
    
    releaseBalls()
    
    moveSteppersToZero()

    scoopExitTasks()
    return
    
#scoop five balls needs to do left side movements first then right side
#in order to prevent collisions
def scoopFiveBalls():
    if(numScoop > 0):
        while(stopBalls()):
            continue
    distLeft = leftStartPosition + ballDiameter * sm.get_screen('main').numBallsLeft
    distRight = rightStartPosition + ballDiameter * sm.get_screen('main').numBallsRight
    
    #move the left stepper to position
    leftHorizontalStepper.goToPosition(distLeft)
    
    #move the left vertical stepper up
    changeVerticalSteppersSpeed(liftSpeed)
    leftVerticalStepper.relativeMove(distUp)
    
    #move the left horizontal stepper back to position
    leftHorizontalStepper.relativeMove(-1 * distBack)
    
    #move the right horizontal stepper to position
    rightHorizontalStepper.goToPosition(distRight)
    
    #move the right vertical stepper up            
    rightVerticalStepper.relativeMove(distUp)
    
    #move the right horizontal stepper to drop position
    rightHorizontalStepper.relativeMove(-1 * distBack)
    
    #letting go
    releaseBalls()
    
    #move the horizontal steppers back to the starting position
    moveSteppersToZero()
        
    scoopExitTasks()
    return
        
def stopBalls():
    #releaseBalls()
    
    #move horizontal steppers to home position
    moveSteppersToZero()
       
    #move vertical steppers up
    pickupBalls(True)
    
    #~ leftVerticalStepper.startRelativeMove(distUp)
    #slowly move the horizontal steppers into the middle/stopping positions
    moveSteppersToStop()
    
    #bring the vertical steppers down
    releaseBalls()
    
    return
       
# ////////////////////////////////////////////////////////////////
# //             Pause and Admin Scene Functions                //
# ////////////////////////////////////////////////////////////////
def pause(text, sec, originalScene):
    sm.transition.direction = 'left'
    sm.current = 'pauseScene'
    sm.current_screen.ids.pauseText.text = text
    load = Animation(size = (10, 10), duration = 0) + \
        Animation(size = (150, 10), duration = sec)
    load.start(sm.current_screen.ids.progressBar)
        
def transitionBack(originalScene, *larg):
    sm.transition.direction = 'right'
    sm.current = originalScene
    
# ////////////////////////////////////////////////////////////////
# //                       Threading                            //
# ////////////////////////////////////////////////////////////////
        
def scoop_balls_thread(*largs):
    numLeft = sm.get_screen('main').numBallsLeft
    numRight = sm.get_screen('main').numBallsRight
    ballSum = numLeft + numRight 
    
    pauseTime = 10 + 2 * (max(numLeft, numRight) - 1)
    
    if (numScoop is not 0):
        pauseTime += 10
    
    if(ballSum <= 4):
        pause('Scooping!', pauseTime, 'main')
        Thread(target = scoop).start()
    else:
        pauseTime += 10
        pause('Scooping!', pauseTime + 5, 'main')
        Thread(target = scoopFiveBalls).start()
   
# ////////////////////////////////////////////////////////////////
# //                     KIVY FILE LOAD-INS                     //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()

class MyApp(App):
    def build(self):
        return sm

Builder.load_file('Kivy/main.kv')
Builder.load_file('Libraries/DPEAButton.kv')
Builder.load_file('Kivy/PauseScene.kv')
Builder.load_file('Libraries/AdminScreen.kv')
Window.clearcolor = (1, 1, 1, 1) # (WHITE)
       
# ////////////////////////////////////////////////////////////////
# //        MainScreen Class                                    //
# ////////////////////////////////////////////////////////////////
    
class MainScreen(Screen):
    numBallsRight = 0
    numBallsLeft = 0
    
    def adminAction(self):
            sm.current = 'admin'

    def scoopCallback(self):
        Clock.schedule_once(scoop_balls_thread, 0)
    
    def changeImageColors(self):
        imagesList = [self.ids.ballOne, self.ids.ballTwo, 
            self.ids.ballThree, self.ids.ballFour, self.ids.ballFive]
        
        for index in range(len(imagesList)):
            color = 1,1,1,1
            if (index < self.numBallsLeft):
                color = .7, .82, .988, 1
            elif (index >= len(imagesList) - self.numBallsRight):
                color = .988, .709, .831, 1
            imagesList[index].color = color   

    def leftScooperSliderChange(self, value):
        self.numBallsLeft = int(value)
        
        if((self.numBallsLeft + self.numBallsRight) > 4):
            self.numBallsRight = 5 - self.numBallsLeft
            self.ids.rightScooperSlider.value = \
              self.ids.rightScooperSlider.max - self.numBallsRight

        self.ids.leftScooperLabel.text = \
          str(int(self.numBallsLeft)) + " Balls Left Side"
        self.changeImageColors()

    def rightScooperSliderChange(self, value):
        self.numBallsRight = self.ids.rightScooperSlider.max - int(value)
        if((self.numBallsLeft + self.numBallsRight) > 4):
        
            self.numBallsLeft = 5 - self.numBallsRight
            self.ids.leftScooperSlider.value = self.numBallsLeft
        
        self.ids.rightScooperLabel.text = \
          str(int(self.numBallsRight)) + " Balls Right Side"
        self.changeImageColors()
    
class PauseScene(Screen):
    pass
    
class adminFunctionsScreen(Screen):
    def quitAction(self):
        quitAll()
    
    def homeAction(self):
        home()
        
        while checkHorizontalSteppersIfBusy() or checkVerticalSteppersIfBusy():
            continue
        sm.current = 'main'
    
sm.add_widget(MainScreen(name = 'main'))
sm.add_widget(PauseScene(name = 'pauseScene'))
sm.add_widget(AdminScreen.AdminScreen(name = 'admin'))
sm.add_widget(adminFunctionsScreen(name = 'adminFunctionsScreen'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

#home all of the hardware
home()
MyApp().run()
quitAll()
