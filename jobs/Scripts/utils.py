import win32gui
import win32api
import pyautogui
from time import sleep
from datetime import datetime
import pyscreenshot
import logging
import types
import os
from time import sleep


case_logger = None


def create_case_logger(case, log_path):

    formatter = logging.Formatter(fmt=u'[%(asctime)s] #%(levelname)-6s [F:%(filename)s L:%(lineno)d] >> %(message)s')

    file_handler = logging.FileHandler(filename=os.path.join(log_path, '{}.log'.format(case['case'])), mode='a')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger('{}'.format(case['case']))
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    global case_logger
    case_logger = logger


def is_case_skipped(case, render_platform):
    if case['status'] == 'skipped':
        return True

    return sum([render_platform & set(x) == set(x) for x in case.get('skip_on', '')])


def make_screen(screen_path):
    screen = pyscreenshot.grab()
    screen = screen.convert('RGB')
    screen.save(screen_path)


def moveTo(x, y):
    case_logger.info("Move to x = {}, y = {}".format(x, y))
    pyautogui.moveTo(x, y)


def get_window_rect(window):
    window_rect = win32gui.GetWindowRect(window)

    case_logger.info("Left-top corner position: x = {}, y = {}".format(window_rect[0], window_rect[1]))
    case_logger.info("Bottom-right corner position: x = {}, y = {}".format(window_rect[2], window_rect[3]))

    return window_rect


def find_inventor_window(args):
    inventor_window = None

    start_time = datetime.now()
    # Wait a minute to open Inventor
    while not inventor_window and (datetime.now() - start_time).total_seconds() <= 60:
        inventor_window = win32gui.FindWindow(None, "{}".format(args.tool_name))
        sleep(5)

    return inventor_window


def open_scene(args, case, current_try, screens_path):
    inventor_window_rect = get_window_rect(win32gui.FindWindow(None, "{}".format(args.tool_name)))

    # Open "File" tab
    file_tab_x = 45
    file_tab_y = 55
    moveTo(file_tab_x, file_tab_y)
    sleep(1)
    make_screen(os.path.join(screens_path, "before_choose_scene_{}_try_{}.jpg".format(case["case"], current_try)))
    pyautogui.click()
    sleep(1)

    # Click "Open file" button
    open_file_button_x = 110
    open_file_button_y = 240
    moveTo(open_file_button_x, open_file_button_y)
    sleep(1)
    pyautogui.click()
    sleep(1)
    make_screen(os.path.join(screens_path, "choose_scene_{}_try_{}.jpg".format(case["case"], current_try)))

    # Set scene path
    scene_path = os.path.abspath(os.path.join(args.res_path, case["scene"]))
    case_logger.info("Scene path: {}".format(scene_path))
    pyautogui.press("backspace")
    sleep(1)
    pyautogui.typewrite(scene_path)
    sleep(2)

    # Click "Open" button
    open_button_x = win32api.GetSystemMetrics(0) - 200
    open_button_y = inventor_window_rect[3] - 50
    moveTo(open_button_x, open_button_y)
    sleep(1)
    make_screen(os.path.join(screens_path, "scene_path_{}_try_{}.jpg".format(case["case"], current_try)))
    pyautogui.click()
    sleep(1)


def open_usd_viewer(args, case, current_try, screens_path):
    # Open "Tools" tab
    tools_tab_x = 680
    tools_tab_y = 55
    moveTo(tools_tab_x, tools_tab_y)
    sleep(1)
    pyautogui.click()
    sleep(1)

    # try to open USD Viewer few times
    max_iterations = 5
    iteration = 0
    usd_viewer_window = None

    while iteration < max_iterations:
        iteration += 1
        case_logger.info("Waiting USD Viewer window (try #{})".format(iteration))
        # Open USD Viewer
        usd_viewer_tabs_x = 1430
        usd_viewer_tabs_y = 120
        moveTo(usd_viewer_tabs_x, usd_viewer_tabs_y)
        sleep(1)
        pyautogui.click()
        make_screen(os.path.join(screens_path, "before_{}_try_{}_iteration_{}.jpg".format(case["case"], current_try, iteration)))
        sleep(1)

        start_time = datetime.now()
        # Wait USD Viewer window
        while not usd_viewer_window and (datetime.now() - start_time).total_seconds() <= 30:
            usd_viewer_window = win32gui.FindWindow(None, "tcp://127.0.0.1:1984")
            sleep(1)

        if usd_viewer_window:
            case_logger.info("USD Viewer window was found. Wait cache building (try #{})".format(iteration))
            # TODO check window is ready by window content
            sleep(10)
            make_screen(os.path.join(screens_path, "usd_viewer_found_{}_try_{}.jpg".format(case["case"], current_try)))
            sleep(20)
            break
        else:
            case_logger.info("Waiting USD Viewer window wasn't found (try #{})".format(iteration))
    else:
        case_logger.info("USD Viewer window wasn't found at all")
        raise Exception("USD Viewer window wasn't found at all")


def open_render_tab(args, case, current_try, screens_path):
    # Open Render tab
    left_menu_width = 180
    right_menu_width = 130
    # (window width - left menu width - right menu width) / 2 
    toolbar_center_x = (win32api.GetSystemMetrics(0) - left_menu_width - right_menu_width) / 2
    render_tab_x = left_menu_width + toolbar_center_x + 170
    render_tab_y = 20
    moveTo(render_tab_x, render_tab_y)
    sleep(1)
    pyautogui.click()
    make_screen(os.path.join(screens_path, "usd_viewer_render_tab_{}_try_{}.jpg".format(case["case"], current_try)))
    sleep(1)


def render(args, case, current_try, screens_path):
    # Render
    render_button_x = 345
    render_button_y = 160
    moveTo(render_button_x, render_button_y)
    sleep(1)
    pyautogui.click()
    make_screen(os.path.join(screens_path, "usd_viewer_render_{}_try_{}.jpg".format(case["case"], current_try)))
    sleep(1)

    # Wait render
    # TODO check that scene is rendered by window content
    sleep(15)


def save_image(args, case, current_try, image_path, screens_path):
    # Export
    export_x = 345
    export_y = 200
    moveTo(export_x, export_y)
    sleep(1)
    pyautogui.click()
    sleep(1)
    make_screen(os.path.join(screens_path, "usd_viewer_export_{}_try_{}.jpg".format(case["case"], current_try)))

    # Set rendered image path
    pyautogui.press("backspace")
    sleep(1)
    pyautogui.typewrite(image_path)
    sleep(2)

    # Click "Open" button
    usd_viewer_window_rect = get_window_rect(win32gui.FindWindow(None, "{}".format("tcp://127.0.0.1:1984")))
    open_button_x = win32api.GetSystemMetrics(0) - 200
    open_button_y = usd_viewer_window_rect[3] - 30
    moveTo(open_button_x, open_button_y)
    sleep(1)
    make_screen(os.path.join(screens_path, "save_rendered_image_{}_try_{}.jpg".format(case["case"], current_try)))
    pyautogui.click()
    sleep(1)

    # Wait a bit to save image
    sleep(5)


def set_viewport(args, case, current_try, value, screens_path):
    items_offset = {
        "Perspective": 25,
        "Top": 50,
        "Side": 75,
        "Front": 100,
        "InventorViewportCamera": 125
    }

    # Open dropdown menu to select viewport
    viewport_menu_x = 890
    viewport_menu_y = 115
    moveTo(viewport_menu_x, viewport_menu_y)
    sleep(1)
    pyautogui.click()
    sleep(1)
    make_screen(os.path.join(screens_path, "open_viewport_menu_{}_try_{}.jpg".format(case["case"], current_try)))

    if value not in items_offset:
        raise Exception("Unknown viewport value")
    else:
        # Select viewport value
        value_x = viewport_menu_x
        value_y = viewport_menu_y + items_offset[value]
        moveTo(value_x, value_y)
        sleep(1)
        make_screen(os.path.join(screens_path, "before_viewport_selected_{}_try_{}.jpg".format(case["case"], current_try)))
        pyautogui.click()
        sleep(1)
        make_screen(os.path.join(screens_path, "after_viewport_selected_{}_try_{}.jpg".format(case["case"], current_try)))


def set_quality(args, case, current_try, value, screens_path):
    items_offset = {
        "Low": 25,
        "1": 50,
        "2": 75,
        "3": 100,
        "4": 125
    }

    # Open dropdown menu to select quality
    quality_menu_x = 1185
    quality_menu_y = 115
    moveTo(quality_menu_x, quality_menu_y)
    sleep(1)
    pyautogui.click()
    sleep(1)
    make_screen(os.path.join(screens_path, "open_quality_menu_{}_try_{}.jpg".format(case["case"], current_try)))

    if value not in items_offset:
        raise Exception("Unknown quality value")
    else:
        # Select quality value
        value_x = quality_menu_x
        value_y = quality_menu_y + items_offset[value]
        moveTo(value_x, value_y)
        sleep(1)
        make_screen(os.path.join(screens_path, "before_quality_selected_{}_try_{}.jpg".format(case["case"], current_try)))
        pyautogui.click()
        sleep(1)
        make_screen(os.path.join(screens_path, "after_quality_selected_{}_try_{}.jpg".format(case["case"], current_try)))
