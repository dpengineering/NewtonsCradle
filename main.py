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
import AdminScreen
import Stepper

# ////////////////////////////////////////////////////////////////
# //                       MAIN VARIABLES                       //
# ////////////////////////////////////////////////////////////////
distBack = 4 * 25.4 
distUp = 2 * 25.4


stopDistLeft = 2.25 * 25.4
stopDistRight = 2.5 * 25.4

leftStartPosition = stopDistLeft
rightStartPosition = stopDistRight

ballDiameter = 2.25 * 25.4     
liftSpeed = 40
dropSpeed = 120

horizontalSpeed = 30
fastHorizontalSpeed = 60

rightHorizontalStepper = Stepper.Stepper(port = 0, microSteps = 32, stepsPerUnit = 25, speed = horizontalSpeed)
rightVerticalStepper = Stepper.Stepper(port = 1, microSteps = 32, speed = liftSpeed)

leftHorizontalStepper = Stepper.Stepper(port = 2, microSteps = 32, stepsPerUnit = 25, speed = horizontalSpeed)
leftVerticalStepper = Stepper.Stepper(port = 3, microSteps = 32, speed = liftSpeed)

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
    rigtHorizontalStepper.setSpeed(speed)

def releaseBalls():
	changeVerticalSteppersMicroSteps(8)
    changeVerticalSteppersSpeed(dropSpeed)
    
    leftVerticalStepper.startGoToPosition(0)
    rightVerticalStepper.startGoToPosition(0)
    
    while checkVerticalSteppersIfBusy():
        continue

def pickupBalls():
    if(sm.get_screen('main').numBallsLeft != 0):
        leftVerticalStepper.startRelativeMove(distUp)
    if(sm.get_screen('main').numBallsRight != 0):
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

def moveSteppersToStart():
    global stopDistLeft, stopDistRight
    leftHorizontalStepper.startGoToPosition(stopDistLeft)
    rightHorizontalStepper.startGoToPosition(stopDistRight)
    
    while checkHorizontalSteppersIfBusy():
        continue

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
            
    moveSteppersToStart()

    
def scoop():
    global numScoop
    
    #distances to move when picking up balls
    distRight = rightStartPosition + ballDiameter * sm.get_screen('main').numBallsRight
    distLeft = leftStartPosition + ballDiameter * sm.get_screen('main').numBallsLeft
    
    if((sm.get_screen('main').numBallsLeft + sm.get_screen('main').numBallsRight) == 0):
        transitionBack('main')
        return
    
    if(numScoop > 0):
        while(stopBalls()):
            continue
    
    moveSteppersToPickupPositions(distRight, distLeft)
    
    pickupBalls()
        
    moveSteppersBackToDrop()
    
    releaseBalls()
    
    moveSteppersToStart()

    scoopExitTasks()
    return
    
#scoop five balls needs to do left side movements first then right side
#in order to prevent collisions
def scoopFiveBalls():
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
    changeVerticalSteppersSpeed(dropSpeed)
    releaseBalls()
    
    #move the horizontal steppers back to the starting position
    moveSteppersToStart()
        
    scoopExitTasks()
    return
        
def stopBalls():
    releaseBalls()
    
    #move horizontal steppers to home position
    changeHorizontalSteppersSpeed(fastHorizontalSpeed)
	moveSteppersToZero()
       
    #move vertical steppers up
	changeVerticalSteppersSpeed(liftSpeed)
    pickUpBalls()
        
    #slowly move the horizontal steppers into the middle/stopping positions
	changeHorizontalSteppersSpeed(15)
    leftHorizontalStepper.startRelativeMove(1 * stopDistLeft)
    rightHorizontalStepper.startRelativeMove(1 * stopDistRight)
    
    while checkHorizontalSteppersIfBusy():
        continue
    
	changeHorizontalSteppersSpeed(horizontalSpeed)
	
    #bring the vertical steppers down
    releaseBalls()
    
    #bring the horizontal steppers back to their starting position
    moveSteppersToStart()
    
    return
    
# ////////////////////////////////////////////////////////////////
# //                       Threading                            //
# ////////////////////////////////////////////////////////////////

def stop_balls_thread(*largs):
    Thread(target = stopBalls).start()
        
def scoop_balls_thread(*largs):
    if(sm.get_screen('main').numBallsLeft + sm.get_screen('main').numBallsRight <= 4):
        Thread(target = scoop).start()
    else:
        Thread(target = scoopFiveBalls).start()
        
# ////////////////////////////////////////////////////////////////
# //             Pause and Admin Scene Functions                //
# ////////////////////////////////////////////////////////////////

def pause(text, sec, originalScene):
    sm.transition.direction = 'left'
    sm.current = 'pauseScene'
    sm.current_screen.ids.pauseText.text = text
    load = Animation(size = (10, 10), duration = 0) + Animation(size = (150, 10), duration = sec)
    load.start(sm.current_screen.ids.progressBar)
        
def transitionBack(originalScene, *larg):
    sm.transition.direction = 'right'
    sm.current = originalScene
   
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
Builder.load_file('AdminScreen.kv')
Window.clearcolor = (1, 1, 1, 1) # (WHITE)
       
# ////////////////////////////////////////////////////////////////
# //        MainScreen Class                                    //
# ////////////////////////////////////////////////////////////////
    
class MainScreen(Screen):
    numBallsRight = 0
    numBallsLeft = 0
    
    def adminTransition(self):
            sm.current = 'admin'

    def scoopCallback(self):
        pause('Scooping!', 5, 'main')
        Clock.schedule_once(scoop_balls_thread, 0)
    
    def changeImageColors(self):
        imagesList = [self.ids.ballOne, self.ids.ballTwo, self.ids.ballThree, self.ids.ballFour, self.ids.ballFive]
        
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
            self.ids.rightScooperSlider.value = self.ids.rightScooperSlider.max - self.numBallsRight

        self.ids.leftScooperLabel.text = str(int(self.numBallsLeft)) + " Balls Left Side"
        self.changeImageColors()

    def rightScooperSliderChange(self, value):
        self.numBallsRight = self.ids.rightScooperSlider.max - int(value)
        if((self.numBallsLeft + self.numBallsRight) > 4):
        
            self.numBallsLeft = 5 - self.numBallsRight
            self.ids.leftScooperSlider.value = self.numBallsLeft
        
        self.ids.rightScooperLabel.text = str(int(self.numBallsRight)) + " Balls Right Side"
        self.changeImageColors()

    def adminAction(self):
       sm.current = 'admin'
    
class PauseScene(Screen):
    pass

class quitScreen(Screen):
    def quitAction(self):
        quitAll()

sm.add_widget(MainScreen(name = 'main'))
sm.add_widget(PauseScene(name = 'pauseScene'))
sm.add_widget(AdminScreen.AdminScreen(name = 'admin'))
sm.add_widget(quitScreen(name = 'quitScreen'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

#home all of the hardware
home()

MyApp().run()
quitAll()
