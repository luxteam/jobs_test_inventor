import os
import sys
from time import sleep
import pyautogui
import win32gui

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))
import utils


def open_converted_scene(args, case, current_try, screens_path, extension = ".usd"):
    scene_name = os.path.split(case["scene"].replace(".iam", extension))[1]
    scene_path = os.path.join(args.res_path, "..", "..", "Temp", scene_name)
    utils.case_logger.info("Converted scene path: {}".format(scene_path))
    abs_scene_path = os.path.abspath(os.path.join(args.res_path, "..", "..", "Temp", scene_name))
    utils.open_scene_usdviewer(args, case, current_try, abs_scene_path, screens_path)


def open_usdviewer_console(args, case, current_try, screens_path, extension = ".usd"):
    scene_name = os.path.split(case["scene"].replace(".iam", extension))[1]
    scene_path = os.path.join(args.res_path, "..", "..", "Temp", scene_name)
    utils.case_logger.info("Converted scene path: {}".format(scene_path))
    abs_scene_path = os.path.abspath(os.path.join(args.res_path, "..", "..", "Temp", scene_name))
    utils.open_usdviewer_console(args, case, current_try, scene_path, screens_path)


def start_assemble_creation(args, case, current_try, screens_path):
    # Click "Assemble" button in main window
    utils.case_logger.info("Start assemble creation")
    assemble_button_x = 370
    assemble_button_y = 430
    utils.move_and_click(args, case, current_try, assemble_button_x, assemble_button_y, "assemble_button", screens_path, 15)


def create_part(args, case, current_try, screens_path):
    # Click "Create" button in assemble tool bar
    utils.case_logger.info("Create part")
    create_button_x = 100
    create_button_y = 120
    utils.move_and_click(args, case, current_try, create_button_x, create_button_y, "create_button", screens_path)

    # Press "Ok" button (press enter button)
    pyautogui.press("enter")

    # Click on empty viewport
    empty_viewport_x = 1000
    empty_viewport_y = 600
    utils.move_and_click(args, case, current_try, empty_viewport_x, empty_viewport_y, "empty_viewport", screens_path)


def create_sketch(args, case, current_try, screens_path):
    utils.case_logger.info("Create sketch")
    # Click "Create 2d sketch" button
    create_sketch_button_x = 155
    create_sketch_button_y = 125
    utils.move_and_click(args, case, current_try, create_sketch_button_x, create_sketch_button_y, "create_sketch_button", screens_path)

    # Select plane by click
    plane_x = 970
    plane_y = 385
    utils.move_and_click(args, case, current_try, plane_x, plane_y, "plane", screens_path, 3)

    # Click "Circle" button
    circle_button_x = 230
    circle_button_y = 105
    utils.move_and_click(args, case, current_try, circle_button_x, circle_button_y, "circle_button", screens_path, 3)

    # Create circle
    circle_button_x = 1061
    circle_button_y = 582
    utils.moveTo(circle_button_x, circle_button_y)
    sleep(1)
    pyautogui.click()
    sleep(1)
    # Set circle radious by mouse movement
    utils.moveTo(circle_button_x + 30, circle_button_y)
    sleep(1)
    pyautogui.click()
    sleep(1)
    utils.make_screen(screens_path, "circle_created_clicked_{}_try_{}.jpg".format(case["case"], current_try))

    # Click "Finish" button
    finish_button_x = 1715
    finish_button_y = 120
    utils.move_and_click(args, case, current_try, finish_button_x, finish_button_y, "finish_button", screens_path)


def do_extrude(args, case, current_try, screens_path):
    utils.case_logger.info("Do extrude")
    # Click "Extrude" button
    extrude_button_x = 155
    extrude_button_y = 120
    utils.move_and_click(args, case, current_try, extrude_button_x, extrude_button_y, "extrude_button", screens_path)

    # Press "Ok" button (press enter button)
    pyautogui.press("enter")

    # Click "Return" button
    return_button_x = 1875
    return_button_y = 120
    utils.move_and_click(args, case, current_try, return_button_x, return_button_y, "return_button", screens_path)


def move_part(args, case, current_try, screens_path):
    utils.case_logger.info("Move part")
    utils.open_inventor_tab(args, case, current_try, "assemble", screens_path)

    # Click "Extrude" button
    move_part_button_x = 220
    move_part_button_y = 95
    utils.move_and_click(args, case, current_try, move_part_button_x, move_part_button_y, "move_part_button", screens_path)

    # Move detail
    detail_x = 930
    detail_y = 645
    utils.moveTo(detail_x, detail_y)
    sleep(1)
    pyautogui.mouseDown()
    sleep(1)
    # Move detail a bit
    utils.moveTo(detail_x - 150, detail_y)
    sleep(1)
    pyautogui.mouseUp()
    utils.make_screen(screens_path, "detail_moved_{}_try_{}.jpg".format(case["case"], current_try))


def save_temp_image(args, case, current_try, screens_path):
    utils.case_logger.info("Save and check temp image")
    image_path = os.path.abspath(os.path.join(args.res_path, "..", "..", "Temp", "RESULT.jpg"))
    utils.save_image(args, case, current_try, image_path, screens_path)

    if not os.path.exists(image_path):
        raise Exception("USD Viewer doesn't work after closing of scene")


def select_pool_bottom_part(args, case, current_try, screens_path):
    # Select bottom part of Pool scene by click
    utils.case_logger.info("Select bottom part of Pool scene")
    inventor_window_rect = utils.get_window_rect(win32gui.FindWindow(None, "{}".format(args.tool_name)))
    select_part_x = 1300
    select_part_y = inventor_window_rect[3] - 30
    utils.move_and_click(args, case, current_try, select_part_x, select_part_y, "select_part", screens_path)
