#!/usr/bin/env python3
import os
import sys
import logging

path_this = os.path.dirname (os.path.abspath (__file__))
LOG_FOLDER = os.path.join(path_this, 'log')

def get_logger (name):
    logger = logging.getLogger (name)
    logger.setLevel (logging.DEBUG)

    formatter = logging.Formatter (
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler ()
    ch.setLevel (logging.DEBUG)
    ch.setFormatter (formatter)
    logger.addHandler (ch)

    if not os.path.isdir (LOG_FOLDER):
        os.makedirs (LOG_FOLDER)

    # create a new file everytime it's get called
    path_log_info = os.path.join (LOG_FOLDER, name +'.info')
    if os.path.exists (path_log_info):
        os.remove (path_log_info)
    fhi = logging.FileHandler (path_log_info)
    fhi.setLevel (logging.INFO)
    fhi.setFormatter (formatter)
    logger.addHandler (fhi)

    return logger

