import argparse
import os
import win32gui
import win32api
import pyautogui
from time import sleep
from datetime import datetime
from psutil import Popen, process_iter
from subprocess import PIPE
import traceback
import pyscreenshot
from shutil import rmtree

pyautogui.FAILSAFE = False


def close_process(process):
    child_processes = process.children()
    print("Child processes: {}".format(child_processes))
    for ch in child_processes:
        try:
            ch.terminate()
            sleep(10)
            ch.kill()
            sleep(10)
            status = ch.status()
            print("Process is alive: {}. Name: {}. Status: {}".format(ch, ch.name(), status))
        except psutil.NoSuchProcess:
            print("Process is killed: {}".format(ch))

    try:
        process.terminate()
        sleep(10)
        process.kill()
        sleep(10)
        status = process.status()
        print("Process is alive: {}. Name: {}. Status: {}".format(process, process.name(), status))
    except psutil.NoSuchProcess:
        print("Process is killed: {}".format(process))


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
        parser.add_argument('--tool_name', required=True)
        parser.add_argument('--output_path', required=True)
        parser.add_argument('--assets_path', required=True)

        args = parser.parse_args()

        if os.path.exists(args.output_path):
            rmtree(args.output_path)
        os.makedirs(args.output_path)

        print("Open Inventor")

        process = Popen(args.tool, shell=True, stdout=PIPE, stderr=PIPE)

        inventor_window = None

        start_time = datetime.now()
        # Wait a minute to open Inventor
        while not inventor_window and (datetime.now() - start_time).total_seconds() <= 60:
            inventor_window = win32gui.FindWindow(None, "{}".format(args.tool_name))
            sleep(1)

        make_screen(os.path.join(args.output_path, "000_opened_inventor.jpg"))

        if not inventor_window:
            print("Inventor window wasn't found")
            rc = -1
        else:
            print("Inventor window found. Wait a bit")
            # TODO check window is ready by window content
            sleep(90)

            window_width = win32api.GetSystemMetrics(0)
            window_height = win32api.GetSystemMetrics(1)

            print("Screen resolution: width = {}, height = {}".format(window_width, window_height))
            inventor_window_rect = win32gui.GetWindowRect(inventor_window)
            print("Left-top corner position: x = {}, y = {}".format(inventor_window_rect[0], inventor_window_rect[1]))
            print("Bottom-right corner position: x = {}, y = {}".format(inventor_window_rect[2], inventor_window_rect[3]))

            # Open "File" tab
            file_tab_x = 45
            file_tab_y = 55
            moveTo(file_tab_x, file_tab_y)
            sleep(1)
            make_screen(os.path.join(args.output_path, "001_before_file_tab_scene.jpg"))
            pyautogui.click()
            sleep(1)

            # Click "Open file" button
            open_file_button_x = 110
            open_file_button_y = 240
            moveTo(open_file_button_x, open_file_button_y)
            sleep(1)
            make_screen(os.path.join(args.output_path, "002_before_choose_scene.jpg"))
            pyautogui.click()
            sleep(1)
            make_screen(os.path.join(args.output_path, "003_choose_scene.jpg"))

            # Set scene path
            scene_path = os.path.abspath(os.path.join(args.assets_path, "Smoke", "TestScene", "test_scene.iam"))
            print("Scene path: {}".format(scene_path))
            pyautogui.press("backspace")
            sleep(1)
            pyautogui.typewrite(scene_path)
            sleep(2)

            # Click "Open" button
            open_button_x = window_width - 200
            open_button_y = inventor_window_rect[3] - 50
            moveTo(open_button_x, open_button_y)
            sleep(1)
            make_screen(os.path.join(args.output_path, "004_scene_path.jpg"))
            pyautogui.click()
            sleep(1)

            # Wait scene opening
            # TODO check that scene is opened by window content
            sleep(30)
            make_screen(os.path.join(args.output_path, "005_opened_scene.jpg"))

            # Open "Tools" tab
            tools_tab_x = 680
            tools_tab_y = 55
            moveTo(tools_tab_x, tools_tab_y)
            sleep(1)
            pyautogui.click()
            sleep(1)

            # try to open USD Viewer few times (sometimes it can't be opened after first click)
            max_iterations = 5
            iteration = 0
            usd_viewer_window = None

            while iteration < max_iterations:
                iteration += 1
                print("Waiting USD Viewer window (try #{})".format(iteration))
                # Open USD Viewer
                usd_viewer_tabs_x = 1430
                usd_viewer_tabs_y = 120
                moveTo(usd_viewer_tabs_x, usd_viewer_tabs_y)
                sleep(1)
                pyautogui.click()
                make_screen(os.path.join(args.output_path, "006_{}_before_usd_viewer.jpg".format(iteration)))
                sleep(1)

                start_time = datetime.now()
                # Wait USD Viewer window
                while not usd_viewer_window and (datetime.now() - start_time).total_seconds() <= 30:
                    usd_viewer_window_name = "tcp://127.0.0.1:1984"
                    usd_viewer_window = win32gui.FindWindow(None, usd_viewer_window_name)
                    sleep(1)

                if usd_viewer_window:
                    print("USD Viewer window was found. Wait cache building (try #{})".format(iteration))
                    # TODO check window is ready by window content
                    sleep(30)
                    make_screen(os.path.join(args.output_path, "007_usd_viewer_found.jpg"))
                    sleep(90)
                    break
                else:
                    print("USD Viewer window wasn't found (try #{})".format(iteration))
            else:
                close_process(process)
                exit(-1)

            usd_viewer_window_rect = win32gui.GetWindowRect(usd_viewer_window)
            print("Left-top corner position: x = {}, y = {}".format(usd_viewer_window_rect[0], usd_viewer_window_rect[1]))
            print("Bottom-right corner position: x = {}, y = {}".format(usd_viewer_window_rect[2], usd_viewer_window_rect[3]))

            # Open Render tab
            left_menu_width = 180
            right_menu_width = 130
            # (window width - left menu width - right menu width) / 2 
            toolbar_center_x = (window_width - left_menu_width - right_menu_width) / 2
            render_tab_x = left_menu_width + toolbar_center_x + 170
            render_tab_y = 20
            moveTo(render_tab_x, render_tab_y)
            sleep(1)
            pyautogui.click()
            make_screen(os.path.join(args.output_path, "008_usd_viewer_render_tab.jpg"))
            sleep(1)

            # Render
            render_button_x = 185
            render_button_y = 155
            moveTo(render_button_x, render_button_y)
            sleep(1)
            pyautogui.click()
            make_screen(os.path.join(args.output_path, "009_usd_viewer_render.jpg"))
            sleep(1)

            # Wait render
            # TODO check that scene is rendered by window content
            sleep(15)

            # Export
            export_x = 355
            export_y = 240
            moveTo(export_x, export_y)
            sleep(1)
            pyautogui.click()
            sleep(1)
            make_screen(os.path.join(args.output_path, "010_usd_viewer_export.jpg"))

            # Set rendered image path
            image_path = os.path.abspath(os.path.join(args.output_path, "RESULT.jpg"))
            pyautogui.press("backspace")
            sleep(1)
            pyautogui.typewrite(image_path)
            sleep(2)

            # Click "Open" button
            open_button_x = window_width - 200
            open_button_y = usd_viewer_window_rect[3] - 30
            moveTo(open_button_x, open_button_y)
            sleep(1)
            make_screen(os.path.join(args.output_path, "011_save_rendered_image.jpg"))
            pyautogui.click()
            sleep(1)

            # Wait a bit to save image
            sleep(5)

    except Exception as e:
        print("Failed to check installation: {}".format(str(e)))
        print("Traceback: {}".format(traceback.format_exc()))
    finally:
        if process:
            close_process(process)
        # RPRViewer.exe isn't a child process of Inventor. It won't be killed if Inventor is killed
        for proc in process_iter():
            if proc.name() == "RPRViewer.exe":
                print("Kill viewer")
                close_process(proc)
        print("Post actions finished")

    exit(rc)
