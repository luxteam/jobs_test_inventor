import os
import sys

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))
from utils import *


def open_converted_scene(args, case, current_try, screens_path, extension = ".usd"):
    scene_name = os.path.split(case["scene"].replace(".iam", extension))[1]
    scene_path = os.path.abspath(os.path.join(args.res_path, "..", "..", "Temp", scene_name))
    open_scene_usdviewer(args, case, current_try, scene_path, screens_path)


def open_usdviewer_console(args, case, current_try, screens_path, extension = ".usd"):
    scene_name = os.path.split(case["scene"].replace(".iam", extension))[1]
    scene_path = os.path.abspath(os.path.join(args.res_path, "..", "..", "Temp", scene_name))
    open_usdviewer_console(args, case, current_try, scene_path, screens_path)


def start_assemble_creation(args, case, current_try, screens_path):
    # Click "Assemble" button in main window
    assemble_button_x = 370
    assemble_button_y = 430
    moveTo(assemble_button_x, assemble_button_y)
    sleep(1)
    make_screen(screens_path, "before_start_assemble_creation_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    # Wait a bit
    sleep(15)
    make_screen(screens_path, "after_start_assemble_creation_{}_try_{}.jpg".format(case["case"], current_try))


def create_part(args, case, current_try, screens_path):
    # Click "Create" button in assemble tool bar
    create_button_x = 100
    create_button_y = 120
    moveTo(create_button_x, create_button_y)
    sleep(1)
    make_screen(screens_path, "before_click_create_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(1)
    make_screen(screens_path, "after_click_create_{}_try_{}.jpg".format(case["case"], current_try))

    # Click "Ok" button to create new part
    ok_button_x = 755
    ok_button_y = 540
    moveTo(ok_button_x, ok_button_y)
    sleep(1)
    make_screen(screens_path, "before_ok_clicked_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(5)
    make_screen(screens_path, "after_ok_clicked_{}_try_{}.jpg".format(case["case"], current_try))

    # Click on empty viewport
    empty_viewport_x = 1000
    empty_viewport_y = 600
    moveTo(empty_viewport_x, empty_viewport_y)
    sleep(1)
    make_screen(screens_path, "before_viewport_clicked_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(1)
    make_screen(screens_path, "after_viewport_clicked_{}_try_{}.jpg".format(case["case"], current_try))


def create_sketch(args, case, current_try, screens_path):
    # Click "Create 2d sketch" button
    create_sketch_button_x = 155
    create_sketch_button_y = 125
    moveTo(create_sketch_button_x, create_sketch_button_y)
    sleep(1)
    make_screen(screens_path, "before_sketch_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(1)
    make_screen(screens_path, "after_sketch_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))

    # Select plane by click
    plane_x = 970
    plane_y = 385
    moveTo(plane_x, plane_y)
    sleep(1)
    make_screen(screens_path, "before_select_plane_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(3)
    make_screen(screens_path, "after_select_plane_{}_try_{}.jpg".format(case["case"], current_try))

    # Click "Circle" button
    circle_button_x = 230
    circle_button_y = 105
    moveTo(circle_button_x, circle_button_y)
    sleep(1)
    make_screen(screens_path, "before_circle_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(1)
    make_screen(screens_path, "after_circle_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))

    # Create circle
    circle_button_x = 1061
    circle_button_y = 582
    moveTo(circle_button_x, circle_button_y)
    sleep(1)
    pyautogui.click()
    sleep(1)
    # Set circle radious by mouse movement
    moveTo(circle_button_x + 30, circle_button_y)
    sleep(1)
    pyautogui.click()
    sleep(1)
    make_screen(screens_path, "circle_created_clicked_{}_try_{}.jpg".format(case["case"], current_try))

    # Click "Finish" button
    finish_button_x = 1715
    finish_button_y = 120
    moveTo(finish_button_x, finish_button_y)
    sleep(1)
    make_screen(screens_path, "before_finish_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(1)
    make_screen(screens_path, "after_finish_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))


def do_extrude(args, case, current_try, screens_path):
    # Click "Extrude" button
    extrude_button_x = 155
    extrude_button_y = 120
    moveTo(extrude_button_x, extrude_button_y)
    sleep(1)
    make_screen(screens_path, "before_extrude_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(1)
    make_screen(screens_path, "after_extrude_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))

    # Click "Ok" button
    ok_button_x = 315
    ok_button_y = 550
    moveTo(ok_button_x, ok_button_y)
    sleep(1)
    make_screen(screens_path, "before_ok_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(1)
    make_screen(screens_path, "after_ok_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))

    # Click "Return" button
    return_button_x = 1875
    return_button_y = 120
    moveTo(return_button_x, return_button_y)
    sleep(1)
    make_screen(screens_path, "before_return_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))
    pyautogui.click()
    sleep(1)
    make_screen(screens_path, "after_return_button_clicked_{}_try_{}.jpg".format(case["case"], current_try))
