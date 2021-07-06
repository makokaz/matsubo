"""Utils

Simple utils python file for handy functions that are needed everywhere in the code.
"""

import datetime, pytz


def getJSTtime():
    """Returns current time in JST"""
    return datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')
