import win32gui
import win32api
import pyautogui
from time import sleep
from datetime import datetime
import pyscreenshot
import logging
import types


def ml_new_line(self):
    self.handler.setFormatter(self.ml_bformatter)
    self.info('')
    self.handler.setFormatter(self.ml_formatter)


def create_case_logger(case):

    formatter = logging.Formatter(fmt=u'[%(asctime)s] #%(levelname)-6s [F:%(filename)s L:%(lineno)d] >> %(message)s')
    blank_formatter = logging.Formatter(fmt=u'')

    ml_handler = logging.FileHandler(filename='{}.log'.format(case['case']), mode='a')
    ml_handler.setLevel(logging.DEBUG)
    ml_handler.setFormatter(formatter)

    case_logger = logging.getLogger('case_logger')
    case_logger.addHandler(ml_handler)
    case_logger.setLevel(logging.DEBUG)

    case_logger.handler = ml_handler
    case_logger.ml_formatter = formatter
    case_logger.ml_bformatter = blank_formatter
    case_logger.newline = types.MethodType(ml_new_line, case_logger)

    return case_logger


def is_case_skipped(case, render_platform):
    if case['status'] == 'skipped':
        return True

    return sum([render_platform & set(x) == set(x) for x in case.get('skip_on', '')])


def make_screen(screen_path):
    screen = pyscreenshot.grab()
    screen = screen.convert('RGB')
    screen.save(screen_path)


def moveTo(x, y, logger=None):
    if logger:
        logger.info("Move to x = {}, y = {}".format(x, y))
    pyautogui.moveTo(x, y)


def find_inventor_window(args):
    inventor_window = None
    # Wait a minute to open Inventor
    while not inventor_window and (datetime.now() - start_time).total_seconds() <= 60:
        inventor_window = win32gui.FindWindow(None, "{}".format(args.tool_name))
        sleep(5)

    return inventor_window


def open_scene(args, case, inventor_window, current_try):
    inventor_window_rect = win32gui.GetWindowRect(inventor_window)

    # Open "File" tab
    file_tab_x = inventor_window_rect[0] + 30
    file_tab_y = inventor_window_rect[1] + 45
    moveTo(file_tab_x, file_tab_y, logger)
    sleep(1)
    make_screen(os.path.join(args.output_path, "before_choose_scene_{}_try_{}.jpg".format(case["case"], current_try)))
    pyautogui.click()
    sleep(1)

    # Click "Open file" button
    open_file_button_x = inventor_window_rect[0] + 75
    open_file_button_y = inventor_window_rect[1] + 170
    moveTo(open_file_button_x, open_file_button_y, logger)
    sleep(1)
    pyautogui.click()
    sleep(1)
    make_screen(os.path.join(args.output_path, "choose_scene_{}_try_{}.jpg".format(case["case"], current_try)))

    # Set scene path
    scene_path = os.path.abspath(os.path.join(args.res_path, args.testType, case["scene"]))
    print("Scene path: {}".format(scene_path))
    pyautogui.press("backspace")
    sleep(1)
    pyautogui.typewrite(scene_path)
    sleep(2)

    # Click "Open" button
    open_button_x = inventor_window_rect[2] - 150
    open_button_y = inventor_window_rect[3] - 45
    moveTo(open_button_x, open_button_y, logger)
    sleep(1)
    make_screen(os.path.join(args.output_path, "scene_path_{}_try_{}.jpg".format(case["case"], current_try)))
    pyautogui.click()
    sleep(1)


def open_usd_viewer(args, case, inventor_window, current_try):
    # try to open USD Viewer few times
    max_iterations = 3
    iteration = 0
    usd_viewer_window = None

    while iteration < max_iterations:
        iteration += 1
        print("Waiting USD Viewer window (try #{})".format(iteration))
        # Open USD Viewer
        usd_viewer_tabs_x = inventor_window_rect[0] + 350
        usd_viewer_tabs_y = inventor_window_rect[1] + 100
        moveTo(usd_viewer_tabs_x, usd_viewer_tabs_y, logger)
        sleep(1)
        usd_viewer_button_x = inventor_window_rect[0] + 350
        usd_viewer_button_y = inventor_window_rect[1] + 150
        moveTo(usd_viewer_button_x, usd_viewer_button_y, logger)
        sleep(1)
        pyautogui.click()
        make_screen(os.path.join(args.output_path, "before_{}_try_{}_iteration_{}.jpg".format(case["case"], current_try, iteration)))
        sleep(1)

        start_time = datetime.now()
        # Wait USD Viewer window
        while not usd_viewer_window and (datetime.now() - start_time).total_seconds() <= 30:
            usd_viewer_window = win32gui.FindWindow(None, "tcp://127.0.0.1:1984")
            sleep(5)

        if usd_viewer_window:
            print("USD Viewer window was found. Wait cache building (try #{})".format(iteration))
            # TODO check window is ready by window content
            sleep(120)
            break
        else:
            print("Waiting USD Viewer window wasn't found (try #{})".format(iteration))
    else:
        print("USD Viewer window wasn't found at all")
        raise Exception("USD Viewer window wasn't found at all")


def open_render_tab(args, case, inventor_window, current_try):
    # Open Render tab
    usd_viewer_menu_width = 40
    # (window width - menu width) / 2 
    toolbar_center_x = (usd_viewer_window_rect[2] - usd_viewer_window_rect[0] - usd_viewer_menu_width) / 2
    render_tab_x = usd_viewer_window_rect[0] + usd_viewer_menu_width + toolbar_center_x + 115
    render_tab_y = usd_viewer_window_rect[1] + 20
    moveTo(render_tab_x, render_tab_y, logger)
    sleep(1)
    pyautogui.click()
    make_screen(os.path.join(args.output_path, "usd_viewer_render_tab_{}_try_{}.jpg".format(case["case"], current_try)))
    sleep(1)


def render(args, case, inventor_window, current_try):
    # Render
    render_button_x = usd_viewer_window_rect[0] + 230
    render_button_y = usd_viewer_window_rect[1] + 105
    moveTo(render_button_x, render_button_y, logger)
    sleep(1)
    pyautogui.click()
    make_screen(os.path.join(args.output_path, "usd_viewer_render_{}_try_{}.jpg".format(case["case"], current_try)))
    sleep(1)

    # Wait render
    # TODO check that scene is rendered by window content
    sleep(15)


def save_image(args, case, inventor_window, current_try, image_path):
    # Export
    export_x = usd_viewer_window_rect[0] + 230
    export_y = usd_viewer_window_rect[1] + 135
    moveTo(export_x, export_y, logger)
    sleep(1)
    pyautogui.click()
    sleep(1)
    make_screen(os.path.join(args.output_path, "usd_viewer_export_{}_try_{}.jpg".format(case["case"], current_try)))

    # Set rendered image path
    rendered_image_field_x = (int)((inventor_window_rect[2] - inventor_window_rect[0]) / 2)
    rendered_image_field_y = inventor_window_rect[3] - 115
    moveTo(rendered_image_field_x, rendered_image_field_y, logger)
    sleep(1)
    pyautogui.click(clicks=2)
    sleep(1)
    scene_path = os.path.abspath(os.path.join(args.output_path, "RESULT.jpg"))
    pyautogui.press("backspace")
    sleep(1)
    pyautogui.typewrite(scene_path)
    sleep(2)

    # Click "Open" button
    open_button_x = inventor_window_rect[2] - 170
    open_button_y = inventor_window_rect[3] - 40
    moveTo(open_button_x, open_button_y, logger)
    sleep(1)
    make_screen(os.path.join(args.output_path, "save_rendered_image_{}_try_{}.jpg".format(case["case"], current_try)))
    pyautogui.click()
    sleep(1)

    # Wait a bit to save image
    sleep(5)
