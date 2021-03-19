import argparse
import os
import subprocess
import win32gui
import win32api
import pyautogui
from time import sleep
from datetime import datetime
from subprocess import Popen, PIPE
import traceback
import pyscreenshot


def close_process(process):
    Popen("taskkill /F /PID {pid} /T".format(pid=process.pid))


def make_screen(screen_path):
    screen = pyscreenshot.grab()
    screen = screen.convert('RGB')
    screen.save(screen_path)


def moveTo(x, y):
    print("Move to x = {}, y = {}".format(x, y))
    pyautogui.moveTo(x, y)



if __name__ == '__main__':
    process = None
    rc = 0

    try:
        parser = argparse.ArgumentParser()

        parser.add_argument('--tool', required=True)
        parser.add_argument('--output_path', required=True)
        parser.add_argument('--assets_path', required=True)

        args = parser.parse_args()

        if not os.path.exists(args.output_path):
            os.makedirs(args.output_path)

        print("Open Inventor")

        process = Popen(args.tool, shell=True, stdout=PIPE, stderr=PIPE)

        inventor_window = None

        start_time = datetime.now()
        # Wait a minute to open Inventor
        while not inventor_window and (datetime.now() - start_time).total_seconds() <= 60:
            inventor_window = win32gui.FindWindow(None, "Autodesk Inventor Professional 2022")
            sleep(5)

        if not inventor_window:
            print("Inventor window wasn't found")
            rc = -1
        else:
            print("Inventor window found. Wait a bit")
            # TODO check window is ready by window content
            sleep(3)
            make_screen(os.path.join(args.output_path, "0_opened_inventor.jpg"))

            print("Screen resolution: width = {}, height = {}".format(win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)))
            inventor_window_rect = win32gui.GetWindowRect(inventor_window)
            print("Left-top corner position: x = {}, y = {}".format(inventor_window_rect[0], inventor_window_rect[1]))

            # Open "File" tab
            file_tab_x = inventor_window_rect[0] + 30
            file_tab_y = inventor_window_rect[1] + 45
            moveTo(file_tab_x, file_tab_y)
            sleep(1)
            make_screen(os.path.join(args.output_path, "1_before_choose_scene.jpg"))
            pyautogui.click()
            sleep(1)

            # Click "Open file" button
            open_file_button_x = inventor_window_rect[0] + 75
            open_file_button_y = inventor_window_rect[1] + 170
            moveTo(open_file_button_x, open_file_button_y)
            sleep(1)
            pyautogui.click()
            sleep(1)
            make_screen(os.path.join(args.output_path, "2_choose_scene.jpg"))

            # Set scene path
            print("Bottom edge position: y = {}".format(inventor_window_rect[3]))
            scene_name_field_x = (int)((inventor_window_rect[2] - inventor_window_rect[0]) / 2)
            scene_name_field_y = inventor_window_rect[3] - 175
            moveTo(scene_name_field_x, scene_name_field_y)
            sleep(1)
            pyautogui.click(clicks=2)
            sleep(1)
            scene_path = os.path.abspath(os.path.join(args.assets_path, "Basic", "test_scene.iam"))
            print("Scene path: {}".format(scene_path))
            pyautogui.press("backspace")
            sleep(1)
            pyautogui.typewrite(scene_path)
            sleep(2)

            # Click "Open" button
            print("Bottom-right corner position: x = {}, y = {}".format(inventor_window_rect[2], inventor_window_rect[3]))
            open_button_x = inventor_window_rect[2] - 150
            open_button_y = inventor_window_rect[3] - 45
            moveTo(open_button_x, open_button_y)
            sleep(1)
            make_screen(os.path.join(args.output_path, "3_scene_path.jpg"))
            pyautogui.click()
            sleep(1)

            # Wait scene opening
            # TODO check that scene is opened by window content
            sleep(10)
            make_screen(os.path.join(args.output_path, "4_opened_scene.jpg"))

            # Open "Tools" tab
            tools_tab_x = inventor_window_rect[0] + 460
            tools_tab_y = inventor_window_rect[1] + 45
            moveTo(tools_tab_x, tools_tab_y)
            sleep(1)
            pyautogui.click()
            sleep(1)

            # Open USD Viewer
            tools_tab_x = inventor_window_rect[0] + 965
            tools_tab_y = inventor_window_rect[1] + 100
            moveTo(tools_tab_x, tools_tab_y)
            sleep(1)
            pyautogui.click()
            make_screen(os.path.join(args.output_path, "5_before_usd_viewer.jpg"))
            sleep(1)

            sleep(10)

    except Exception as e:
        print("Failed to check installation: {}".format(str(e)))
        print("Traceback: {}".format(traceback.format_exc()))
    finally:
        if process:
            close_process(process)
