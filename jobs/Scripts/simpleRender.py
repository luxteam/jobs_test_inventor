import argparse
import os
from subprocess import Popen, PIPE
import json
import platform
from datetime import datetime
from shutil import copyfile
import utils
import sys
import traceback
import win32gui
import win32api
from time import sleep
import re
import importlib
from glob import glob

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from jobs_launcher.core.config import *
from jobs_launcher.core.system_info import get_gpu
from jobs_launcher.core.kill_process import kill_process


def copy_test_cases(args):
    copyfile(os.path.realpath(os.path.join(os.path.dirname(
        __file__), '..', 'Tests', args.test_group, 'test_cases.json')),
        os.path.realpath(os.path.join(os.path.abspath(
            args.output), 'test_cases.json')))


def copy_baselines(args, case, baseline_path, baseline_path_tr):
    try:
        copyfile(os.path.join(baseline_path_tr, case['case'] + CASE_REPORT_SUFFIX),
                 os.path.join(baseline_path, case['case'] + CASE_REPORT_SUFFIX))

        with open(os.path.join(baseline_path, case['case'] + CASE_REPORT_SUFFIX)) as baseline:
            baseline_json = json.load(baseline)

        for thumb in [''] + THUMBNAIL_PREFIXES:
            if os.path.exists(os.path.join(baseline_path_tr, baseline_json[thumb + 'render_color_path'])):
                copyfile(os.path.join(baseline_path_tr, baseline_json[thumb + 'render_color_path']),
                         os.path.join(baseline_path, baseline_json[thumb + 'render_color_path']))
    except:
        main_logger.error('Failed to copy baseline ' +
                                      os.path.join(baseline_path_tr, case['case'] + CASE_REPORT_SUFFIX))


def prepare_empty_reports(args, current_conf):
    main_logger.info('Create empty report files')

    baseline_path_tr = os.path.join(
        'c:/TestResources/usd_viewer_autotests_baselines', args.test_group)

    baseline_path = os.path.join(
        args.output, os.path.pardir, os.path.pardir, os.path.pardir, 'Baseline', args.test_group)

    copyfile(os.path.abspath(os.path.join(args.output, '..', '..', '..', '..', 'jobs_launcher',
                                          'common', 'img', 'error.jpg')), os.path.join(args.output, 'Color', 'failed.jpg'))

    with open(os.path.join(os.path.abspath(args.output), "test_cases.json"), "r") as json_file:
        cases = json.load(json_file)

    for case in cases:
        if utils.is_case_skipped(case, current_conf):
            case['status'] = 'skipped'

        if case['status'] != 'done' and case['status'] != 'error':
            if case["status"] == 'inprogress':
                case['status'] = 'active'

            test_case_report = RENDER_REPORT_BASE.copy()
            test_case_report['test_case'] = case['case']
            test_case_report['case_functions'] = case['functions']
            test_case_report['render_device'] = get_gpu()
            test_case_report['script_info'] = case['script_info']
            test_case_report['scene_name'] = case.get('scene', '')
            test_case_report['test_group'] = args.test_group
            test_case_report['date_time'] = datetime.now().strftime(
                '%m/%d/%Y %H:%M:%S')
            if case['status'] == 'skipped':
                test_case_report['test_status'] = 'skipped'
                test_case_report['file_name'] = case['case'] + case.get('extension', '.jpg')
                test_case_report['render_color_path'] = os.path.join('Color', test_case_report['file_name'])
                test_case_report['group_timeout_exceeded'] = False

                try:
                    skipped_case_image_path = os.path.join(args.output, 'Color', test_case_report['file_name'])
                    if not os.path.exists(skipped_case_image_path):
                        copyfile(os.path.join(args.output, '..', '..', '..', '..', 'jobs_launcher', 
                            'common', 'img', "skipped.jpg"), skipped_case_image_path)
                except OSError or FileNotFoundError as err:
                    main_logger.error("Can't create img stub: {}".format(str(err)))
            else:
                test_case_report['test_status'] = 'error'
                test_case_report['file_name'] = 'failed.jpg'
                test_case_report['render_color_path'] = os.path.join('Color', 'failed.jpg')

            case_path = os.path.join(args.output, case['case'] + CASE_REPORT_SUFFIX)

            if os.path.exists(case_path):
                with open(case_path) as f:
                    case_json = json.load(f)[0]
                    test_case_report["number_of_tries"] = case_json["number_of_tries"]

            with open(case_path, "w") as f:
                f.write(json.dumps([test_case_report], indent=4))

        copy_baselines(args, case, baseline_path, baseline_path_tr)
    with open(os.path.join(args.output, "test_cases.json"), "w+") as f:
        json.dump(cases, f, indent=4)


def save_results(args, case, cases, test_case_status, render_time = 0.0):
    with open(os.path.join(args.output, case["case"] + CASE_REPORT_SUFFIX), "r") as file:
        test_case_report = json.loads(file.read())[0]
        test_case_report["file_name"] = case["case"] + case.get("extension", '.jpg')
        test_case_report["render_color_path"] = os.path.join("Color", test_case_report["file_name"])
        test_case_report["test_status"] = test_case_status
        test_case_report["render_time"] = render_time
        test_case_report["execution_log"] = os.path.join("execution_logs", case["case"] + ".log")
        test_case_report["group_timeout_exceeded"] = False
        test_case_report["testing_start"] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        test_case_report["number_of_tries"] += 1

    with open(os.path.join(args.output, case["case"] + CASE_REPORT_SUFFIX), "w") as file:
        json.dump([test_case_report], file, indent=4)

    case["status"] = test_case_status
    with open(os.path.join(args.output, "test_cases.json"), "w") as file:
        json.dump(cases, file, indent=4)


def execute_tests(args, current_conf):
    rc = 0

    with open(os.path.join(os.path.abspath(args.output), "test_cases.json"), "r") as json_file:
        cases = json.load(json_file)

    spec = importlib.util.find_spec("extensions." + args.test_group)
    group_module = importlib.util.module_from_spec(spec)
    sys.modules["group_module"] = group_module
    spec.loader.exec_module(group_module)

    for case in [x for x in cases if not utils.is_case_skipped(x, current_conf)]:

        screens_path = os.path.join(args.output, "Color", case["case"])

        if not os.path.exists(screens_path):
            os.makedirs(screens_path)

        current_try = 0

        utils.start_new_case(case, os.path.join(args.output, "execution_logs"))

        while current_try < args.retries:
            try:
                utils.start_new_try()
                # clear dir with exported files
                trash_files = glob(os.path.join(args.res_path, "..", "..", "Temp", "*"))
                for file in trash_files:
                    os.remove(file)

                process = None

                utils.case_logger.info("Start '{}' (try #{})".format(case["case"], current_try))
                utils.case_logger.info("Screen resolution: width = {}, height = {}".format(win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)))
                utils.case_logger.info("Open Inventor")

                process = Popen(args.tool, shell=True, stdout=PIPE, stderr=PIPE)

                inventor_window = utils.find_inventor_window(args)

                utils.make_screen(screens_path, "opened_inventor_{}_try_{}.jpg".format(case["case"], current_try))

                if not inventor_window:
                    raise Exception("Inventor window wasn't found")
                else:
                    utils.case_logger.info("Inventor window found. Wait a bit")
                    # TODO check window is ready by window content
                    sleep(20)

                if "scene" in case:
                    utils.open_scene(args, case, current_try, screens_path)

                    # Wait scene opening
                    # TODO check that scene is opened by window content    
                    sleep(case["open_time"])
                    utils.make_screen(screens_path, "opened_scene_{}_try_{}.jpg".format(case["case"], current_try))

                image_path = os.path.abspath(os.path.join(args.output, "Color", case["case"] + ".jpg"))
                utils.case_logger.info("Image path: {}".format(image_path))

                for function in case["functions"]:
                    if re.match("((^\S+|^\S+ \S+) = |^print|^if|^for|^with)", function):
                        exec(function)
                    else:
                        eval(function)

                save_results(args, case, cases, "passed")

                if not os.path.exists(image_path):
                    raise Exception("Output image doesn't exist")

                utils.case_logger.info("Case '{}' finished".format(case["case"]))

                break
            except Exception as e:
                utils.case_logger.error("Failed to execute test case (try #{}): {}".format(current_try, str(e)))
                utils.case_logger.error("Traceback: {}".format(traceback.format_exc()))
            finally:
                if process:
                    utils.close_process(process)
                current_try += 1
                utils.post_try(current_try)
        else:
            utils.case_logger.error("Failed to execute case '{}' at all".format(case["case"]))
            rc = -1
            save_results(args, case, cases, "error")

    return rc


def createArgsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--tool", required=True, metavar="<path>")
    parser.add_argument("--tool_name", required=True)
    parser.add_argument("--output", required=True, metavar="<dir>")
    parser.add_argument("--test_group", required=True)
    parser.add_argument("--res_path", required=True)
    parser.add_argument("--test_cases", required=True)
    parser.add_argument("--retries", required=False, default=2, type=int)
    parser.add_argument("--update_refs", required=True)
    parser.add_argument("--stucking_time", required=False, default=180, type=int)

    return parser


if __name__ == "__main__":
    main_logger.info("simpleRender start working...")

    args = createArgsParser().parse_args()

    try:
        os.makedirs(args.output)

        if not os.path.exists(os.path.join(args.output, "Color")):
            os.makedirs(os.path.join(args.output, "Color"))
        if not os.path.exists(os.path.join(args.output, "render_tool_logs")):
            os.makedirs(os.path.join(args.output, "render_tool_logs"))
        if not os.path.exists(os.path.join(args.output, "execution_logs")):
            os.makedirs(os.path.join(args.output, "execution_logs"))

        render_device = get_gpu()
        system_pl = platform.system()
        current_conf = set(platform.system()) if not render_device else {platform.system(), render_device}
        main_logger.info("Detected GPUs: {}".format(render_device))
        main_logger.info("PC conf: {}".format(current_conf))
        main_logger.info("Creating predefined errors json...")

        copy_test_cases(args)
        prepare_empty_reports(args, current_conf)
        #TODO do not open inventor each time
        exit(execute_tests(args, current_conf))
    except Exception as e:
        main_logger.error("Failed during script execution. Exception: {}".format(str(e)))
        main_logger.error("Traceback: {}".format(traceback.format_exc()))
        exit(-1)
