#!/usr/bin/python3

import sys

from kivy.properties import ObjectProperty

sys.path.insert(0, 'Kivy/')
sys.path.insert(0, 'Kivy/Scenes/')
sys.path.insert(0, 'Libraries')
sys.path.insert(0, '/usr/local/lib/python2.7/dist-packages')

import time
from threading import Thread
from kivy.animation import Animation
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color
from kivy.vector import Vector
import AdminScreen
import Stepper

# ////////////////////////////////////////////////////////////////
# //                       MAIN VARIABLES                       //
# ////////////////////////////////////////////////////////////////

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

RIGHT_HORIZONTAL_STEPPER = Stepper.Stepper(port=0, microSteps=MICRO_STEPS_HORIZONTAL, stepsPerUnit=STEPS_PER_UNIT, speed=HORIZONTAL_SPEED, accel=ACCELERATION)
RIGHT_VERTICAL_STEPPER = Stepper.Stepper(port=1, microSteps=MICRO_STEPS_VERTICAL, speed=VERTICAL_SPEED, accel=ACCELERATION)

LEFT_HORIZONTAL_STEPPER = Stepper.Stepper(port=2, microSteps=MICRO_STEPS_HORIZONTAL, stepsPerUnit=STEPS_PER_UNIT, speed=HORIZONTAL_SPEED, accel=ACCELERATION)
LEFT_VERTICAL_STEPPER = Stepper.Stepper(port=3, microSteps=MICRO_STEPS_VERTICAL, speed=VERTICAL_SPEED, accel=ACCELERATION)


GESTURE_MIN_DELTA = 25
GESTURE_MAX_DELTA = 75


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# ////////////////////////////////////////////////////////////////
def quit_all():
    RIGHT_HORIZONTAL_STEPPER.free()
    RIGHT_VERTICAL_STEPPER.free()
    LEFT_VERTICAL_STEPPER.free()
    LEFT_HORIZONTAL_STEPPER.free()
    quit()


def are_horizontal_busy():
    return RIGHT_HORIZONTAL_STEPPER.isBusy() or LEFT_HORIZONTAL_STEPPER.isBusy()


def are_vertical_busy():
    return RIGHT_VERTICAL_STEPPER.isBusy() or LEFT_VERTICAL_STEPPER.isBusy()


def set_vertical_speed(speed):
    LEFT_VERTICAL_STEPPER.setSpeed(speed)
    RIGHT_VERTICAL_STEPPER.setSpeed(speed)


def set_horizontal_speed(speed):
    LEFT_HORIZONTAL_STEPPER.setSpeed(speed)
    RIGHT_HORIZONTAL_STEPPER.setSpeed(speed)


def set_vertical_pos(pos):
    RIGHT_VERTICAL_STEPPER.startGoToPosition(pos)
    LEFT_VERTICAL_STEPPER.startGoToPosition(pos)

    while are_vertical_busy():
        continue


def set_vertical_poss(pos_l, pos_r):
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
    LEFT_HORIZONTAL_STEPPER.startGoToPosition(pos)
    RIGHT_HORIZONTAL_STEPPER.startGoToPosition(pos)

    while are_horizontal_busy():
        continue


def set_horizontal_poss(pos_l, pos_r):
    LEFT_HORIZONTAL_STEPPER.startGoToPosition(pos_l)
    RIGHT_HORIZONTAL_STEPPER.startGoToPosition(pos_r)

    while are_horizontal_busy():
        continue


def set_horizontal_pos_rel(r):
    LEFT_HORIZONTAL_STEPPER.startRelativeMove(r)
    RIGHT_HORIZONTAL_STEPPER.startRelativeMove(r)

    while are_horizontal_busy():
        continue


def home():
    LEFT_VERTICAL_STEPPER.home(0)
    RIGHT_VERTICAL_STEPPER.home(0)
    LEFT_HORIZONTAL_STEPPER.home(0)
    RIGHT_HORIZONTAL_STEPPER.home(0)


def new_scoop():
    num_left = sm.get_screen('main').cradle.num_left()
    num_right = sm.get_screen('main').cradle.num_right()

    if num_left + num_right == 0:
        return

    # stop balls
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
    # release
    release_both()

    home()

    time.sleep(30)

    transition_back('main')


# does not wait for last move to complete
def scoop_left(num):
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


# does not wait for last move to complete
def scoop_right(num):
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
    set_vertical_pos(0)


def stop_balls():
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


# ////////////////////////////////////////////////////////////////
# //             Pause and Admin Scene Functions                //
# ////////////////////////////////////////////////////////////////
def pause(text, sec):
    sm.transition.direction = 'left'
    sm.current = 'pauseScene'
    sm.current_screen.ids.pauseText.text = text
    load = Animation(size=(10, 10), duration=0) + \
           Animation(size=(150, 10), duration=sec)
    load.start(sm.current_screen.ids.progressBar)


def transition_back(original_scene, *larg):
    sm.transition.direction = 'right'
    sm.current = original_scene


# ////////////////////////////////////////////////////////////////
# //                       Threading                            //
# ////////////////////////////////////////////////////////////////
def scoop_balls_thread(*largs):
    if sm.current != "main":
        return

    num_left = sm.get_screen('main').cradle.num_left()
    num_right = sm.get_screen('main').cradle.num_right()

    if num_right == 0 and num_left == 0:
        return

    pause_time = 30 + 26 + 2 * max(num_left, num_right)

    pause('Please wait...', pause_time)
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
        return sm


Builder.load_file('Kivy/Scenes/main.kv')
Builder.load_file('Kivy/Libraries/DPEAButton.kv')
Builder.load_file('Kivy/Scenes/PauseScene.kv')
Builder.load_file('Kivy/Scenes/AdminScreen.kv')
Window.clearcolor = (1, 1, 1, 1)  # (WHITE)


# ////////////////////////////////////////////////////////////////
# //        MainScreen Class                                    //
# ////////////////////////////////////////////////////////////////    
class MainScreen(Screen):
    cradle = ObjectProperty(None)
    execute = ObjectProperty(None)
    hint = ObjectProperty(None)

    fade_out = Animation(opacity=0, t="out_quad")
    fade_in = Animation(opacity=1, t="out_quad")

    def admin_action(self):
        sm.current = 'admin'

    def scoop_call_back(self):
        Clock.schedule_once(scoop_balls_thread, 0)

    def update_button(self):
        l = self.cradle.num_left()
        r = self.cradle.num_right()
        button = self.execute
        label = self.hint

        Animation.cancel_all(label)
        Animation.cancel_all(button)

        if l == 0 and r == 0:
            MainScreen.fade_in.start(label)
            MainScreen.fade_out.start(button)
        else:
            MainScreen.fade_in.start(button)
            MainScreen.fade_out.start(label)


# ////////////////////////////////////////////////////////////////
# //        PauseScene and Admin Scene Class                    //
# ////////////////////////////////////////////////////////////////
class PauseScene(Screen):
    pass


class adminFunctionsScreen(Screen):
    def quit_action(self):
        quit_all()

    def backAction(self):
        home()

        sm.current = 'main'


sm.add_widget(MainScreen(name='main'))
sm.add_widget(PauseScene(name='pauseScene'))
sm.add_widget(AdminScreen.AdminScreen(name='admin'))
sm.add_widget(adminFunctionsScreen(name='adminFunctionsScreen'))

if __name__ == "__main__":
    home()
    MyApp().run()
    quit_all()
