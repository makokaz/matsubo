"""Utils

Simple utils python file for handy functions that are needed everywhere in the code.
"""

import asyncio
import calendar
import datetime
import pytz
# import builtins

from functools import wraps


def day_suffix(d:int) -> str:
    """Returns day-suffix 'st', 'nd', 'rd', 'th' for a day of a month.

    For example, the 21st of August -> returns 'st'.

    Parameters
    ----------
    d: :class:`int`
        Integer that represents the day of the month.
        Ranges from 1-31(max).
    """
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')
def day_kanji(w:str) -> str:
    """Returns a Japanese Kanji that represents a weekday.
    
    Parameters
    ----------
    w: :class:`str`
        String that represents the day of the week, for example 'Monday'.
    """
    return {'Monday':'月','Tuesday':'火','Wednesday':'水','Thursday':'木','Friday':'金','Saturday':'土','Sunday':'日'}.get(w,'')
def custom_strftime(format:str, t:datetime.datetime) -> str:
    """Returns special date format as string.

    That means:
        - `{S}` in a string will be replaced with the day + suffix
        - `{DAY}` will be replaced with the Kanji of the weekday
    
    Parameters
    ----------
    format: :class:`str`
        String with special keys `{S}` and `{DAY}` to be formatted.
    t: :class:`datetime`
        The date from where to fetch the information.
    """
    return t.strftime(format).replace('{S}', str(t.day) + day_suffix(t.day)).replace('{DAY}', day_kanji(calendar.day_name[t.weekday()]))


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
