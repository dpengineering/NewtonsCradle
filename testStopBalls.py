import sys
import time
sys.path.insert(0, 'Libraries')
import Stepper

distBack = 5 * 25.4
distUp = 3.2 * 25.4

stopDistLeft = 2.41 * 25.4
stopDistRight = 2.41 * 25.4

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

leftVerticalStepper.home(0)
rightVerticalStepper.home(0)
leftHorizontalStepper.home(0)
rightHorizontalStepper.home(0)

def releaseBalls():
    changeVerticalSteppersSpeed(dropSpeed)

    leftVerticalStepper.startGoToPosition(0)
    rightVerticalStepper.startGoToPosition(0)

    while checkVerticalSteppersIfBusy():
        continue

def moveSteppersToStop():
    changeHorizontalSteppersSpeed(horizontalSpeedSlow)

    leftHorizontalStepper.startGoToPosition(stopDistLeft)
    rightHorizontalStepper.startGoToPosition(stopDistRight)

    while checkHorizontalSteppersIfBusy():
        continue

    changeHorizontalSteppersSpeed(horizontalSpeed)

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

def pickupBalls(stoppingBalls=False):
    changeVerticalSteppersSpeed(liftSpeed)

    leftVerticalStepper.startRelativeMove(distUp)
    rightVerticalStepper.startRelativeMove(distUp)

    while checkVerticalSteppersIfBusy():
        continue

def checkHorizontalSteppersIfBusy():
    if(rightHorizontalStepper.isBusy() or leftHorizontalStepper.isBusy()):
        return True
    else:
        return False

def moveSteppersToZero():
    leftHorizontalStepper.startGoToPosition(0)
    rightHorizontalStepper.startGoToPosition(0)

    while checkHorizontalSteppersIfBusy():
        continue

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

    while(checkHorizontalSteppersIfBusy()):
        continue

    releaseBalls()
    return

if __name__ == "__main__":
    stopBalls()
