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

    return logger

