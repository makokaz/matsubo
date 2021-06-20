"""Event scrapper

Scraps events from pre-defined websites.
"""

import sys
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from event import Event, mergeDuplicateEvents
import database


def grabPage(url: str):
    """Return html-code of a given url as soup"""
    uClient = urlopen(url)
    page_html = uClient.read()
    uClient.close()
    return soup(page_html, "html.parser")

def getEventsTC():
    """Return events from Tokyo Cheapo"""
    # Fetch soup from TokyoCheapo
    url = 'https://tokyocheapo.com/events/'
    page = grabPage(url)
    event_soup = page.findAll("article",{"class":"article card card--event"})
    # Identify events in soup
    events = []
    for event_ in event_soup:
        event = Event(
            id='TC'+event_.findAll(attrs={"data-post-id" : True})[0]['data-post-id'].strip(),
            name=event_.findAll("h3", class_="card__title")[0].text.strip(),
            description=event_.findAll("p", class_="card__excerpt")[0].text.strip(),
            url=event_.findAll("h3", class_="card__title")[0].a['href'],
            img=event_.findAll("a",  class_="card__image")[0].img,
            date=event_.findAll("div", class_="card--event__date-box")[0].div.text.strip().replace("\n"," "),
            time=', '.join([t.parent.span.text.strip() for t in event_.findAll("div", title="Start/end time")]),
            location=', '.join([loc.text for loc in event_.findAll("a", class_="location")]),
            cost=', '.join([cost.parent.text.strip() for cost in event_.findAll("div", title="Entry")]),
            status=', '.join([stat.text.strip().lower() for stat in event_.findAll("div", class_="event-status")]),
            category='Kanto')
        if event.img is not None: # Hotfix
            event.img = event.img['data-src']
        events.append(event)
    # merge duplicate events: Merge date, check by ID
    events = mergeDuplicateEvents(events)
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
                event = Event(
                    id='JC'+event_.findAll(attrs={"data-post-id" : True})[0]['data-post-id'].strip(),
                    name=event_.findAll("h3", class_="card__title")[0].text.strip(),
                    description=event_.findAll("p", class_="card__excerpt")[0].text.strip(),
                    url=event_.findAll("h3", class_="card__title")[0].a['href'],
                    img=event_.findAll("a",  class_="card__image")[0].img,
                    date=event_.findAll("div", class_="card--event__date-box")[0].div.text.strip().replace("\n"," "),
                    time=', '.join([t.parent.span.text.strip() for t in event_.findAll("div", title="Start/end time")]),
                    location=', '.join([loc.text for loc in event_.findAll("a", class_="location")]),
                    cost=', '.join([cost.parent.text.strip() for cost in event_.findAll("div", title="Entry")]),
                    status=', '.join([stat.text.strip().lower() for stat in event_.findAll("div", class_="event-status")]),
                    category=region)
                if event.img is not None: # Hotfix
                    event.img = event.img['data-src']
                prefecture_events.append(event)
            # merge duplicate events: Merge date, check by ID
            prefecture_events = mergeDuplicateEvents(prefecture_events)
            events.extend(prefecture_events)
        # Update progressbar
        sys.stdout.write("-")
        sys.stdout.flush()
    sys.stdout.write("]\n") # this ends the progress bar
    return events


# START OF PROGRAM
if __name__ == "__main__":
    # Crawl events
    eventsTY = getEventsTC()
    eventsJC = getEventsJC()
    # Print events
    events = eventsTY + eventsJC
    for event in events:
       print(event)
    events = mergeDuplicateEvents(events)
    database.insertEvents(events)
    


# TODO:
# 1. Save events into Postgres
# 2. Write Discord bot
# 3. Extend crawled websites: Global Komaba, Todai ISSR, EMail, Facebook, ...