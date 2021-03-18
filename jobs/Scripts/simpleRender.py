import argparse
import os
import subprocess
import json
import platform
from datetime import datetime
from shutil import copyfile
from utils import is_case_skipped
import sys
import traceback

sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
import jobs_launcher.core.config as core_config
from jobs_launcher.core.system_info import get_gpu
from jobs_launcher.core.kill_process import kill_process


def copy_test_cases(args):
    copyfile(os.path.realpath(os.path.join(os.path.dirname(
        __file__), '..', 'Tests', args.testType, 'test_cases.json')),
        os.path.realpath(os.path.join(os.path.abspath(
            args.output), 'test_cases.json')))


def copy_baselines(args):
    baseline_path_tr = os.path.join('c:/TestResources', baseline_dir, args.testType)

    baseline_path = os.path.join(
        work_dir, os.path.pardir, os.path.pardir, os.path.pardir, 'Baseline', args.testType)

    if not os.path.exists(baseline_path):
        os.makedirs(baseline_path)
        os.makedirs(os.path.join(baseline_path, 'Color'))

    if 'Update' not in args.update_refs:
        try:
            copyfile(os.path.join(baseline_path_tr, case['case'] + core_config.CASE_REPORT_SUFFIX),
                     os.path.join(baseline_path, case['case'] + core_config.CASE_REPORT_SUFFIX))

            with open(os.path.join(baseline_path, case['case'] + core_config.CASE_REPORT_SUFFIX)) as baseline:
                baseline_json = json.load(baseline)

            for thumb in [''] + core_config.THUMBNAIL_PREFIXES:
                if thumb + 'render_color_path' and os.path.exists(os.path.join(baseline_path_tr, baseline_json[thumb + 'render_color_path'])):
                    copyfile(os.path.join(baseline_path_tr, baseline_json[thumb + 'render_color_path']),
                             os.path.join(baseline_path, baseline_json[thumb + 'render_color_path']))
        except:
            core_config.main_logger.error('Failed to copy baseline ' +
                                          os.path.join(baseline_path_tr, case['case'] + core_config.CASE_REPORT_SUFFIX))


def prepare_empty_reports(args):
    core_config.main_logger.info('Create empty report files')

    if not os.path.exists(os.path.join(work_dir, 'Color')):
        os.makedirs(os.path.join(work_dir, 'Color'))
    copyfile(os.path.abspath(os.path.join(work_dir, '..', '..', '..', '..', 'jobs_launcher',
                                          'common', 'img', 'error.jpg')), os.path.join(work_dir, 'Color', 'failed.jpg'))

    gpu = get_gpu()
    system_pl = platform.system()
    if not gpu:
        core_config.main_logger.error("Can't get gpu name")
    if not system_pl:
        core_config.main_logger.error("Can't get system name")
    render_platform = {platform.system(), gpu}

    for case in cases:
        if is_case_skipped(case, render_platform):
            case['status'] = 'skipped'

        if case['status'] != 'done' and case['status'] != 'error':
            if case["status"] == 'inprogress':
                case['status'] = 'active'

            template = core_config.RENDER_REPORT_BASE.copy()
            template['test_case'] = case['case']
            template['case_functions'] = case['functions']
            template['render_device'] = gpu
            template['script_info'] = case['script_info']
            template['scene_name'] = case.get('scene', '')
            template['test_group'] = args.testType
            template['date_time'] = datetime.now().strftime(
                '%m/%d/%Y %H:%M:%S')
            if case['status'] == 'skipped':
                template['test_status'] = 'skipped'
                template['file_name'] = case['case'] + case.get('extension', '.jpg')
                template['render_color_path'] = os.path.join('Color', template['file_name'])
                template['group_timeout_exceeded'] = False

                try:
                    skipped_case_image_path = os.path.join(args.output, 'Color', template['file_name'])
                    if not os.path.exists(skipped_case_image_path):
                        copyfile(os.path.join(work_dir, '..', '..', '..', '..', 'jobs_launcher', 
                            'common', 'img', "skipped.jpg"), skipped_case_image_path)
                except OSError or FileNotFoundError as err:
                    core_config.main_logger.error("Can't create img stub: {}".format(str(err)))
            else:
                template['test_status'] = 'error'
                template['file_name'] = 'failed.jpg'
                template['render_color_path'] = os.path.join('Color', 'failed.jpg')

            case_path = os.path.join(work_dir, case['case'] + core_config.CASE_REPORT_SUFFIX)

            if os.path.exists(case_path):
                with open(case_path) as f:
                    case_json = json.load(f)[0]
                    template["number_of_tries"] = case_json["number_of_tries"]

            with open(case_path, 'w') as f:
                f.write(json.dumps([template], indent=4))

        copy_baselines(args)
    with open(os.path.join(work_dir, 'test_cases.json'), "w+") as f:
        json.dump(cases, f, indent=4)


def execute_tests(args):
    pass


def main(args):
    prepare_empty_reports(args)

    return execute_tests(args)


def createArgsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--tool', required=True, metavar="<path>")
    parser.add_argument('--output', required=True, metavar="<dir>")
    parser.add_argument('--testType', required=True)
    parser.add_argument('--res_path', required=True)
    parser.add_argument('--testCases', required=True)
    parser.add_argument('--retries', required=False, default=2, type=int)
    parser.add_argument('--update_refs', required=True)
    parser.add_argument('--stucking_time', required=False, default=180, type=int)

    return parser


if __name__ == "__main__":
    core_config.main_logger.info("simpleRender start working...")

    args = createArgsParser().parse_args()

    try:
        os.makedirs(args.output)
        copy_test_cases(args)
        prepare_empty_reports(args)
        #TODO do not open inventor each time
        exit(execute_tests(args))
    except Exception as e:
        core_config.main_logger.error("Failed during script execution. Exception: {}".format(str(e)))
        core_config.main_logger.error("Traceback: {}".format(traceback.format_exc()))
        exit(-1)
