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
from subprocess import Popen, PIPE
import traceback


# Counter which display current action number
current_image_num = 0
# Logger for current test case
case_logger = None
# TODO delete port variable then widnow name will be fixed
usdviewer_window_name = "tcp://127.0.0.1:"
# Initial USD Viewer port (it's used in name of window)
initial_usdviewer_port = 1984
# Current port of USD Viewer (it's increased by 2 after each reopening of usdviewer without closing of Inventor)
usdviewer_port = initial_usdviewer_port
# Current USD Viewer window
usd_viewer_window = None
# Process of USD Viewer started from console (it's used in some cases)
usd_viewer_console_process = None


def close_process(process):
    Popen("taskkill /F /PID {pid} /T".format(pid=process.pid))


def start_new_case(case, log_path):
    global current_image_num
    current_image_num = 0
    create_case_logger(case, log_path)


def start_new_try():
    # Reset USD Viewer port number after finishing of test case
    global usdviewer_port, initial_usdviewer_port
    usdviewer_port = initial_usdviewer_port


def post_try(current_try):
    try:
        # Close USD Viewer started from console if it's necessary
        global usd_viewer_console_process
        if usd_viewer_console_process:
            close_process(usd_viewer_console_process)
    except e:
        utils.case_logger.error("Failed to execute post try (try #{}): {}".format(current_try, str(e)))
        utils.case_logger.error("Traceback: {}".format(traceback.format_exc()))


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


def make_screen(screen_path, screen_name):
    screen = pyscreenshot.grab()
    screen = screen.convert('RGB')
    global current_image_num
    screen.save(os.path.join(screen_path, "{:03}_{}".format(current_image_num, screen_name)))
    current_image_num += 1


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


def move_and_click(args, case, current_try, x, y, name, screens_path, delay_after_click = 1):
    moveTo(x, y)
    sleep(1)
    make_screen(screens_path, "before_{}_clicked_{}_try_{}.jpg".format(name, case["case"], current_try))
    pyautogui.click()
    sleep(wait_after_click)
    make_screen(screens_path, "after_{}_clicked_{}_try_{}.jpg".format(name, case["case"], current_try))


# Optimized method to select some item in menu/tool bar
def click_item_with_offset(args, case, current_try, offsets, item_name, x, y, use_x_direction, screens_path):
    if item_name.lower() not in offsets:
        raise Exception("Unknown item value")
    else:
        # Select viewport value
        item_x = x
        item_y = y

        if use_x_direction:
            item_x += items_offset[value.lower()]
        else:
            item_y += items_offset[value.lower()]

        moveTo(item_x, item_y)
        sleep(1)
        make_screen(screens_path, "before_{}_item_selected_{}_try_{}.jpg".format(item_name, case["case"], current_try))
        pyautogui.click()
        sleep(1)
        make_screen(screens_path, "after_{}_item_selected_{}_try_{}.jpg".format(item_name, case["case"], current_try))


def open_scene(args, case, current_try, screens_path):
    inventor_window_rect = get_window_rect(win32gui.FindWindow(None, "{}".format(args.tool_name)))

    open_inventor_tab(args, case, current_try, "file", screens_path)

    select_inventor_file_item(args, case, current_try, "open", screens_path)

    # Set scene path
    case_logger.info("Set scene path")
    scene_path = os.path.abspath(os.path.join(args.res_path, case["scene"]))
    case_logger.info("Scene path: {}".format(scene_path))
    pyautogui.press("backspace")
    sleep(1)
    pyautogui.typewrite(scene_path)
    sleep(2)

    # Click "Open" button
    case_logger.info("Click 'Open' button")
    open_button_x = win32api.GetSystemMetrics(0) - 200
    open_button_y = inventor_window_rect[3] - 50
    move_and_click(args, case, current_try, open_button_x, open_button_y, "open_button", screens_path)


def open_usdviewer(args, case, current_try, screens_path, click_twice = False):
    open_inventor_tab(args, case, current_try, "tools", screens_path)

    # try to open USD Viewer few times (sometimes it can't be opened after first click)
    max_iterations = 5
    iteration = 0

    global usd_viewer_window, usdviewer_port

    while iteration < max_iterations:
        iteration += 1
        window_name = usdviewer_window_name + str(usdviewer_port)
        case_logger.info("Waiting USD Viewer window with name {} (try #{})".format(window_name, iteration))
        # Open USD Viewer
        usd_viewer_tabs_x = 1430
        usd_viewer_tabs_y = 120
        moveTo(usd_viewer_tabs_x, usd_viewer_tabs_y)
        sleep(1)
        pyautogui.click()
        if click_twice:
            sleep(1)
            pyautogui.click()
        make_screen(screens_path, "before_{}_try_{}_iteration_{}.jpg".format(case["case"], current_try, iteration))
        sleep(1)

        start_time = datetime.now()
        # Wait USD Viewer window
        while not usd_viewer_window and (datetime.now() - start_time).total_seconds() <= 30:
            usd_viewer_window = win32gui.FindWindow(None, window_name)
            usdviewer_port += 2
            sleep(1)

        if usd_viewer_window:
            case_logger.info("USD Viewer window was found. Wait a bit (try #{})".format(iteration))
            # TODO check window is ready by window content
            sleep(5)
            make_screen(screens_path, "usd_viewer_found_{}_try_{}.jpg".format(case["case"], current_try))
            sleep(10)
            break
        else:
            case_logger.info("Waiting USD Viewer window wasn't found (try #{})".format(iteration))
    else:
        case_logger.info("USD Viewer window wasn't found at all")
        raise Exception("USD Viewer window wasn't found at all")


def open_usdviewer_console(args, case, current_try, scene_path, screens_path):
    case_logger.info("Open USD Viewer in console")
    console_command = "\"C:\\Program Files\\RPRViewer\\RPRViewer.exe\" \"{}\"".format(scene_path)
    case_logger.info("Start: {}".format(console_command))
    process = Popen(console_command, shell=True, stdout=PIPE, stderr=PIPE)
    global usd_viewer_console_process
    usd_viewer_console_process = process
    # TODO check window is ready by window content
    # Now window name = scene path
    window_name = scene_path
    sleep(10)
    global usd_viewer_window
    usd_viewer_window = win32gui.FindWindow(None, window_name)
    make_screen(screens_path, "usd_viewer_console_{}_try_{}.jpg".format(case["case"], current_try))
    if usd_viewer_window:
        sleep(20)
    else:
        raise Exception("USD Viewer window from console wasn't found")


def open_usdviewer_tab(args, case, current_try, tab, screens_path):
    tabs_offset = {
        "review": -160,
        "edit": -85,
        "materials": 0,
        "lightning": 90,
        "render": 170
    }

    if tab.lower() not in tabs_offset:
        raise Exception("Unknown USD Viewer tab")
    else:
        # Open tab
        case_logger.info("Open USD Viewer tab: {}".format(tab))
        left_menu_width = 180
        right_menu_width = 130
        # (window width - left menu width - right menu width) / 2 
        toolbar_center_x = (win32api.GetSystemMetrics(0) - left_menu_width - right_menu_width) / 2
        render_tab_x = left_menu_width + toolbar_center_x + tabs_offset[tab.lower()]
        render_tab_y = 20
        moveTo(render_tab_x, render_tab_y)
        # First click can't be ignored. Do it twice
        sleep(1)
        pyautogui.click()
        sleep(1)
        pyautogui.click()
        make_screen(screens_path, "usd_viewer_{}_tab_{}_try_{}.jpg".format(tab.lower(), case["case"], current_try))
        sleep(1)


def render(args, case, current_try, screens_path):
    # Render
    case_logger.info("Start render")
    render_button_x = 185
    render_button_y = 155
    move_and_click(args, case, current_try, render_button_x, render_button_y, "render_button", screens_path)

    # Wait render
    # TODO check that scene is rendered by window content
    sleep(15)


def save_image(args, case, current_try, image_path, screens_path):
    case_logger.info("Save output image")
    # Export
    export_x = 355
    export_y = 240
    move_and_click(args, case, current_try, export_x, export_y, "export", screens_path)

    # Set rendered image path
    pyautogui.press("backspace")
    sleep(1)
    pyautogui.typewrite(image_path)
    sleep(2)

    # Click "Save" button
    global usd_viewer_window
    usd_viewer_window_rect = get_window_rect(usd_viewer_window)
    save_button_x = win32api.GetSystemMetrics(0) - 200
    save_button_y = usd_viewer_window_rect[3] - 30
    move_and_click(args, case, current_try, save_button_x, save_button_y, "save_button", screens_path)

    # Wait a bit to save image
    sleep(5)


def set_viewport(args, case, current_try, value, screens_path):
    case_logger.info("Set viewport: {}".format(value))
    # Open dropdown menu to select viewport
    viewport_menu_x = 890
    viewport_menu_y = 115
    move_and_click(args, case, current_try, viewport_menu_x, viewport_menu_y, "viewport_menu", screens_path)

    items_offset = {
        "perspective": 25,
        "top": 50,
        "side": 75,
        "front": 100,
        "inventorviewportcamera": 125
    }

    # Select viewport value
    click_item_with_offset(args, case, current_try, items_offset, item_name, viewport_menu_x, viewport_menu_y, False, screens_path)


def set_quality(args, case, current_try, value, screens_path):
    case_logger.info("Set quality: {}".format(value))
    items_offset = {
        "low": 25,
        "medium": 50,
        "high": 75,
        "full": 100,
        "full 2.0": 125
    }

    # Open dropdown menu to select quality
    quality_menu_x = 1185
    quality_menu_y = 115
    move_and_click(args, case, current_try, quality_menu_x, quality_menu_y, "quality_menu", screens_path)

    # Select quality value
    click_item_with_offset(args, case, current_try, items_offset, item_name, quality_menu_x, quality_menu_y, False, screens_path)


def set_lightning(args, case, current_try, lightning_name, screens_path):
    # Search lightning name
    case_logger.info("Set lightning: {}".format(lightning_name))
    lightning_name_field_x = win32api.GetSystemMetrics(0) - 320
    lightning_name_field_y = 160
    moveTo(lightning_name_field_x, lightning_name_field_y)
    sleep(1)
    pyautogui.click()
    sleep(1)
    pyautogui.typewrite(lightning_name)
    sleep(1)
    make_screen(screens_path, "search_lightning_name_{}_try_{}.jpg".format(case["case"], current_try))

    # Select lightning
    lightning_item_x = win32api.GetSystemMetrics(0) - 540
    lightning_item_y = 285
    move_and_click(args, case, current_try, lightning_item_x, lightning_item_y, "lightning_item", screens_path)


def open_inventor_tab(args, case, current_try, tab_name, screens_path):
    case_logger.info("Open Inventor tab: {}".format(tab_name))
    tabs_offset = {
        "file": 35,
        "assemble": 120,
        "design": 225,
        "3d model": 320,
        "sketch": 410,
        "annotate": 500,
        "inspect": 600,
        "tools": 680,
        "manage": 760,
        "view": 845,
        "engironments": 950,
        "get started": 1075,
        "collaborate": 1190,
        "electromechanical": 1335
    }

    # Find menu item
    click_item_with_offset(args, case, current_try, tabs_offset, tab_name, 0, 55, True, screens_path)


def select_inventor_file_item(args, case, current_try, file_item, screens_path):
    case_logger.info("Select item in Inventor file menu: {}".format(file_item))
    file_items_offset = {
        "new": 170,
        "open": 240,
        "save": 310,
        "save as": 380,
        "export": 450,
        "share": 520,
        "manage": 590,
        "iproperties": 660,
        "print": 730,
        "close": 800
    }

    # Find menu item
    click_item_with_offset(args, case, current_try, file_items_offset, file_item, 110, 0, False, screens_path)


def convert_to_usd(args, case, current_try, wait_time, screens_path):
    case_logger.info("Convert to USD")
    open_inventor_tab(args, case, current_try, "tools", screens_path)

    # Open convertation window
    convert_button_x = 1560
    convert_button_y = 120
    move_and_click(args, case, current_try, convert_button_x, convert_button_y, "convert_button", screens_path)

    # Convert (press enter button)
    pyautogui.press("enter")
    # wait convertation a bit
    sleep(wait_time)
    make_screen(screens_path, "after_convertation_{}_try_{}.jpg".format(case["case"], current_try))



def open_scene_usdviewer(args, case, current_try, scene_path, screens_path):
    # Open convertation window
    case_logger.info("Open scene from USD Viewer")
    menu_button_x = 20
    menu_button_y = 20
    move_and_click(args, case, current_try, menu_button_x, menu_button_y, "menu_button", screens_path)

    select_usdviewer_menu_item(args, case, current_try, "open", screens_path)

    # Set scene path
    pyautogui.press("backspace")
    sleep(1)
    pyautogui.typewrite(scene_path)
    sleep(2)

    # Click "Open" button
    global usd_viewer_window
    usd_viewer_window_rect = get_window_rect(usd_viewer_window)
    open_button_x = win32api.GetSystemMetrics(0) - 200
    open_button_y = usd_viewer_window_rect[3] - 30
    move_and_click(args, case, current_try, open_button_x, open_button_y, "open_button", screens_path)

    # Wait a bit to open scene
    sleep(15)


def select_usdviewer_menu_item(args, case, current_try, item_name, screens_path):
    case_logger.info("Select item in USD Viewer menu: {}".format(item_name))
    items_offset = {
        "open": 0,
        "open recent": 50,
        "save": 100,
        "save as": 150,
        "edit": 200,
        "settings": 250,
        "help": 300,
        "quit": 350
    }

    # Find menu item
    click_item_with_offset(args, case, current_try, items_offset, item_name, 160, 60, False, screens_path)


def close_usdviewer(args, case, current_try, screens_path):
    # Click close button
    case_logger.info("Close USD Viewer")
    menu_button_x = win32api.GetSystemMetrics(0) - 23
    menu_button_y = 17
    move_and_click(args, case, current_try, menu_button_x, menu_button_y, "menu_button", screens_path, 5)
    global usd_viewer_window
    usd_viewer_window = None


def set_convert_files_format(args, case, current_try, item_name, screens_path):
    case_logger.info("Set convertation file format: {}".format(item_name))
    items_offset = {
        ".usd": 100,
        ".usda": 150
    }

    open_inventor_tab(args, case, current_try, "tools", screens_path)

    # Open plugin settings
    plugin_settings_x = 1700
    plugin_settings_y = 120
    move_and_click(args, case, current_try, plugin_settings_x, plugin_settings_y, "plugin_settings", screens_path)

    inventor_window_rect = get_window_rect(win32gui.FindWindow(None, "{}".format(args.tool_name)))
    inventor_window_center_x = (int)(inventor_window_rect[2] - inventor_window_rect[0]) / 2
    inventor_window_center_y = (int)(inventor_window_rect[3] - inventor_window_rect[1]) / 2

    # Select menu item
    dropdown_menu_x = inventor_window_center_x - 35
    dropdown_menu_y = inventor_window_center_y + 55
    move_and_click(args, case, current_try, dropdown_menu_x, dropdown_menu_y, "dropdown_menu", screens_path)

    # Find menu item
    if item_name.lower() not in items_offset:
        raise Exception("Unknown menu item")
    else:
        # Select menu item
        setting_x = inventor_window_center_x - 35
        setting_y = inventor_window_center_y + items_offset[item_name.lower()]
        move_and_click(args, case, current_try, setting_x, setting_y, "setting", screens_path)

        # Select "Ok" button
        ok_button_x = inventor_window_center_x + 150
        ok_button_y = inventor_window_center_y + 175
        move_and_click(args, case, current_try, ok_button_x, ok_button_y, "ok_button", screens_path)


def make_inventor_active(args, case, current_try, screens_path):
    case_logger.info("Make Inventor window active")
    inventor_window = win32gui.FindWindow(None, "{}".format(args.tool_name))
    win32gui.ShowWindow(inventor_window, 5)
    win32gui.SetForegroundWindow(inventor_window)
    sleep(1)
    make_screen(screens_path, "make_inventor_active{}_try_{}.jpg".format(case["case"], current_try))


def make_usdviewer_active(args, case, current_try, screens_path):
    case_logger.info("Make USD Viewer window")
    global usd_viewer_window
    win32gui.ShowWindow(usd_viewer_window, 5)
    win32gui.SetForegroundWindow(usd_viewer_window)
    sleep(1)
    make_screen(screens_path, "make_inventor_active{}_try_{}.jpg".format(case["case"], current_try))


def close_scene(args, case, current_try, screens_path):
    case_logger.info("Close scene")
    open_inventor_tab(args, case, current_try, "file", screens_path)

    select_inventor_file_item(args, case, current_try, "close", screens_path)

    inventor_window_rect = get_window_rect(win32gui.FindWindow(None, "{}".format(args.tool_name)))
    inventor_window_center_x = (int)(inventor_window_rect[2] - inventor_window_rect[0]) / 2
    inventor_window_center_y = (int)(inventor_window_rect[3] - inventor_window_rect[1]) / 2

    # Click "No" button
    no_button_x = inventor_window_center_x - 75
    no_button_y = inventor_window_center_y + 55
    move_and_click(args, case, current_try, no_button_x, no_button_y, "no_button", screens_path)
