import os
import sys
from time import sleep
import pyautogui

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))
import utils


def run_case(args, case, current_try, screens_path, image_path, material_name, material_in_row = 1, material_row = 1):
    utils.open_usdviewer(args, case, current_try, screens_path)
    utils.open_usdviewer_tab(args, case, current_try, "materials", screens_path)
    select_part_desk_top(args, case, current_try, screens_path)
    utils.select_material(args, case, current_try, material_name, screens_path, material_in_row, material_row)
    utils.open_usdviewer_tab(args, case, current_try, "render", screens_path)
    utils.render(args, case, current_try, screens_path)
    utils.save_image(args, case, current_try, image_path, screens_path)


def select_part_desk_top(args, case, current_try, screens_path):
    # Select top part of Desk scene by click
    utils.case_logger.info("Select top part of Desk scene")
    select_part_x = 1000
    select_part_y = 520
    utils.move_and_click(args, case, current_try, select_part_x, select_part_y, "select_part", screens_path)
