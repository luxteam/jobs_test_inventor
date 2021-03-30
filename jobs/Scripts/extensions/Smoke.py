import os
import sys

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))
import utils


def open_converted_scene(args, case, current_try, screens_path):
    scene_path = os.path.abspath(os.path.join(args.res_path, "..", "..", "Temp", case["scene"].replace(".iam", ".usd")))
    utils.open_scene_usdviewer(args, case, current_try, scene_path, screens_path)
