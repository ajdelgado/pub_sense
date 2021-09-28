#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This script is licensed under GNU GPL version 2.0 or above
# (c) 2021 Antonio J. Delgado
# 

import sys
import os
import logging
import click
import click_config_file
from logging.handlers import SysLogHandler

class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class pub_sense:

    def __init__(self, debug_level, log_file):
        ''' Initial function called when object is created '''
        self.debug_level = debug_level
        if log_file is None:
            log_file = os.path.join(os.environ.get('HOME', os.environ.get('USERPROFILE', os.getcwd())), 'log', 'pub_sense.log')
        self.log_file = log_file
        self._init_log()

    def _init_log(self):
        ''' Initialize log object '''
        self._log = logging.getLogger("pub_sense")
        self._log.setLevel(logging.DEBUG)

        sysloghandler = SysLogHandler()
        sysloghandler.setLevel(logging.DEBUG)
        self._log.addHandler(sysloghandler)

        streamhandler = logging.StreamHandler(sys.stdout)
        streamhandler.setLevel(logging.getLevelName(self.debug_level))
        #formatter = '%(asctime)s | %(levelname)8s | %(message)s'
        formatter = '[%(levelname)s] %(message)s'
        streamhandler.setFormatter(CustomFormatter(formatter))
        self._log.addHandler(streamhandler)

        if not os.path.exists(os.path.dirname(self.log_file)):
            os.mkdir(os.path.dirname(self.log_file))

        filehandler = logging.handlers.RotatingFileHandler(self.log_file, maxBytes=102400000)
        # create formatter
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        filehandler.setFormatter(formatter)
        filehandler.setLevel(logging.DEBUG)
        self._log.addHandler(filehandler)
        return True

@click.command()
@click.option("--debug-level", "-d", default="INFO",
    type=click.Choice(
        ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
        case_sensitive=False,
    ), help='Set the debug level for the standard output.')
@click.option('--log-file', '-l', help="File to store all debug messages.")
#@click.option("--dummy","-n", is_flag=True, help="Don't do anything, just show what would be done.") # Don't forget to add dummy to parameters of main function
@click_config_file.configuration_option()
def __main__(debug_level, log_file):
    object = pub_sense(debug_level, log_file)

if __name__ == "__main__":
    __main__()

