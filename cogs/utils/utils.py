"""Utils

Simple utils python file for handy functions that are needed everywhere in the code.
"""

import datetime, pytz


def getJSTtime():
    """Returns current time in JST"""
    return datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(text:str, color:str):
    print(f"{color}{text}{bcolors.ENDC}")

def print_warning(text:str):
    print_color(text, bcolors.WARNING)