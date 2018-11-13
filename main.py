#!/usr/bin/python3

import sys
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
import AdminScreen
import Stepper

# ////////////////////////////////////////////////////////////////
# //                       MAIN VARIABLES                       //
# ////////////////////////////////////////////////////////////////
dist_back = 5 * 25.4 + 50
dist_up = 3.2 * 25.4

stop_dist_left = 2.41 * 25.4 - 0.25
stop_dist_right = 2.41 * 25.4

left_start_position = stop_dist_left - 5
right_start_position = stop_dist_right - 5

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


def check_horizontal_steppers_if_busy():
    if right_horizontal_stepper.isBusy() or left_horizontal_stepper.isBusy():
        return True
    else:
        return False


def check_vertical_steppers_if_busy():
    if right_vertical_stepper.isBusy() or left_vertical_stepper.isBusy():
        return True
    else:
        return False


def change_vertical_steppers_speed(speed):
    left_vertical_stepper.setSpeed(speed)
    right_vertical_stepper.setSpeed(speed)


def change_horizontal_steppers_speed(speed):
    left_horizontal_stepper.setSpeed(speed)
    right_horizontal_stepper.setSpeed(speed)


def release_balls():
    change_vertical_steppers_speed(drop_speed)

    left_vertical_stepper.startGoToPosition(0)
    right_vertical_stepper.startGoToPosition(0)

    while check_vertical_steppers_if_busy():
        continue


def pickup_balls(stopping_balls=False):
    change_vertical_steppers_speed(lift_speed)

    if sm.get_screen('main').num_balls_left != 0 or stopping_balls:
        left_vertical_stepper.startRelativeMove(dist_up)
    if sm.get_screen('main').num_balls_right != 0 or stopping_balls:
        right_vertical_stepper.startRelativeMove(dist_up)

    while check_vertical_steppers_if_busy():
        continue
    return


def slow_move_down_to_drop():
    num_balls_left = sm.get_screen('main').num_balls_left
    num_balls_right = sm.get_screen('main').num_balls_right

    change_vertical_steppers_speed(10)
    time.sleep(0.1)  # ensure speed was changed

    if num_balls_right > 0:
        right_vertical_stepper.startRelativeMove(-30)

    if num_balls_left > 0:
        left_vertical_stepper.startRelativeMove(-30)

    while check_vertical_steppers_if_busy():
        continue

    time.sleep(1)

    release_balls()
    return


def get_back_up_distance(right_distance=True):
    num_balls_left = sm.get_screen('main').num_balls_left
    num_balls_right = sm.get_screen('main').num_balls_right
    back_up_dist_right = 0
    back_up_dist_left = 0

    # Change pick up distances for right side
    if num_balls_left == 0 and num_balls_right == 0:
        return 0
    elif num_balls_right == 1:
        back_up_dist_right = dist_back
    elif num_balls_right == 2:
        back_up_dist_right = dist_back - 25
    elif num_balls_right == 3:
        back_up_dist_right = dist_back - 50
    else:
        back_up_dist_right = dist_back - 75

    # Change pick up distances for left side
    if num_balls_left == 0:
        back_up_dist_left = 0
    elif num_balls_left == 1:
        back_up_dist_left = dist_back
    elif num_balls_left == 2:
        back_up_dist_left = dist_back - 25
    elif num_balls_left == 3:
        back_up_dist_left = dist_back - 50
    else:
        back_up_dist_left = dist_back - 75

    # if num_balls_left != 0 and

    return -min(back_up_dist_left, back_up_dist_right) / 2


def move_steppers_back_to_drop(five_balls=False):
    num_balls_left = sm.get_screen('main').num_balls_left
    num_balls_right = sm.get_screen('main').num_balls_right

    if five_balls:
        pass
    else:  # if we are not scooping five balls
        d = -dist_back / 2
        if num_balls_left > 0 and num_balls_right > 0:
            right_horizontal_stepper.startRelativeMove(d)
            left_horizontal_stepper.startRelativeMove(d)
        elif num_balls_right > 0:
            right_horizontal_stepper.startRelativeMove(d)

        elif num_balls_left > 0:
            left_horizontal_stepper.startRelativeMove(d)

    while check_horizontal_steppers_if_busy():
        continue

    return


def move_steppers_to_zero():
    left_horizontal_stepper.home(0)
    right_horizontal_stepper.home(0)

    while check_horizontal_steppers_if_busy():
        continue


def move_steppers_to_pickup_positions(dist_right, dist_left):
    right_horizontal_stepper.startGoToPosition(dist_right)
    left_horizontal_stepper.startGoToPosition(dist_left)

    while check_horizontal_steppers_if_busy():
        continue


def move_steppers_to_stop():
    change_horizontal_steppers_speed(stopping_speed)

    left_horizontal_stepper.startGoToPosition(stop_dist_left)
    right_horizontal_stepper.startGoToPosition(stop_dist_right)

    while check_horizontal_steppers_if_busy():
        continue

    change_horizontal_steppers_speed(horizontal_speed)


def reset_all_widgets():
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
    sm.get_screen('main').change_image_colors()


def scoop_exit_tasks():
    reset_all_widgets()
    transition_back('main')


def home():
    left_vertical_stepper.home(0)
    right_vertical_stepper.home(0)
    left_horizontal_stepper.home(0)
    right_horizontal_stepper.home(0)


def scoop():
    # distances to move when picking up balls
    num_left = sm.get_screen('main').num_balls_left
    num_right = sm.get_screen('main').num_balls_right

    if num_left + num_right == 0:
        transition_back('main')
        return

    if num_left != 0:
        dist_left = left_start_position + ball_diameter * num_left
    else:
        dist_left = 0

    if num_right != 0:
        dist_right = right_start_position + ball_diameter * num_right
    else:
        dist_right = 0

    while stop_balls():
        continue

    move_steppers_to_pickup_positions(dist_right, dist_left)

    pickup_balls()

    while check_vertical_steppers_if_busy():
        continue

    move_steppers_back_to_drop()

    slow_move_down_to_drop()

    move_steppers_to_zero()

    scoop_exit_tasks()
    return


# scoop five balls needs to do left side movements first then right side
# in order to prevent collisions
def scoop_five_balls():
    while stop_balls():
        continue

    pick_up_dist_right = right_start_position + ball_diameter * sm.get_screen('main').num_balls_right
    pick_up_dist_left = left_start_position + ball_diameter * sm.get_screen('main').num_balls_left

    left_horizontal_stepper.goToPosition(pick_up_dist_left)

    change_vertical_steppers_speed(lift_speed)
    left_vertical_stepper.relativeMove(dist_up)

    # move left stepper out and to position
    left_horizontal_stepper.relativeMove(get_back_up_distance(right_distance=False))

    # go to pickup position
    right_horizontal_stepper.goToPosition(pick_up_dist_right)
    right_vertical_stepper.relativeMove(dist_up)

    right_horizontal_stepper.relativeMove(get_back_up_distance())

    # letting go
    slow_move_down_to_drop()

    # move the horizontal steppers back to the starting position
    move_steppers_to_zero()

    scoop_exit_tasks()
    return


def stop_balls():
    # move horizontal steppers to home position
    move_steppers_to_zero()

    # move vertical steppers up
    pickup_balls(True)

    # slowly move the horizontal steppers into the middle/stopping positions
    change_horizontal_steppers_speed(stopping_speed)
    move_steppers_to_stop()

    # bring the vertical steppers down
    time.sleep(3)

    change_horizontal_steppers_speed(stopping_speed / 10)
    right_horizontal_stepper.startRelativeMove(-1)
    left_horizontal_stepper.startRelativeMove(-1)

    while check_horizontal_steppers_if_busy():
        continue

    change_horizontal_steppers_speed(stopping_speed)
    right_horizontal_stepper.startRelativeMove(-5)
    left_horizontal_stepper.startRelativeMove(-5)

    while check_horizontal_steppers_if_busy():
        continue

    change_horizontal_steppers_speed(horizontal_speed)
    release_balls()
    return


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
    reset_all_widgets()
    sm.current = original_scene


# ////////////////////////////////////////////////////////////////
# //                       Threading                            //
# ////////////////////////////////////////////////////////////////
def scoop_balls_thread(*largs):
    num_left = sm.get_screen('main').num_balls_left
    num_right = sm.get_screen('main').num_balls_right
    ball_sum = num_left + num_right

    pause_time = 28 + 2 * (max(num_left, num_right) - 1)

    if sm.current != "main":
        return

    if ball_sum <= 4:
        pause('Scooping!', pause_time, 'main')
        Thread(target=scoop).start()
    else:
        pause_time += 10
        pause('Scooping!', pause_time, 'main')
        Thread(target=scoop_five_balls).start()


# ////////////////////////////////////////////////////////////////
# //                     KIVY FILE LOAD-INS                     //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()


class Ball(Widget):
    def released(self, args):
        touch = args[1]
        self = args[0]
        if self.collide_point(*touch.pos):
            print("Whoa")


class Cradle(Widget):
    pass


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
    num_balls_right = 0
    num_balls_left = 0

    def admin_action(self):
        sm.current = 'admin'

    def scoop_call_back(self):
        Clock.schedule_once(scoop_balls_thread, 0)

    def change_image_colors(self):
        images_list = [self.ids.ballOne, self.ids.ballTwo,
                       self.ids.ballThree, self.ids.ballFour, self.ids.ballFive]

        for index in range(len(images_list)):
            color = 1, 1, 1, 1
            red = 1, 0, 0.050, 1
            blue = 0.062, 0, 1, 1
            if index < self.num_balls_left:
                # change to blue
                color = blue
            elif index >= len(images_list) - self.num_balls_right:
                # change to red
                color = red
            images_list[index].color = color

    def left_scooper_slider_change(self, value):
        self.num_balls_left = int(value)

        if (self.num_balls_left + self.num_balls_right) > 4:
            self.num_balls_right = 5 - self.num_balls_left
            self.ids.rightScooperSlider.value = \
                self.ids.rightScooperSlider.max - self.num_balls_right

        # Check the value of each slider and change the text accordingly
        if self.num_balls_left == 0:
            self.ids.leftScooperLabel.text = "Slide To Control Left Scooper"
        elif self.num_balls_left == 1:
            self.ids.leftScooperLabel.text = \
                str(int(self.num_balls_left)) + " Ball Left Side: Slide To Adjust"
        else:
            self.ids.leftScooperLabel.text = \
                str(int(self.num_balls_left)) + " Balls Left Side: Slide To Adjust"

        self.change_image_colors()

    def right_scooper_slider_change(self, value):
        self.num_balls_right = self.ids.rightScooperSlider.max - int(value)
        if (self.num_balls_left + self.num_balls_right) > 4:
            self.num_balls_left = 5 - self.num_balls_right
            self.ids.leftScooperSlider.value = self.num_balls_left

        # Check the value of each slider and change the text accordingly
        if self.num_balls_right == 0:
            self.ids.rightScooperLabel.text = "Slide To Control Right Scooper"
        elif self.num_balls_right == 1:
            self.ids.rightScooperLabel.text = \
                str(int(self.num_balls_right)) + " Ball Right Side: Slide To Adjust"
        else:
            self.ids.rightScooperLabel.text = \
                str(int(self.num_balls_right)) + " Balls Right Side: Slide To Adjust"

        self.change_image_colors()


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
        reset_all_widgets()

        while check_horizontal_steppers_if_busy() or check_vertical_steppers_if_busy():
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
