import argparse
import os
import subprocess
import win32gui
from time import sleep
from datetime import datetime


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--tool', required=True)
    parser.add_argument('--output_path', required=True)

    args = parser.parse_args()

    if not os.path.exists(baseline_path):
        os.makedirs(baseline_path)

    print("Open Inventor")

    process = subprocess.Popen(cmdScriptPath, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    inventor_window = None

    start_time = datetime.now()
    # Wait a minute to open Inventor
    while not inventor_window and (datetime.now() - start_time).total_seconds() <= 60:
        inventor_window = win32gui.FindWindow("Autodesk Inventor Professional 2022", None)
        print(str(inventor_window))
        sleep(5)

    if not inventor_window:
        print("Inventor window wasn't found")
        process.terminate()
        sleep(10)
        process.kill()
        exit(-1)
    else:
        print("Inventor window found")

    process.terminate()
    sleep(10)
    process.kill()
