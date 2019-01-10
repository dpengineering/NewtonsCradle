#!/usr/bin/python3

import sys
sys.path.insert(0, 'Kivy/')
sys.path.insert(0, 'Kivy/Scenes/')
sys.path.insert(0, 'Libraries')

import time
from threading import Thread
from kivy.properties import ObjectProperty, AliasProperty, NumericProperty
from kivy.animation import Animation
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.vector import Vector
from Kivy.Scenes import AdminScreen
from apscheduler.schedulers.background import BackgroundScheduler
from dpea.utilities import MixPanel
import TemperatureSensor
import Stepper

"""
Globals
"""

MIXPANEL_TOKEN = "02f0373e5a3d6354fbc9d41d6b3a002a"

STEPS_PER_INCH = 25.4
BALL_DIAMETER = 2.25 * STEPS_PER_INCH

STOP_DISTANCE = 2.41 * STEPS_PER_INCH
STOP_DISTANCE_LEFT = STOP_DISTANCE - 3
STOP_DISTANCE_RIGHT = STOP_DISTANCE + 4

START_INSET = 10
START_POSITION_LEFT = STOP_DISTANCE_LEFT - START_INSET
START_POSITION_RIGHT = STOP_DISTANCE_RIGHT - START_INSET

BACKUP_DISTANCE = -4.5 * STEPS_PER_INCH
LIFT_DISTANCE = 3 * STEPS_PER_INCH

VERTICAL_SPEED = 800
LIFT_SPEED = 40
STOPPING_SPEED = 7.5
HORIZONTAL_SPEED = 36

MICRO_STEPS_HORIZONTAL = 16
MICRO_STEPS_VERTICAL = 16
STEPS_PER_UNIT = 25
ACCELERATION = 40

RIGHT_HORIZONTAL_STEPPER = Stepper.Stepper(port=0, microSteps=MICRO_STEPS_HORIZONTAL, stepsPerUnit=STEPS_PER_UNIT,
                                           speed=HORIZONTAL_SPEED, accel=ACCELERATION)
RIGHT_VERTICAL_STEPPER = Stepper.Stepper(port=1, microSteps=MICRO_STEPS_VERTICAL, speed=VERTICAL_SPEED,
                                         accel=ACCELERATION)

LEFT_HORIZONTAL_STEPPER = Stepper.Stepper(port=2, microSteps=MICRO_STEPS_HORIZONTAL, stepsPerUnit=STEPS_PER_UNIT,
                                          speed=HORIZONTAL_SPEED, accel=ACCELERATION)
LEFT_VERTICAL_STEPPER = Stepper.Stepper(port=3, microSteps=MICRO_STEPS_VERTICAL, speed=VERTICAL_SPEED,
                                        accel=ACCELERATION)

GESTURE_MIN_DELTA = 25
GESTURE_MAX_DELTA = 75


"""
Main functions
"""


def quit_all():
    """Called upon exiting UI, frees all steppers"""
    RIGHT_HORIZONTAL_STEPPER.free()
    RIGHT_VERTICAL_STEPPER.free()
    LEFT_VERTICAL_STEPPER.free()
    LEFT_HORIZONTAL_STEPPER.free()
    quit()


def are_horizontal_busy():
    """Check to see if the horizontal steppers are currently busy (moving)"""
    return RIGHT_HORIZONTAL_STEPPER.isBusy() or LEFT_HORIZONTAL_STEPPER.isBusy()


def are_vertical_busy():
    """
    Check to see if the vertical steppers are busy
    :return: True if busy, False if not
    """
    return RIGHT_VERTICAL_STEPPER.isBusy() or LEFT_VERTICAL_STEPPER.isBusy()


def set_vertical_speed(speed):
    """
    Set the speed of the vertical steppers
    :param speed: Speed to set the vertical steppers at
    :return: None
    """
    LEFT_VERTICAL_STEPPER.setSpeed(speed)
    RIGHT_VERTICAL_STEPPER.setSpeed(speed)


def set_horizontal_speed(speed):
    """
    Set the speed of the horizontal steppers
    :param speed: Speed to set the horizontal steppers at
    :return: None
    """
    LEFT_HORIZONTAL_STEPPER.setSpeed(speed)
    RIGHT_HORIZONTAL_STEPPER.setSpeed(speed)


def set_vertical_pos(pos):
    """
    Set the vertical position of the vertical steppers
    :param pos: The position to both of the vertical stepper to
    :return: None
    """
    RIGHT_VERTICAL_STEPPER.startGoToPosition(pos)
    LEFT_VERTICAL_STEPPER.startGoToPosition(pos)

    while are_vertical_busy():
        continue


def set_vertical_poss(pos_l, pos_r):
    """
    Set the vertical position (relative) of the vertical steppers
    :param pos_l: Relative move amount for left vertical stepper
    :param pos_r: Relative move amount for right vertical stepper
    :return: None
    """
    LEFT_VERTICAL_STEPPER.startGoToPosition(pos_l)
    RIGHT_VERTICAL_STEPPER.startGoToPosition(pos_r)

    while are_vertical_busy():
        continue


def set_vertical_pos_rel(r):
    RIGHT_VERTICAL_STEPPER.startRelativeMove(r)
    LEFT_VERTICAL_STEPPER.startRelativeMove(r)

    while are_vertical_busy():
        continue


def set_horizontal_pos(pos):
    """
    Set the horizontal position of the horizontal steppers
    :param pos: Position for each horizontal stepper to start a relative move to
    :return: None
    """
    LEFT_HORIZONTAL_STEPPER.startGoToPosition(pos)
    RIGHT_HORIZONTAL_STEPPER.startGoToPosition(pos)

    while are_horizontal_busy():
        continue


def set_horizontal_poss(pos_l, pos_r):
    """
    Set the horizontal positions of the steppers
    :param pos_l: Position of the left horizontal stepper
    :param pos_r: Position of the right horizontal stepper
    :return: None
    """
    LEFT_HORIZONTAL_STEPPER.startGoToPosition(pos_l)
    RIGHT_HORIZONTAL_STEPPER.startGoToPosition(pos_r)

    while are_horizontal_busy():
        continue


def set_horizontal_pos_rel(r):
    """
    Start a relative horizontal move
    :param r: Amount to perform a horizontal move
    :return: None
    """
    LEFT_HORIZONTAL_STEPPER.startRelativeMove(r)
    RIGHT_HORIZONTAL_STEPPER.startRelativeMove(r)

    while are_horizontal_busy():
        continue


def home():
    """
    Home all of the steppers
    :return:
    """
    LEFT_VERTICAL_STEPPER.home(0)
    RIGHT_VERTICAL_STEPPER.home(0)
    LEFT_HORIZONTAL_STEPPER.home(0)
    RIGHT_HORIZONTAL_STEPPER.home(0)


def send_start_event(num_left, num_right):
    """
    Send the number of balls selected on both sides to MixPanel
    :param num_left: Number of balls selected on the left side
    :param num_right: Number of balls selected on the right side
    :return: None
    """
    global mixpanel
    mixpanel.setEventName("Start")
    mixpanel.addProperty("Left ball count", num_left)
    mixpanel.addProperty("Right ball count", num_right)
    mixpanel.sendEvent()


def check_temperature():
    """
    Check the temperature from the slush engine temperature sensor and send the data to MixPanel
    :return:
    """
    global mixpanel
    temp_sensor = TemperatureSensor.TemperatureSensor()
    temp = temp_sensor.getTemperatureInFahrenheit()

    mixpanel.setEventName("Temperature")
    mixpanel.addProperty("Temperature", temp)
    mixpanel.sendEvent()

def new_scoop():
    """
    New scooped initiated, gets the number of balls on each side and calls the perspective function to control pickups
    :return: None
    """
    num_left = sm.get_screen('main').cradle.num_left()
    num_right = sm.get_screen('main').cradle.num_right()

    if num_left + num_right == 0:
        return

    stop_balls()

    set_vertical_speed(LIFT_SPEED)
    if num_left + num_right == 5:
        scoop_left(num_left)
        scoop_right(num_right)

        while are_horizontal_busy():
            continue
    else:
        scoop_both(num_left, num_right)

    set_vertical_speed(VERTICAL_SPEED)
    release_both()

    home()

    time.sleep(5)

    sm.get_screen('main').unpause()


def scoop_left(num):
    """
    Scoop the balls on the left, doesn't wait for the last move to complete
    :param num: Number of balls to scoop on the left
    :return: None
    """
    if num == 0:
        return

    p = START_POSITION_LEFT + BALL_DIAMETER * num
    set_horizontal_speed(HORIZONTAL_SPEED)
    LEFT_HORIZONTAL_STEPPER.startGoToPosition(p)

    while are_horizontal_busy():
        continue

    LEFT_VERTICAL_STEPPER.startGoToPosition(LIFT_DISTANCE)

    while are_vertical_busy():
        continue

    LEFT_HORIZONTAL_STEPPER.startRelativeMove(BACKUP_DISTANCE)


def scoop_right(num):
    """
    Scoop the balls on the right, doesn't wait for the last move to complete
    :param num: Number of balls to scoop on the right
    :return: None
    """
    if num == 0:
        return

    p = START_POSITION_RIGHT + BALL_DIAMETER * num
    set_horizontal_speed(HORIZONTAL_SPEED)
    RIGHT_HORIZONTAL_STEPPER.startGoToPosition(p)

    while are_horizontal_busy():
        continue

    RIGHT_VERTICAL_STEPPER.startGoToPosition(LIFT_DISTANCE)

    while are_vertical_busy():
        continue

    RIGHT_HORIZONTAL_STEPPER.startRelativeMove(BACKUP_DISTANCE)


def scoop_both(num_left, num_right):
    """
    Scoop both sides
    :param num_left: Number of balls on the left side to be scooped
    :param num_right: Number of balls on the right side to be scooped
    :return: None
    """
    p_r = START_POSITION_RIGHT + BALL_DIAMETER * num_right
    p_l = START_POSITION_LEFT + BALL_DIAMETER * num_left

    set_horizontal_speed(HORIZONTAL_SPEED)
    if num_right > 0:
        RIGHT_HORIZONTAL_STEPPER.startGoToPosition(p_r)
    if num_left > 0:
        LEFT_HORIZONTAL_STEPPER.startGoToPosition(p_l)

    while are_horizontal_busy():
        continue

    if num_right > 0:
        RIGHT_VERTICAL_STEPPER.startGoToPosition(LIFT_DISTANCE)
    if num_left > 0:
        LEFT_VERTICAL_STEPPER.startGoToPosition(LIFT_DISTANCE)

    while are_vertical_busy():
        continue

    if num_right > 0:
        RIGHT_HORIZONTAL_STEPPER.startRelativeMove(BACKUP_DISTANCE)
    if num_left > 0:
        LEFT_HORIZONTAL_STEPPER.startRelativeMove(BACKUP_DISTANCE)

    while are_horizontal_busy():
        continue


def release_both():
    """
    Release both of the vertical steppers
    :return: None
    """
    set_vertical_pos(0)


def stop_balls():
    """
    Stop the balls movement, by bringing horiz. steppers out the uo to stop all balls
    :return: None
    """
    # move vertical steppers up
    set_vertical_pos(LIFT_DISTANCE)

    # slowly move the horizontal steppers into the middle/stopping positions
    set_horizontal_speed(STOPPING_SPEED)
    set_horizontal_poss(STOP_DISTANCE_LEFT, STOP_DISTANCE_RIGHT)

    # back away slowly
    set_horizontal_speed(STOPPING_SPEED / 10)
    set_horizontal_pos_rel(-1)

    set_horizontal_speed(STOPPING_SPEED / 5)
    set_horizontal_pos_rel(-4)

    # bring the vertical steppers down
    set_vertical_pos(0)


"""
PauseScene functions
"""


def pause(text, sec):
    """
    Pause the screen for a set amount of time
    :param text: Text to display while the pause screen is visible
    :param sec: Number of seconds to pause the screen for
    :return: None
    """
    sm.transition.direction = 'left'
    sm.current = 'pauseScene'
    sm.current_screen.ids.pauseText.text = text
    load = Animation(size=(10, 10), duration=0) + \
           Animation(size=(150, 10), duration=sec)
    load.start(sm.current_screen.ids.progressBar)


def transition_back(original_scene):
    """
    Transition back to the previous scene
    :param original_scene: The previous scene to transition back to
    :return: None
    """
    sm.transition.direction = 'right'
    sm.current = original_scene


def scoop_balls_thread(*largs):
    if sm.current != "main":
        return

    main = sm.get_screen('main')

    num_left = main.cradle.num_left()
    num_right = main.cradle.num_right()

    if num_right == 0 and num_left == 0:
        return

    pause_time = 5 + 26 + 2 * max(num_left, num_right)
    main.pause(pause_time)

    Thread(target=new_scoop).start()


sm = ScreenManager()


class Ball(Widget):
    down_exists = False
    down = ObjectProperty((0, 0))

    def transform_point(self, v):
        v -= Vector(self.parent.pos)
        v = v.rotate(-self.parent.rotation)
        v += Vector(self.parent.pos)
        return v

    def clear(self):
        self.down = (0, 0)
        Ball.down_exists = False

    def pushed(self, touch):
        pos = touch.pos
        v = self.transform_point(Vector(pos))

        if self.collide_point(v.x, v.y) and not Ball.down_exists:
            self.down = v
            Ball.down_exists = True

    def moved(self, touch):
        p = self.parent
        pos = touch.pos
        v = self.transform_point(Vector(pos))

        if self.down != (0, 0):
            d = v - Vector(self.down)
            if d.length() >= GESTURE_MAX_DELTA:
                if d.x >= GESTURE_MIN_DELTA:
                    self.parent.parent.ball_right(p)
                    self.clear()
                elif d.x <= -GESTURE_MIN_DELTA:
                    self.parent.parent.ball_left(p)
                    self.clear()

    def released(self, touch):
        p = self.parent
        pos = touch.pos
        v = self.transform_point(Vector(pos))

        if self.down != (0, 0):
            d = v - Vector(self.down)
            if d.x >= GESTURE_MIN_DELTA:
                self.parent.parent.ball_right(p)
                self.clear()
                return
            elif d.x <= -GESTURE_MIN_DELTA:
                self.parent.parent.ball_left(p)
                self.clear()
            self.parent.parent.ball_touched(p)
            self.clear()


class BallString(Widget):
    rotation = ObjectProperty(0)
    ball = ObjectProperty(None)
    name = ObjectProperty("middle")
    ROT_LEFT = -35
    ROT_RIGHT = 35
    ROT_DOWN = 0
    a_down = Animation(rotation=ROT_DOWN, t="out_quad")
    a_left = Animation(rotation=ROT_LEFT, t="out_quad")
    a_right = Animation(rotation=ROT_RIGHT, t="out_quad")
    r = ObjectProperty(ROT_DOWN)

    def down(self):
        Animation.cancel_all(self)
        BallString.a_down.start(self)
        self.r = BallString.ROT_DOWN

    def left(self):
        Animation.cancel_all(self)
        BallString.a_left.start(self)
        self.r = BallString.ROT_LEFT

    def right(self):
        Animation.cancel_all(self)
        BallString.a_right.start(self)
        self.r = BallString.ROT_RIGHT


class Cradle(Widget):
    def num_left(self):
        return sum(ball.r == BallString.ROT_LEFT for ball in self.get_balls())

    def num_right(self):
        return sum(ball.r == BallString.ROT_RIGHT for ball in self.get_balls())

    def get_balls(self):
        return self.children

    def ball_right(self, ball_string):
        if ball_string.r == BallString.ROT_LEFT:
            self.ball_down(ball_string)
            return
        balls = self.get_balls()[::-1]
        i = balls.index(ball_string)
        for ball in balls[i:]:
            if ball.name == "left":
                ball.down()
            else:
                ball.right()
        sm.get_screen("main").update_button()

    def ball_left(self, ball_string):
        if ball_string.r == BallString.ROT_RIGHT:
            self.ball_down(ball_string)
            return
        balls = self.get_balls()
        i = balls.index(ball_string)
        for ball in balls[i:]:
            if ball.name == "right":
                ball.down()
            else:
                ball.left()
        sm.get_screen("main").update_button()

    def ball_down(self, ball_string):
        if ball_string.r == BallString.ROT_LEFT:
            balls = self.get_balls()[::-1]
            i = balls.index(ball_string)
            for ball in balls[i:]:
                if ball.r != BallString.ROT_LEFT:
                    break
                ball.down()
        elif ball_string.r == BallString.ROT_RIGHT:
            balls = self.get_balls()
            i = balls.index(ball_string)
            for ball in balls[i:]:
                if ball.r != BallString.ROT_RIGHT:
                    break
                ball.down()
        sm.get_screen("main").update_button()

    def ball_touched(self, ball_string):
        if ball_string.r == BallString.ROT_DOWN:
            if ball_string.name == "left":
                self.ball_left(ball_string)
            elif ball_string.name == "middle-left":
                self.ball_left(ball_string)
            elif ball_string.name == "middle":
                self.ball_right(ball_string)
            elif ball_string.name == "middle-right":
                self.ball_right(ball_string)
            elif ball_string.name == "right":
                self.ball_right(ball_string)
        else:
            self.ball_down(ball_string)
        sm.get_screen("main").update_button()


class MyApp(App):
    def build(self):
        """
        Called upon launching application
        :return: Screen Manager
        """
        return sm


Builder.load_file('Kivy/Scenes/main.kv')
Builder.load_file('Kivy/Libraries/DPEAButton.kv')
Builder.load_file('Kivy/Scenes/PauseScene.kv')
Builder.load_file('Kivy/Scenes/AdminScreen.kv')
Window.clearcolor = (1, 1, 1, 1)  # (WHITE)

"""
MainScreen Class
"""


class MainScreen(Screen):
    cradle = ObjectProperty(None)
    execute = ObjectProperty(None)
    hint = ObjectProperty(None)

    fade_out = Animation(opacity=0, t="out_quad")
    fade_in = Animation(opacity=1, t="out_quad")

    @staticmethod
    def admin_action():
        sm.current = 'admin'

    def scoop_call_back(self):
        Clock.schedule_once(scoop_balls_thread, 0)

    def set_visible(self, widget):
        print("set_visible", widget)
        if self.is_paused:
            return

        Animation.cancel_all(self.hint)
        Animation.cancel_all(self.execute)
        Animation.cancel_all(self.progress)

        MainScreen.fade_out.start(self.hint)
        MainScreen.fade_out.start(self.execute)
        MainScreen.fade_out.start(self.progress)

        Animation.cancel_all(widget)
        MainScreen.fade_in.start(widget)

    def pause(self, delay):
        # this is run in another thread so we can delay
        self.set_visible(self.progress)
        self.is_paused = True
        self.progress.value = 0
        a = Animation(value=100, duration=delay)
        a.start(self.progress)

    def unpause(self):
        self.is_paused = False
        self.set_visible(self.hint)

    def update_button(self):
        l = self.cradle.num_left()
        r = self.cradle.num_right()

        if l == 0 and r == 0:
            self.set_visible(self.hint)
        else:
            self.set_visible(self.execute)


class MyProgressBar(Widget):
    def __init__(self, **kwargs):
        self._value = 0.
        super(MyProgressBar, self).__init__(**kwargs)

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        value = max(0, min(self.max, value))
        if value != self._value:
            self._value = value
            return True

    value = AliasProperty(_get_value, _set_value)

    def get_norm_value(self):
        d = self.max
        if d == 0:
            return 0
        return self.value / float(d)

    def set_norm_value(self, value):
        self.value = value * self.max

    value_normalized = AliasProperty(get_norm_value, set_norm_value,
                                     bind=('value', 'max'))

    max = NumericProperty(100.)

# ////////////////////////////////////////////////////////////////
# //        PauseScene and Admin Scene Class                    //
# ////////////////////////////////////////////////////////////////


class adminFunctionsScreen(Screen):
    @staticmethod
    def quit_action():
        quit_all()

    @staticmethod
    def back_action(self):
        home()
        sm.current = 'main'


sm.add_widget(MainScreen(name='main'))
sm.add_widget(AdminScreen.AdminScreen(name='admin'))
sm.add_widget(adminFunctionsScreen(name='adminFunctionsScreen'))

mixpanel = MixPanel("Newtons Cradle", MIXPANEL_TOKEN)

temperature_refresh = BackgroundScheduler()
temperature_refresh.add_job(check_temperature(), 'interval', minutes=5)

if __name__ == "__main__":
    try:
        home()
        mixpanel.setEventName("Project Initialized")
        mixpanel.sendEvent()
        temperature_refresh.start()
        MyApp().run()
    except KeyboardInterrupt:
        quit_all()
