#!/usr/bin/python3

import sys
import time
from threading import Thread
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

# necessary to include folders in main directory for imports
sys.path.insert(0, 'Kivy/')
sys.path.insert(0, 'Kivy/Scenes/')
sys.path.insert(0, 'Libraries')
sys.path.insert(0, '/usr/local/lib/python2.7/dist-packages')

import AdminScreen
import Stepper

# ////////////////////////////////////////////////////////////////
# //                       MAIN VARIABLES                       //
# ////////////////////////////////////////////////////////////////
distBack = 5 * 25.4 + 50
distUp = 3.2 * 25.4

stopDistLeft = 2.41 * 25.4
stopDistRight = 2.41 * 25.4

leftStartPosition = stopDistLeft - 5
rightStartPosition = stopDistRight - 5

ballDiameter = 2.25 * 25.4

liftSpeed = 40
dropSpeed = 800

horizontalSpeedSlow = 15
horizontalSpeed = 36

accel = 45

rightHorizontalStepper = Stepper.Stepper(port=0, microSteps=16,
                                         stepsPerUnit=25, speed=horizontalSpeed, accel=accel)
rightVerticalStepper = Stepper.Stepper(port=1, microSteps=8,
                                       speed=liftSpeed, accel=accel)

leftHorizontalStepper = Stepper.Stepper(port=2, microSteps=16,
                                        stepsPerUnit=25, speed=horizontalSpeed, accel=accel)
leftVerticalStepper = Stepper.Stepper(port=3, microSteps=8,
                                      speed=liftSpeed, accel=accel)

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
    if (rightHorizontalStepper.isBusy() or leftHorizontalStepper.isBusy()):
        return True
    else:
        return False


def checkVerticalSteppersIfBusy():
    if (rightVerticalStepper.isBusy() or leftVerticalStepper.isBusy()):
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


def pickupBalls(stoppingBalls=False):
    changeVerticalSteppersSpeed(liftSpeed)

    if (sm.get_screen('main').numBallsLeft != 0 or stoppingBalls):
        leftVerticalStepper.startRelativeMove(distUp)
    if (sm.get_screen('main').numBallsRight != 0 or stoppingBalls):
        rightVerticalStepper.startRelativeMove(distUp)

    while checkVerticalSteppersIfBusy():
        continue
    return

def slowMoveDownToDrop():
    numBallsLeft = sm.get_screen('main').numBallsLeft
    numBallsRight = sm.get_screen('main').numBallsRight
    rightLowerDistance = 0
    leftLowerDistance = 0

    #Change lower distance for right scooper
    if numBallsRight == 1:
        rightLowerDistance = -35
    elif numBallsRight == 2:
        rightLowerDistance = -35
    elif numBallsRight == 3:
        rightLowerDistance = -30
    else:
        rightLowerDistance = -35

    #Change lower distance for left scooper
    if numBallsLeft == 1:
        leftLowerDistance = -35
    elif numBallsLeft == 2:
        leftLowerDistance = -35
    elif numBallsLeft == 3:
        leftLowerDistance = -30
    else:
        leftLowerDistance = -35

    changeVerticalSteppersSpeed(10)
    time.sleep(0.1) #ensure speed was changed

    if numBallsRight > 0:
        rightVerticalStepper.startRelativeMove(rightLowerDistance)

    if numBallsLeft > 0:
        leftVerticalStepper.startRelativeMove(leftLowerDistance)


    while checkVerticalSteppersIfBusy():
        continue

    time.sleep(1)

    releaseBalls()
    return

def getBackUpDistance(rightDistance=True):
    numBallsLeft = sm.get_screen('main').numBallsLeft
    numBallsRight = sm.get_screen('main').numBallsRight
    backUpDistRight = 0
    backUpDistLeft = 0

    # Change pick up distances for right side
    if numBallsLeft == 0 and numBallsRight == 0:
        return 0
    elif numBallsRight == 1:
        backUpDistRight = -1 * distBack
    elif numBallsRight == 2:
        backUpDistRight = -1 * distBack + 95
    elif numBallsRight == 3:
        backUpDistRight = -1 * distBack + 85
    else:
        backUpDistRight = -1 * distBack + 95

    # Change pick up distances for left side
    if numBallsLeft == 0:
        backUpDistLeft = 0
    elif numBallsLeft == 1:
        backUpDistLeft = -1 * distBack
    elif numBallsLeft == 2:
        backUpDistLeft = -1 * distBack + 95
    elif numBallsLeft == 3:
        backUpDistLeft = -1 * distBack + 85
    else:
        backUpDistLeft = -1 * distBack + 95

    if rightDistance:
        return backUpDistRight
    else:
        return backUpDistLeft


def moveSteppersBackToDrop(fiveBalls=False):
    numBallsLeft = sm.get_screen('main').numBallsLeft
    numBallsRight = sm.get_screen('main').numBallsRight

    if fiveBalls:
        pass
    else: #if we are not scooping five balls
        if numBallsLeft > 0 and numBallsRight >0:
            rightHorizontalStepper.startRelativeMove(getBackUpDistance())
            leftHorizontalStepper.startRelativeMove(getBackUpDistance(rightDistance=False))
        elif numBallsRight > 0:
            rightHorizontalStepper.startRelativeMove(getBackUpDistance())

        elif numBallsLeft > 0:
            leftHorizontalStepper.startRelativeMove(getBackUpDistance(rightDistance=False))

    while checkHorizontalSteppersIfBusy():
        continue

    return


def moveSteppersToZero():
    leftHorizontalStepper.home(0)
    rightHorizontalStepper.home(0)

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

    # ensure slider label text resets
    sm.get_screen('main').ids.rightScooperLabel.text = "Slide To Control Right Scooper"
    sm.get_screen('main').ids.leftScooperLabel.text = "Slide To Control Left Scooper"

    # ensure slider border is redrawn
    sm.get_screen('main').ids.rightScooperSlider.background_width = 100
    sm.get_screen('main').ids.leftScooperSlider.background_width = 100

    # ensure cursor image is re drawn
    sm.get_screen('main').ids.rightScooperSlider.cursor_image = 'Kivy/Images/right_scooper_image.png'
    sm.get_screen('main').ids.leftScooperSlider.cursor_image = 'Kivy/Images/left_scooper_image.png'

    # ensure the ball image colors are drawn correctly
    sm.get_screen('main').changeImageColors()


def scoopExitTasks():
    resetAllWidgets()
    transitionBack('main')


def home():
    leftVerticalStepper.home(0)
    rightVerticalStepper.home(0)
    leftHorizontalStepper.home(0)
    rightHorizontalStepper.home(0)


def scoop():
    # distances to move when picking up balls
    numLeft = sm.get_screen('main').numBallsLeft
    numRight = sm.get_screen('main').numBallsRight

    if (numLeft + numRight == 0):
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

    while (stopBalls()):
        continue

    moveSteppersToPickupPositions(distRight, distLeft)

    pickupBalls()

    while checkVerticalSteppersIfBusy():
        continue

    moveSteppersBackToDrop()

    slowMoveDownToDrop()

    moveSteppersToZero()

    scoopExitTasks()
    return


# scoop five balls needs to do left side movements first then right side
# in order to prevent collisions
def scoopFiveBalls():
    while (stopBalls()):
        continue

    pickUpDistRight = rightStartPosition + ballDiameter * sm.get_screen('main').numBallsRight
    pickUpDistLeft = leftStartPosition + ballDiameter * sm.get_screen('main').numBallsLeft

    leftHorizontalStepper.goToPosition(pickUpDistLeft)

    changeVerticalSteppersSpeed(liftSpeed)
    leftVerticalStepper.relativeMove(distUp)

    #move left stepper out and to position
    leftHorizontalStepper.relativeMove(getBackUpDistance(rightDistance=False))

    #go to pickup position
    rightHorizontalStepper.goToPosition(pickUpDistRight)
    rightVerticalStepper.relativeMove(distUp)

    rightHorizontalStepper.relativeMove(getBackUpDistance())

    # letting go
    slowMoveDownToDrop()

    # move the horizontal steppers back to the starting position
    moveSteppersToZero()

    scoopExitTasks()
    return


def stopBalls():
    # move horizontal steppers to home position
    moveSteppersToZero()

    # move vertical steppers up
    pickupBalls(True)

    # slowly move the horizontal steppers into the middle/stopping positions
    moveSteppersToStop()

    # bring the vertical steppers down
    time.sleep(3)

    rightHorizontalStepper.startRelativeMove(-5)
    leftHorizontalStepper.startRelativeMove(-5)

    while (checkHorizontalSteppersIfBusy()):
        continue

    releaseBalls()
    return


# ////////////////////////////////////////////////////////////////
# //             Pause and Admin Scene Functions                //
# ////////////////////////////////////////////////////////////////
def pause(text, sec, originalScene):
    sm.transition.direction = 'left'
    sm.current = 'pauseScene'
    sm.current_screen.ids.pauseText.text = text
    load = Animation(size=(10, 10), duration=0) + \
           Animation(size=(150, 10), duration=sec)
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

    pauseTime = 18 + 2 * (max(numLeft, numRight) - 1)

    if (ballSum <= 4):
        pause('Scooping!', pauseTime, 'main')
        Thread(target=scoop).start()
    else:
        pauseTime += 10
        pause('Scooping!', pauseTime, 'main')
        Thread(target=scoopFiveBalls).start()


# ////////////////////////////////////////////////////////////////
# //                     KIVY FILE LOAD-INS                     //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()

class MyApp(App):
    def build(self):
        return sm

Builder.load_file('Kivy/Scenes/main.kv')
Builder.load_file('Kivy/DPEAButton.kv')
Builder.load_file('Kivy/Scenes/PauseScene.kv')
Builder.load_file('Kivy/Scenes/AdminScreen.kv')
Window.clearcolor = (1, 1, 1, 1)  # (WHITE)

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
            color = 1, 1, 1, 1
            red = 1, 0, 0.050, 1
            blue = 0.062, 0, 1, 1
            if (index < self.numBallsLeft):
                # change to blue
                color = blue
            elif (index >= len(imagesList) - self.numBallsRight):
                # change to red
                color = red
            imagesList[index].color = color

    def leftScooperSliderChange(self, value):
        self.numBallsLeft = int(value)

        if ((self.numBallsLeft + self.numBallsRight) > 4):
            self.numBallsRight = 5 - self.numBallsLeft
            self.ids.rightScooperSlider.value = \
                self.ids.rightScooperSlider.max - self.numBallsRight

        # Check the value of each slider and change the text accordingly
        if (self.numBallsLeft == 0):
            self.ids.leftScooperLabel.text = "Slide To Control Left Scooper"
        elif (self.numBallsLeft == 1):
            self.ids.leftScooperLabel.text = \
                str(int(self.numBallsLeft)) + " Ball Left Side: Slide To Adjust"
        else:
            self.ids.leftScooperLabel.text = \
                str(int(self.numBallsLeft)) + " Balls Left Side: Slide To Adjust"

        self.changeImageColors()

    def rightScooperSliderChange(self, value):
        self.numBallsRight = self.ids.rightScooperSlider.max - int(value)
        if ((self.numBallsLeft + self.numBallsRight) > 4):
            self.numBallsLeft = 5 - self.numBallsRight
            self.ids.leftScooperSlider.value = self.numBallsLeft

        # Check the value of each slider and change the text accordingly
        if (self.numBallsRight == 0):
            self.ids.rightScooperLabel.text = "Slide To Control Right Scooper"
        elif (self.numBallsRight == 1):
            self.ids.rightScooperLabel.text = \
                str(int(self.numBallsRight)) + " Ball Right Side: Slide To Adjust"
        else:
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


sm.add_widget(MainScreen(name='main'))
sm.add_widget(PauseScene(name='pauseScene'))
sm.add_widget(AdminScreen.AdminScreen(name='admin'))
sm.add_widget(adminFunctionsScreen(name='adminFunctionsScreen'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

if __name__ == "__main__":
    home()
    MyApp().run()
    quitAll()
