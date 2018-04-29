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

# ////////////////////////////////////////////////////////////////
# //                       MAIN VARIABLES                       //
# ////////////////////////////////////////////////////////////////

distUp = 2 * 25.4
distBack = 4 * 25.4

stopDistLeft = 2.25 * 25.4
stopDistRight = 2.5 * 25.4

leftStartPosition = stopDistLeft  #2.45 * 25.4
rightStartPosition = stopDistRight  #2.05 * 25.4

ballDiameter = 2.25 * 25.4     

lowerSpeed = 120
liftSpeed = 40
horizontalSpeed = 30

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
	
def checkHorizontalSteppersIfBusy()
	if(rightHorizontalStepper.isBusy() or leftHorizontalStepper.isBusy()):
		return True
	else:
		return False
		
def checkVerticalSteppersIfBusy():
	if(rightVerticalStepper.isBusy() or leftVerticalStepper.isBusy()):
		return True
	else:
		return False
	
def moveSteppersToStart():
	leftHorizontalStepper.startGoToPosition(leftStartPosition)
    rightHorizontalStepper.startGoToPosition(rightStartPosition)
	
	while checkHorizontalSteppersIfBusy()
		continue
	return
    
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
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
    
def scoop():
    global numScoop
    
	if((sm.get_screen('main').numBallsLeft + sm.get_screen('main').numBallsRight) == 0):
		return
		
    if(numScoop > 0):
        while(stopBalls()):
            continue
    
    distLeft = leftStartPosition + ballDiameter * sm.get_screen('main').numBallsLeft
    distRight = rightStartPosition + ballDiameter * sm.get_screen('main').numBallsRight
    
    moveSteppersToStart()
	
	rightHorizontalStepper.startGoToPosition(distRight)
	leftHorizontalStepper.startGoToPosition(distLeft)
	
	while checkHorizontalSteppersIfBusy():
		continue
         
    leftVerticalStepper.startRelativeMove(distUp)
    rightVerticalStepper.startRelativeMove(distUp)
       
    while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
        continue
        
    #moving back
    if (numLeft != 0): 
        leftHorizontalStepper.relativeMove(-1 * distBack)
    if (numRight != 0): 
        rightHorizontalStepper.relativeMove(-1 * distBack)
        
    while checkHorizontalSteppersIfBusy():
        continue
        
    #letting go
    moveSteppersToStart()
    
    while checkVerticalSteppersIfBusy():
        continue

    moveSteppersToStart()
    
    while checkHorizontalSteppersIfBusy():
        continue

    resetAllWidgets()
    transitionBack('main')
    numScoop+=1
	
def scoopFiveBalls():
    distLeft = leftStartPosition + ballDiameter * sm.get_screen('main').numBallsLeft
    distRight = rightStartPosition + ballDiameter * sm.get_screen('main').numBallsRight

	#move the left stepper to position
	leftHorizontalStepper.goToPosition(distLeft)
	
	#move the left vertical stepper up
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
	leftVerticalStepper.startGoToPosition(0)
	rightVerticalStepper.startGoToPosition(0)
	
	while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
		continue
	
	#move the horizontal steppers back to the starting position
	leftHorizontalStepper.startGoToPosition(leftStartPosition)
	rightHorizontalStepper.startGoToPosition(rightStartPosition)
	
	while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
		continue
		
	resetAllWidgets()
	transitionBack('main')
	numScoop+=1
	return
        
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
    leftVerticalStepper.relativeMove(distUp)
    rightVerticalStepper.relativeMove(distUp)
       
    while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
        continue
        
    #move the horizontal steppers in to the middle
    leftHorizontalStepper.relativeMove(1 * stopDistLeft)
    rightHorizontalStepper.relativeMove(1 * stopDistRight)
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
    
    #bring the vertical steppers down
    leftVerticalStepper.startGoToPosition(0)   
    rightVerticalStepper.startGoToPosition(0)
    
    while leftVerticalStepper.isBusy() or rightVerticalStepper.isBusy():
        continue
    
    #bring the horizontal steppers back to their starting position
    moveSteppersToStart()
    
    while leftHorizontalStepper.isBusy() or rightHorizontalStepper.isBusy():
        continue
    
    return
        
def stop_balls_thread(*largs):
	Thread(target = stopBalls).start()
		
def scoop_balls_thread(*largs):
	if(sm.get_screen('main').numBallsLeft + sm.get_screen('main').numBallsRight <= 4):
		Thread(target = scoop).start()
	else:
		Thread(target = scoopFiveBalls).start()

def pause(text, sec, originalScene):
    sm.transition.direction = 'left'
    sm.current = 'pauseScene'
    sm.current_screen.ids.pauseText.text = text
    load = Animation(size = (10, 10), duration = 0) + Animation(size = (150, 10), duration = sec)
    load.start(sm.current_screen.ids.progressBar)
        
def transitionBack(originalScene, *larg):
    sm.transition.direction = 'right'
    sm.current = originalScene

def resetAllWidgets():
    sm.get_screen('main').ids.rightScooperSlider.value = 4
    sm.get_screen('main').ids.leftScooperSlider.value = 0
            
    sm.get_screen('main').ids.rightScooperLabel.text = "Control The Right Scooper"
    sm.get_screen('main').ids.leftScooperLabel.text = "Control The Left Scooper"
   
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
Window.clearcolor = (1, 1, 1, 1) # (WHITE)
       
# ////////////////////////////////////////////////////////////////
# //        MainScreen Class                                    //
# ////////////////////////////////////////////////////////////////
    
class MainScreen(Screen):
    numBallsRight = 0
    numBallsLeft = 0
    
    def exitProgram(self):
        quitAll()
    
    def stopBallsCallback(self):
        pause('Stopping the balls', 5, 'main')
        Clock.schedule_once(stop_balls_thread, 0)
    
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
