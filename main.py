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
dist_back = 5 * 25.4 + 50
dist_up = 3.2 * 25.4

prerelease_pos = dist_up - 18

stop_dist_left = 2.41 * 25.4 - 1
stop_dist_right = 2.41 * 25.4 + 4

backup_dist = -120

left_start_position = stop_dist_left - 10
right_start_position = stop_dist_right - 10

ball_diameter = 2.25 * 25.4

lift_speed = 40
drop_speed = 800

stopping_speed = 7.5
horizontal_speed = 36

accel = 45

right_horizontal_stepper = Stepper.Stepper(port=0, microSteps=16,
                                           stepsPerUnit=25, speed=horizontal_speed, accel=accel)
right_vertical_stepper = Stepper.Stepper(port=1, microSteps=8,
                                         speed=lift_speed, accel=accel)

left_horizontal_stepper = Stepper.Stepper(port=2, microSteps=16,
                                          stepsPerUnit=25, speed=horizontal_speed, accel=accel)
left_vertical_stepper = Stepper.Stepper(port=3, microSteps=8,
                                        speed=lift_speed, accel=accel)


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# ////////////////////////////////////////////////////////////////
def quit_all():
    right_horizontal_stepper.free()
    right_vertical_stepper.free()
    left_vertical_stepper.free()
    left_horizontal_stepper.free()
    quit()


def are_horizontal_busy():
    return right_horizontal_stepper.isBusy() or left_horizontal_stepper.isBusy()


def are_vertical_busy():
    return right_vertical_stepper.isBusy() or left_vertical_stepper.isBusy()


def set_vertical_speed(speed):
    left_vertical_stepper.setSpeed(speed)
    right_vertical_stepper.setSpeed(speed)


def set_horizontal_speed(speed):
    left_horizontal_stepper.setSpeed(speed)
    right_horizontal_stepper.setSpeed(speed)


def set_vertical_pos(pos):
    right_vertical_stepper.startGoToPosition(pos)
    left_vertical_stepper.startGoToPosition(pos)

    while are_vertical_busy():
        continue


def set_vertical_poss(pos_l, pos_r):
    left_vertical_stepper.startGoToPosition(pos_l)
    right_vertical_stepper.startGoToPosition(pos_r)

    while are_vertical_busy():
        continue

def set_vertical_pos_rel(r):
    right_vertical_stepper.startRelativeMove(r)
    left_vertical_stepper.startRelativeMove(r)

    while are_vertical_busy():
        continue


def set_horizontal_pos(pos):
    left_horizontal_stepper.startGoToPosition(pos)
    right_horizontal_stepper.startGoToPosition(pos)

    while are_horizontal_busy():
        continue


def set_horizontal_poss(pos_l, pos_r):
    left_horizontal_stepper.startGoToPosition(pos_l)
    right_horizontal_stepper.startGoToPosition(pos_r)

    while are_horizontal_busy():
        continue


def set_horizontal_pos_rel(r):
    left_horizontal_stepper.startRelativeMove(r)
    right_horizontal_stepper.startRelativeMove(r)

    while are_horizontal_busy():
        continue


def home():
    left_vertical_stepper.home(0)
    right_vertical_stepper.home(0)
    left_horizontal_stepper.home(0)
    right_horizontal_stepper.home(0)


def new_scoop():
    num_left = sm.get_screen('main').cradle.num_left()
    num_right = sm.get_screen('main').cradle.num_right()

    if num_left + num_right == 0:
        return

    # stop balls
    stop_balls()

    if num_left + num_right == 5:
        scoop_left(num_left)
        scoop_right(num_right)

        while are_horizontal_busy():
            continue
    else:
        scoop_both(num_left, num_right)

    # release
    release_both()

    home()

    transition_back('main')


# does not wait for last move to complete
def scoop_left(num):
    if num == 0:
        return

    p = left_start_position + ball_diameter * num
    set_horizontal_speed(horizontal_speed)
    left_horizontal_stepper.startGoToPosition(p)

    while are_horizontal_busy():
        continue

    set_vertical_speed(lift_speed)
    left_vertical_stepper.startGoToPosition(dist_up)

    while are_vertical_busy():
        continue

    left_horizontal_stepper.startRelativeMove(backup_dist)


# does not wait for last move to complete
def scoop_right(num):
    if num == 0:
        return

    p = right_start_position + ball_diameter * num
    set_horizontal_speed(horizontal_speed)
    right_horizontal_stepper.startGoToPosition(p)

    while are_horizontal_busy():
        continue

    set_vertical_speed(lift_speed)
    right_vertical_stepper.startGoToPosition(dist_up)

    while are_vertical_busy():
        continue

    right_horizontal_stepper.startRelativeMove(backup_dist)


def scoop_both(num_left, num_right):
    p_r = right_start_position + ball_diameter * num_right
    p_l = left_start_position + ball_diameter * num_left

    set_horizontal_speed(horizontal_speed)
    if num_right > 0:
        right_horizontal_stepper.startGoToPosition(p_r)
    if num_left > 0:
        left_horizontal_stepper.startGoToPosition(p_l)

    while are_horizontal_busy():
        continue

    set_vertical_speed(lift_speed)
    if num_right > 0:
        right_vertical_stepper.startGoToPosition(dist_up)
    if num_left > 0:
        left_vertical_stepper.startGoToPosition(dist_up)

    while are_vertical_busy():
        continue

    if num_right > 0:
        right_horizontal_stepper.startRelativeMove(backup_dist)
    if num_left > 0:
        left_horizontal_stepper.startRelativeMove(backup_dist)

    while are_horizontal_busy():
        continue


def release_both():
    set_vertical_speed(drop_speed)
    set_vertical_pos(0)


def stop_balls():
    # move vertical steppers up
    set_vertical_speed(lift_speed)
    set_vertical_pos(dist_up)

    # slowly move the horizontal steppers into the middle/stopping positions
    set_horizontal_speed(stopping_speed)
    set_horizontal_poss(stop_dist_left, stop_dist_right)

    # back away slowly
    set_horizontal_speed(stopping_speed / 10)
    set_horizontal_pos_rel(-1)

    set_horizontal_speed(stopping_speed / 5)
    set_horizontal_pos_rel(-4)

    # bring the vertical steppers down
    set_vertical_speed(drop_speed)
    set_vertical_pos(0)


# ////////////////////////////////////////////////////////////////
# //             Pause and Admin Scene Functions                //
# ////////////////////////////////////////////////////////////////
def pause(text, sec, original_scene):
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

    pause_time = 26 + 2 * max(num_left, num_right)

    pause('Scooping!', pause_time, 'main')
    Thread(target=new_scoop).start()


# ////////////////////////////////////////////////////////////////
# //                     KIVY FILE LOAD-INS                     //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()


class Ball(Widget):
    down_exists = False
    color = ObjectProperty((0.5, 0.5, 0.5))
    down = ObjectProperty((0, 0))

    def pushed(self, args):
        touch = args[1]
        self = args[0]
        p = self.parent
        pos = touch.pos
        v = Vector(pos)
        v -= Vector(self.parent.pos)
        v = v.rotate(-self.parent.rotation)
        v += Vector(self.parent.pos)

        if self.collide_point(v.x, v.y) and not Ball.down_exists:
            self.color = (0.2, 0.2, 0.2)
            self.down = v
            Ball.down_exists = True

    def moved(self, args):
        touch = args[1]
        self = args[0]
        p = self.parent
        pos = touch.pos
        v = Vector(pos)
        v -= Vector(self.parent.pos)
        v = v.rotate(-self.parent.rotation)
        v += Vector(self.parent.pos)

        if self.down != (0, 0):
            dx = v.x - self.down[0]
            dy = v.y - self.down[1]
            if abs(dx * dx + dy * dy) > 150:
                if dy < -150:
                    self.parent.parent.ball_down(p)
                    self.down = (0, 0)
                    self.color = (0.5, 0.5, 0.5)
                    Ball.down_exists = False
                elif dx > 150:
                    self.parent.parent.ball_right(p)
                    self.down = (0, 0)
                    self.color = (0.5, 0.5, 0.5)
                    Ball.down_exists = False
                elif dx < -150:
                    self.parent.parent.ball_left(p)
                    self.down = (0, 0)
                    self.color = (0.5, 0.5, 0.5)
                    Ball.down_exists = False

    def released(self, args):
        touch = args[1]
        self = args[0]
        p = self.parent
        pos = touch.pos
        v = Vector(pos)
        v -= Vector(self.parent.pos)
        v = v.rotate(-self.parent.rotation)
        v += Vector(self.parent.pos)

        if self.down != (0, 0):
            self.color = (0.5, 0.5, 0.5)
            dx = v.x - self.down[0]
            dy = v.y - self.down[1]
            if dy < -50:
                self.parent.parent.ball_down(p)
            elif dx > 50:
                self.parent.parent.ball_right(p)
            elif dx < -50:
                self.parent.parent.ball_left(p)
            else:
                self.parent.parent.ball_touched(p)
            self.down = (0, 0)
            Ball.down_exists = False


class BallString(Widget):
    rotation = ObjectProperty(0)
    ball = ObjectProperty(None)
    name = ObjectProperty("middle")
    ROT_LEFT = -35
    ROT_RIGHT = 35
    ROT_DOWN = 0
    r = ObjectProperty(ROT_DOWN)


class Cradle(Widget):
    down = Animation(rotation=BallString.ROT_DOWN, t="out_quad")
    left = Animation(rotation=BallString.ROT_LEFT, t="out_quad")
    right = Animation(rotation=BallString.ROT_RIGHT, t="out_quad")

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
        balls = self.get_balls()
        balls = list(reversed(balls))
        i = balls.index(ball_string)
        for ball in balls[i:]:
            if ball.name == "left":
                Animation.cancel_all(ball)
                Cradle.down.start(ball)
                ball.r = BallString.ROT_DOWN
            else:
                Animation.cancel_all(ball)
                Cradle.right.start(ball)
                ball.r = BallString.ROT_RIGHT

    def ball_left(self, ball_string):
        if ball_string.r == BallString.ROT_RIGHT:
            self.ball_down(ball_string)
            return
        balls = self.get_balls()
        i = balls.index(ball_string)
        for ball in balls[i:]:
            if ball.name == "right":
                Animation.cancel_all(ball)
                Cradle.down.start(ball)
                ball.r = BallString.ROT_DOWN
            else:
                Animation.cancel_all(ball)
                Cradle.left.start(ball)
                ball.r = BallString.ROT_LEFT

    def ball_down(self, ball_string):
        if ball_string.r == BallString.ROT_LEFT:
            balls = self.get_balls()
            balls = list(reversed(balls))
            i = balls.index(ball_string)
            for ball in balls[i:]:
                if ball.r != BallString.ROT_LEFT:
                    break
                Animation.cancel_all(ball)
                Cradle.down.start(ball)
                ball.r = BallString.ROT_DOWN
        elif ball_string.r == BallString.ROT_RIGHT:
            balls = self.get_balls()
            balls = balls
            i = balls.index(ball_string)
            for ball in balls[i:]:
                if ball.r != BallString.ROT_RIGHT:
                    break
                Animation.cancel_all(ball)
                Cradle.down.start(ball)
                ball.r = BallString.ROT_DOWN

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


class MyApp(App):
    def build(self):
        return sm


Builder.load_file('Kivy/Scenes/main.kv')
Builder.load_file('Kivy/Scenes/Ball.kv')
Builder.load_file('Kivy/Libraries/DPEAButton.kv')
Builder.load_file('Kivy/Scenes/PauseScene.kv')
Builder.load_file('Kivy/Scenes/AdminScreen.kv')
Window.clearcolor = (1, 1, 1, 1)  # (WHITE)


# ////////////////////////////////////////////////////////////////
# //        MainScreen Class                                    //
# ////////////////////////////////////////////////////////////////    
class MainScreen(Screen):
    cradle = ObjectProperty(None)

    def admin_action(self):
        sm.current = 'admin'

    def scoop_call_back(self):
        Clock.schedule_once(scoop_balls_thread, 0)


# ////////////////////////////////////////////////////////////////
# //        PauseScene and Admin Scene Class                    //
# ////////////////////////////////////////////////////////////////
class PauseScene(Screen):
    pass


class adminFunctionsScreen(Screen):
    def quit_action(self):
        quit_all()

    def home_action(self):
        home()

        while are_horizontal_busy() or are_vertical_busy():
            continue
        sm.current = 'main'


sm.add_widget(MainScreen(name='main'))
sm.add_widget(PauseScene(name='pauseScene'))
sm.add_widget(AdminScreen.AdminScreen(name='admin'))
sm.add_widget(adminFunctionsScreen(name='adminFunctionsScreen'))

if __name__ == "__main__":
    home()
    MyApp().run()
    quit_all()
