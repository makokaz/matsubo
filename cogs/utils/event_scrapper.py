"""Event scrapper

Scraps events from pre-defined websites.
"""

import sys
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import datetime, pytz
from dateutil.parser import parse as parse_date
import calendar
from .event import Event, mergeDuplicateEvents
from . import database


def grabPage(url: str):
    """Return html-code of a given url as soup"""
    uClient = urlopen(url)
    page_html = uClient.read()
    uClient.close()
    return soup(page_html, "html.parser")

def getTCDate(date):
    """Returns date_start, date_end, date_fuzzy of Tokyo Cheapo and Japan Cheapo Events"""
    # try:
    #     parse_date(date, default=datetime.datetime(1978, 1, 1, 0, 0), fuzzy_with_tokens=True)
    # except Exception:
    #     return '', '', 'Unknown'
    date = date.split(" ~ ")

    # Hotfix
    if len(date) > 1:
        try:
            date_start, fuzzy = parse_date(date[0], default=datetime.datetime(datetime.datetime.now().year, 1, 1, 0, 0, tzinfo=pytz.timezone('Asia/Tokyo')), fuzzy_with_tokens=True)
        except Exception:
            date[0] = date[0] + ' ' + date[1].split()[1]

    date_start, fuzzy = parse_date(date[0], default=datetime.datetime(datetime.datetime.now().year, 1, 1, 0, 0, tzinfo=pytz.timezone('Asia/Tokyo')), fuzzy_with_tokens=True)
    date_start = date_start.date()
    fuzzy = [a.strip() for a in fuzzy]
    date_end = date_start
    if fuzzy[0]:
        if fuzzy[0].strip() == 'Early':
            pass
        if fuzzy[0].strip() == 'Mid':
            date_start = parse_date(f"{date_start.year}-{date_start.month}-{'15'}").date()
        if fuzzy[0].strip() == 'End' or fuzzy[0].strip() == 'Late':
            date_start = parse_date(f"{date_start.year}-{date_start.month}-{'20'}").date()
    if len(date) > 1:
        date_end, fuzzy = parse_date(date[1], default=datetime.datetime(datetime.datetime.now().year, 1, 1, 0, 0, tzinfo=pytz.timezone('Asia/Tokyo')), fuzzy_with_tokens=True)
        date_end = date_end.date()
        fuzzy = [a.strip() for a in fuzzy]
        if fuzzy[0]:
            if fuzzy[0].strip() == 'Early':
                date_end = parse_date(f"{date_end.year}-{date_end.month}-{'10'}").date()
            if fuzzy[0].strip() == 'Mid':
                date_end = parse_date(f"{date_end.year}-{date_end.month}-{'20'}").date()
            if fuzzy[0].strip() == 'End' or fuzzy[0].strip() == 'Late':
                date_end = parse_date(f"{date_end.year}-{date_end.month}-{calendar.monthrange(date_end.year, date_end.month)[1]}").date()
    if fuzzy[0] not in ['Early', 'Mid', 'End', 'Late']:
        fuzzy[0] = ''
    date_fuzzy = " ~ ".join(date) if fuzzy[0] else ''
    return date_start, date_end, date_fuzzy
    

def getTCTime(time):
    """Returns time_start and time_end of Tokyo Cheapo and Japan Cheapo Events"""
    time = time.split(" – ")
    if not time[0]:
        return '', ''
    time_start = parse_date(time[0], default=datetime.datetime(datetime.datetime.now().year, 1, 1, 0, 0, tzinfo=pytz.timezone('Asia/Tokyo'))).timetz()
    time_end = ''
    if len(time) > 1:
        time_end = parse_date(time[1], default=datetime.datetime(datetime.datetime.now().year, 1, 1, 0, 0, tzinfo=pytz.timezone('Asia/Tokyo'))).timetz()
    return time_start, time_end


def getEventsTC():
    """Return events from Tokyo Cheapo"""
    # Fetch soup from TokyoCheapo
    url = 'https://tokyocheapo.com/events/'
    page = grabPage(url)
    event_soup = page.findAll("article",{"class":"article card card--event"})
    # Identify events in soup
    events = []
    for event_ in event_soup:
        # Process date & Time
        date=event_.findAll("div", class_="card--event__date-box")[0].div.text.strip().replace("\n"," ")
        time=', '.join([t.parent.span.text.strip() for t in event_.findAll("div", title="Start/end time")])
        date_start, date_end, date_fuzzy = getTCDate(date)
        time_start, time_end = getTCTime(time)

        # Create event-object
        event = Event(
            id='TC'+event_.findAll(attrs={"data-post-id" : True})[0]['data-post-id'].strip(),
            name=event_.findAll("h3", class_="card__title")[0].text.strip(),
            description=event_.findAll("p", class_="card__excerpt")[0].text.strip(),
            url=event_.findAll("h3", class_="card__title")[0].a['href'],
            img=event_.findAll("a",  class_="card__image")[0].img,
            date_start=date_start,
            date_end=date_end,
            date_fuzzy=date_fuzzy,
            time_start=time_start,
            time_end=time_end,
            location=', '.join([loc.text for loc in event_.findAll("a", class_="location")]),
            cost=', '.join([cost.parent.text.strip() for cost in event_.findAll("div", title="Entry")]),
            status=', '.join([stat.text.strip().lower() for stat in event_.findAll("div", class_="event-status")]),
            visibility='Kanto',
            source='Web:TokyoCheapo')
        if event.img is not None: # Hotfix
            event.img = event.img['data-src']
        events.append(event)
    # merge duplicate events: Merge date, check by ID
    #events = mergeDuplicateEvents(events,verbose=True)
    return events

def getEventsJC():
    """Return events from Japan Cheapo"""
    regions = {
        'Chubu': ['Niigata','Ishikawa','Fukui','Yamanashi','Nagano','Gifu','Shizuoka','Aichi'],
        'Chugoku': ['Shimane','Okayama','Hiroshima','Yamaguchi'],
        'Hokkaido': ['Hokkaido'],
        'Kansai': ['Mie','Shiga','Kyoto','Osaka','Hyogo','Nara','Wakayama'], # Himeji, Kobe are also options, but are also included in Hyogo
        'Kanto': ['Tochigi'], # Tokyo, Ibaraki, Gunma... are left out because they are published on Tokyo Cheapo
        'Kyushu': ['Fukuoka','Saga','Nagasaki','Kumamoto','Oita','Miyazaki'],
        'Okinawa': ['Okinawa'],
        'Shikoku': ['Tokushima','Kagawa'],
        'Tohoku': ['Aomori','Iwate','Miyagi','Akita','Yamagata','Fukushima'],
        }
    # setup toolbar
    WIDTH_PROGRESSBAR = len(regions)
    sys.stdout.write("Progress: [%s]" % (" " * len(regions)))
    sys.stdout.flush()
    sys.stdout.write("\b" * (len(regions)+1)) # return to start of line, after '['
    # Crawl events
    events = []
    for i, region in enumerate(regions):
        for prefecture in regions[region]:
            # Fetch soup from JapanCheapo
            url = 'https://japancheapo.com/events/location/' + prefecture.lower()
            page = grabPage(url)
            event_soup = page.findAll("article",{"class":"article card card--event"})
            # Identify events in soup
            prefecture_events = []
            for event_ in event_soup:
                # Process date & Time
                date=event_.findAll("div", class_="card--event__date-box")[0].div.text.strip().replace("\n"," ")
                time=', '.join([t.parent.span.text.strip() for t in event_.findAll("div", title="Start/end time")])
                date_start, date_end, date_fuzzy = getTCDate(date)
                time_start, time_end = getTCTime(time)

                # Create event-object
                event = Event(
                    id='JC'+event_.findAll(attrs={"data-post-id" : True})[0]['data-post-id'].strip(),
                    name=event_.findAll("h3", class_="card__title")[0].text.strip(),
                    description=event_.findAll("p", class_="card__excerpt")[0].text.strip(),
                    url=event_.findAll("h3", class_="card__title")[0].a['href'],
                    img=event_.findAll("a",  class_="card__image")[0].img,
                    date_start=date_start,
                    date_end=date_end,
                    date_fuzzy=date_fuzzy,
                    time_start=time_start,
                    time_end=time_end,
                    location=', '.join([loc.text for loc in event_.findAll("a", class_="location")]),
                    cost=', '.join([cost.parent.text.strip() for cost in event_.findAll("div", title="Entry")]),
                    status=', '.join([stat.text.strip().lower() for stat in event_.findAll("div", class_="event-status")]),
                    visibility=region,
                    source='Web:JapanCheapo')
                if event.img is not None: # Hotfix
                    event.img = event.img['data-src']
                prefecture_events.append(event)
            # merge duplicate events: Merge date, check by ID
            #prefecture_events = mergeDuplicateEvents(prefecture_events)
            events.extend(prefecture_events)
        # Update progressbar
        sys.stdout.write("-")
        sys.stdout.flush()
    sys.stdout.write("]\n") # this ends the progress bar
    return events

def getEvents() -> list[Event]:
    """Scraps all event sources. Returns list of scrapped events."""
    events  = []
    events += getEventsTC()
    #events += getEventsJC()

    # Print events
    # print("Found the following events:")
    # for event in events:
    #    print(event)

    # TODO: In JapanCheapo, a few events might happen on the border of 2 cities and are thus seen in both cities/categories/visibility. Merge these events before
    # events = mergeDuplicateEvents(events)
    return events


# START OF PROGRAM
if __name__ == "__main__":
    # Crawl events
    events = getEvents()
    database.eventDB.insertEvents(events)
    


# TODO:
# - Extend crawled websites: Global Komaba, Todai ISSR, EMail, Facebook, ...
# - Handle the status 'postponed' correctly in the database (currently, it believes a new event is created...)
