"""module for enable logging and set directory for log file"""
import json
import logging.config
import os

from .simple_classes import *
from .status_bar import Status
from .table_panel import Table
from .tool_bar import ToolBar
from .common_menu import CommonMenu
from .db_handler import DbHandler
from .navigation_bar import Navbar
from .report import Report

__version__ = "2.0"
with open(f"/home/{os.getlogin()}/.config/lightDB/logging_conf.json")\
        as log_conf:
    data = json.load(log_conf)
    if data['handlers']['file_handler']['filename'] == '':
        data['handlers']['file_handler']['filename'] = \
            f"/home/{os.getlogin()}/.config/lightDB/lightDB.log"
with open(f"/home/{os.getlogin()}/.config/lightDB/logging_conf.json", 'w') as log_conf:
    json.dump(data, log_conf)
with open(f"/home/{os.getlogin()}/.config/lightDB/logging_conf.json",
          'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)

logging.config.dictConfig(config_dict)

logger = logging.getLogger(__name__)
logger.info('logger created!')
