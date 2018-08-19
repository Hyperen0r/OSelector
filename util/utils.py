import logging
import os

log = logging.getLogger(__name__)

INDENT_SIZE = 8

def create_dir(path):
    if os.path.exists(path):
        log.info("Path already exists : " + path)
    else:
        log.info("Creating new directory: " + path)
        os.makedirs(path)

def indent(text, level=0):
    return (" " * INDENT_SIZE)*level + text
