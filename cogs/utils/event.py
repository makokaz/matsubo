"""Event class

Simple event class to define what attributes an event has, and other helpful functions like euqlity-checking.
"""

import calendar

from . import utils


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
        date_start = str(utils.custom_strftime('%b {S} ({DAY}), %Y', self.date_start))
        date_end = str(utils.custom_strftime('%b {S} ({DAY}), %Y', self.date_end)) if self.date_start != self.date_end else ''
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
    def sameIDDate(eventA:Event, eventB:Event):
        """Checks if two events are duplicate by their ID and start_date"""
        if not (eventA and eventB):
            utils.print_warning("One of the two events was `None`!")
            return False
        return eventA.id == eventB.id and eventA.date_start == eventB.date_start
    def mergeDate(eventA:Event, eventB:Event):
        """Merges two events by appending only their date"""
        if not (eventA and eventB):
            utils.print_warning("One of the two events was `None`!")
            if eventA:
                return eventA
            return eventB
        eventA.date += ' & ' + eventB.date
        return eventA
    def dontmerge(eventA:Event, eventB:Event):
        """Simply discards eventB. Does not merge metadata."""
        return eventA

    # Process mergefunc
    if type(merge_func) is str:
        merge_func = {'mergeDate':mergeDate,'dontmerge':dontmerge}.get(merge_func, dontmerge)

    # Fallback: If no check/merging functions given, use the default (merge if same ID; merge by date)
    if check_duplicate_func is None:
        check_duplicate_func = sameIDDate
    if merge_func is None:
        merge_func = dontmerge

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
