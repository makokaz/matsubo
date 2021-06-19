"""Event class

Simple event class to define what attributes an event has, and other helpful functions like euqlity-checking.
"""

class Event(object):
    def __init__(self,
            id='', # Unique ID for every event
            name='', # Event name
            description='', # Event description
            url='', # URL where event was found
            img='', # Image URL
            date='', # Date of event
            time='', # Time of event
            location='', # Event-Location
            cost='', # Entry-fee to event
            status='', # Cancelled, Online, ...
            category=''): # Prefecture, University, ... used for visibility to channels
        self.id = id
        self.name = name
        self.description = description
        self.url = url
        self.img = img
        self.date = date
        self.time = time
        self.location = location
        self.cost = cost
        self.status = status
        self.category = category

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.id == other.id
        return False

    def __str__(self):
        text = """***{name}*** [{id}]
        date: {date}
        time: {time}
        location: {location}
        cost: {cost}
        url: {url}
        image-url: {img}
        status: {status}
        category: {category}
        description: {description}"""
        return text.format(id=self.id,
            name=self.name,
            description=self.description,
            url=self.url,
            img=self.img,
            date=self.date,
            time=self.time,
            location=self.location,
            cost=self.cost,
            status=self.status,
            category=self.category)

def mergeDuplicateEvents(events, check_duplicate_func=None, merge_func=None, verbose=False):
    """
    Merges duplicate events in given list.
    Duplicate events happen when e.g. the same event is hold next week again.
    
    Optional arguments:
        * check_duplicate_func: Pointer to function that checks if two events are identical. [Default: Check by event-ID]
        * merge_func: Pointer to function that merges the events. [Default: Only merge event-dates]
        * verbose: Flag, defines if merged events shall be printed
    """
    def sameID(eventA, eventB):
        return eventA.id == eventB.id
    def mergeDate(eventA, eventB):
        eventA.date += ' & ' + eventB.date
        return eventA

    if check_duplicate_func is None:
        check_duplicate_func = sameID
    if merge_func is None:
        merge_func = mergeDate

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
                del events[j]
                j -= 1
            j += 1
        i += 1
    return events
