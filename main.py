#!/usr/bin/python3

# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////
import sys
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
import time

#necessary to include folders in main directory for imports
sys.path.insert(0, 'Kivy/')
sys.path.insert(0, 'Libraries')
sys.path.insert(0, '/usr/local/lib/python2.7/dist-packages')

import AdminScreen
import Stepper

# ////////////////////////////////////////////////////////////////
# //                       MAIN VARIABLES                       //
# ////////////////////////////////////////////////////////////////
distBack = 5 * 25.4 
distUp = 3.2 * 25.4

stopDistLeft = 2.12 * 25.4
stopDistRight = 2.57 * 25.4

leftStartPosition = stopDistLeft
rightStartPosition = stopDistRight

ballDiameter = 2.25 * 25.4     

liftSpeed = 40
dropSpeed = 360

horizontalSpeedSlow = 15
horizontalSpeed = 36

accel = 45

rightHorizontalStepper = Stepper.Stepper(port = 0, microSteps = 16, 
  stepsPerUnit = 25, speed = horizontalSpeed, accel = accel)
rightVerticalStepper = Stepper.Stepper(port = 1, microSteps = 8, 
  speed = liftSpeed, accel = accel)

leftHorizontalStepper = Stepper.Stepper(port = 2, microSteps = 16, 
  stepsPerUnit = 25, speed = horizontalSpeed, accel = accel)
leftVerticalStepper = Stepper.Stepper(port = 3, microSteps = 8, 
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

def changeHorizontalSteppersSpeed(speed):
    leftHorizontalStepper.setSpeed(speed)
    rightHorizontalStepper.setSpeed(speed)

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
            
    sm.get_screen('main').ids.rightScooperLabel.text = "Slide To Control The Right Scooper"
    sm.get_screen('main').ids.leftScooperLabel.text = "Slide To Control The Left Scooper"

def scoopExitTasks():
    global numScoop
    
    resetAllWidgets()
    transitionBack('main')
    numScoop += 1
    
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
    
    #slowly move the horizontal steppers into the middle/stopping positions
    moveSteppersToStop()
    
    #bring the vertical steppers down
    time.sleep(1)
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
    resetAllWidgets()
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
        pauseTime += 8
    
    if(ballSum <= 4):
        pause('Scooping!', pauseTime, 'main')
        Thread(target = scoop).start()
    else:
        pauseTime += 10
        pause('Scooping!', pauseTime, 'main')
        Thread(target = scoopFiveBalls).start()
   
# ////////////////////////////////////////////////////////////////
# //                     KIVY FILE LOAD-INS                     //
# ////////////////////////////////////////////////////////////////

sm = ScreenManager()

class MyApp(App):
    def build(self):
        return sm

Builder.load_file('Kivy/main.kv')
Builder.load_file('Kivy/DPEAButton.kv')
Builder.load_file('Kivy/PauseScene.kv')
Builder.load_file('Kivy/AdminScreen.kv')
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
            red = 1, 0, 0.050, 1
            blue = 0.062, 0, 1, 1
            if (index < self.numBallsLeft):
                #change to blue
                color = blue
            elif (index >= len(imagesList) - self.numBallsRight):
                #change to red
                color =  red
            imagesList[index].color = color
        
    def leftScooperSliderChange(self, value):
        self.numBallsLeft = int(value)
        
        if((self.numBallsLeft + self.numBallsRight) > 4):
            self.numBallsRight = 5 - self.numBallsLeft
            self.ids.rightScooperSlider.value = \
              self.ids.rightScooperSlider.max - self.numBallsRight

        self.ids.leftScooperLabel.text = \
          str(int(self.numBallsLeft)) + " Balls Left Side: Slide To Adjust"
        self.changeImageColors()

    def rightScooperSliderChange(self, value):
        self.numBallsRight = self.ids.rightScooperSlider.max - int(value)
        if((self.numBallsLeft + self.numBallsRight) > 4):
        
            self.numBallsLeft = 5 - self.numBallsRight
            self.ids.leftScooperSlider.value = self.numBallsLeft
        
        self.ids.rightScooperLabel.text = \
          str(int(self.numBallsRight)) + " Balls Right Side: Slide To Adjust"
        self.changeImageColors()
        
# ////////////////////////////////////////////////////////////////
# //        PauseScene and Admin Scene Class                    //
# ////////////////////////////////////////////////////////////////
class PauseScene(Screen):
    pass
    
class adminFunctionsScreen(Screen):
    def quitAction(self):
        quitAll()
    
    def homeAction(self):
        home()
        resetAllWidgets()
        
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

home()
MyApp().run()
quitAll()
