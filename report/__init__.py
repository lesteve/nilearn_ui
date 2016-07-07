"""files for generating a report"""
import os.path as osp
import shutil

TEMPLATES = osp.join(osp.dirname(__file__), 'templates')
REPORT = osp.join(TEMPLATES, 'report')


def prepare_report_directory(directory):
    if osp.exists(directory):
        shutil.rmtree(directory)
    shutil.copytree(REPORT, directory)
