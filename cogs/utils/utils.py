"""Utils

Simple utils python file for handy functions that are needed everywhere in the code.
"""

import asyncio
import datetime
import pytz
# import builtins

from functools import wraps


def getJSTtime():
    """Returns current time in JST"""
    return datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')

class bcolors:
    """Class that defines colors for printing in a console."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(text:str, color:str):
    """
    Print function for colors.
    
    Pass in any color of the class ``bcolors``.
    """
    print(f"{color}{text}{bcolors.ENDC}")

def print_warning(text:str):
    """
    Print function for warnings (yellow color).
    
    It is a shorthand version of writing ``print_color(text, bcolors.WARNING)``.
    """
    print_color(text, bcolors.WARNING)

def log_call(func):
    """
    Wrapper. Prints to console that function has been called.
    
    Everything inside the function will be enwrapped in a headline and footline.
    """
    async def wrapper_helper(func, *args, **kwargs):
        """
        Helper function for the wrapper.
        Makes this decorator independent of async or not-async functions.

        From: https://stackoverflow.com/a/63156433
        """
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    @wraps(func)
    async def wrapper(*args, **kwargs):
        print('============================================')
        print(f'Function called: {func.__name__.upper()}()')
        # old = builtins.print
        # builtins.print = lambda x, *args, **kwargs:  old("  >", x, *args, **kwargs)
        ret = await wrapper_helper(func, *args, **kwargs)
        # builtins.print = old
        print('============================================')
        return ret
    return wrapper
