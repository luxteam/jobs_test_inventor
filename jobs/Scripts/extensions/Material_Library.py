import os
import sys
from time import sleep
import pyautogui

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))
import utils


def select_part_desk_top(args, case, current_try, screens_path):
    # Select top part of Desk scene by click
    utils.case_logger.info("Select top part of Desk scene")
    select_part_x = 880
    select_part_y = 500
    utils.move_and_click(args, case, current_try, select_part_x, select_part_y, "select_part", screens_path)
