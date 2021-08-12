"""Event class

Simple event class to define what attributes an event has, and other helpful functions like euqlity-checking.
"""

import datetime
import calendar

def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')
def suffix2(w):
    return {'Monday':'月','Tuesday':'火','Wednesday':'水','Thursday':'木','Friday':'金','Saturday':'土','Sunday':'日'}.get(w,'')
def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day)).replace('{DAY}', suffix2(calendar.day_name[t.weekday()]))

class Event(object):
    def __init__(self,
            id='', # Unique ID for every event
            name='', # Event name
            description='', # Event description
            url='', # URL where event was found
            img='', # Image URL
            date_start='', # Start-date of event
            date_end='', # End-date of event
            date_fuzzy='', # If no hard date is given
            time_start='', # Time of event
            time_end='', # Time of event
            location='', # Event-Location
            cost='', # Entry-fee to event
            status='', # Cancelled, Online, Postponed, ...
            other='', # Additional information tag
            visibility='', # Prefecture, University, ... used for visibility to channels
            source='', # Source where event was scrapped
            date_added=None): # ONLY SET BY DATABASE: Date of when event was added to database
        self.id = id
        self.name = name
        self.description = description
        self.url = url
        self.img = img
        self.date_start = date_start
        self.date_end = date_end
        self.date_fuzzy = date_fuzzy
        self.time_start = time_start
        self.time_end = time_end
        self.location = location
        self.cost = cost
        self.status = status
        self.other = other
        self.visibility = visibility
        self.source = source
        self.date_added = date_added

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.id == other.id
        return False

    def __str__(self):
        text = f"""***{self.name}*** [{self.id}]
        date: {self.getDateRange() if not self.date_fuzzy else self.date_fuzzy}
        time: {self.getTimeRange()}
        location: {self.location}
        cost: {self.cost}
        url: {self.url}
        image-url: {self.img}
        status: {self.status}
        visibility: {self.visibility}
        source: {self.source}
        other: {self.other}
        description: {self.description}"""
        return text
    
    def getDateRange(self) -> str:
        """Returns date-range of when event occurs"""
        if self.date_fuzzy:
            return self.date_fuzzy
        # date_start = str(custom_strftime('%b {S} ({DAY}), %Y', datetime.datetime.strptime(self.date_start, '%Y-%m-%d')))
        # date_end = str(custom_strftime('%b {S} ({DAY}), %Y', datetime.datetime.strptime(self.date_end, '%Y-%m-%d'))) if self.date_start != self.date_end else ''
        date_start = str(custom_strftime('%b {S} ({DAY}), %Y', self.date_start))
        date_end = str(custom_strftime('%b {S} ({DAY}), %Y', self.date_end)) if self.date_start != self.date_end else ''
        return f"{date_start} - {date_end}".strip(' - ')

    def getTimeRange(self) -> str:
        """Returns time-range of when event occurs"""
        if not self.time_start:
            return '---'
        time_start = self.time_start.strftime('%H:%M')
        time_end = self.time_end.strftime('%H:%M') if self.time_end else ''
        return f"{time_start} - {time_end}".strip(' - ')
    

def mergeDuplicateEvents(events, check_duplicate_func=None, merge_func=None, verbose=False):
    """
    Merges duplicate events in given list.
    Duplicate events happen when e.g. the same event is hold next week again.
    
    Optional arguments:
        * check_duplicate_func: Pointer to function that checks if two events are identical. [Default: Check by event-ID]
        * merge_func: Pointer to function that merges the events. [Default: Only merge event-dates]
        * verbose: Flag, defines if merged events shall be printed
    """
    # Merging functions
    def sameID(eventA, eventB):
        """Checks if two events are duplicate by their ID"""
        return eventA.id == eventB.id
    def mergeDate(eventA, eventB):
        """Merges two events by appending only their date"""
        eventA.date += ' & ' + eventB.date
        return eventA

    # Fallback: If no check/merging functions given, use the default (merge if same ID; merge by date)
    if check_duplicate_func is None:
        check_duplicate_func = sameID
    if merge_func is None:
        merge_func = mergeDate

    # Loop over entire event array
    i = 0
    while i < len(events):
        eventA = events[i]
        j = i + 1
        while j < len(events):
            eventB = events[j]
            if check_duplicate_func(eventA, eventB):
                eventA = merge_func(eventA, eventB)
                events[i] = eventA
                if verbose:
                    print("Merged events:\n\teventA: {}\n\teventB: {}".format(eventA.url,eventB.url))
                    #print("Merged event:\n{}".format(eventA))
                del events[j]
                j -= 1
            j += 1
        i += 1
    return events
