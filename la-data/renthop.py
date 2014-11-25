import datetime

from apartment import Apartment
from browser import get_browser
from geocode import get_latlong
import html_helper

MIN_PRICE = 2300
MAX_PRICE = 4300

NEIGHBORHOOD_NAMES = [
    'Upper East Side', # 29
    'West Village', # 39
    'East Village', # 35
    ]
NEIGHBORHOOD_IDS = [
    29,
    39,
    35,
    ]
CHOOSE_NEIGHBOORHOODS = [0, 1, 2]

FILTERS = [
    'has_photo',
    'has_floorplan',
    ]
FEATURES = [
    'Doorman',
    'Elevator',
    'Fitness Center',
    ]

BASE_URL = 'http://www.renthop.com/search/new-york-city-ny?'

PAGE_PLACE_MARKER = '"page_input_box"'
TITLE_PLACE_MARKER = '"listing-title-link"'

class RenthopLoader:
    def __init__(self):
        self._br = get_browser()

    def _get_url(self, page=1):
        nsids = []
        nsnames = []
        for id in CHOOSE_NEIGHBOORHOODS:
            nsids.append(str(NEIGHBORHOOD_IDS[id]))
            nsnames.append(NEIGHBORHOOD_NAMES[id])

        params = [
            'bedrooms[]=1',
            'neighborhoods_str=' + ','.join(nsids),
            'sort=hopscore',
            'page=%d' % page,
            'search=0',
            ]
        params += map(lambda i: 'neighborhoods[]=%s' % i, nsnames)
        params += map(lambda i: 'features[]=%s' % i, FEATURES)
        params += map(lambda i: '%s=on' % i, FILTERS)

        all = '&'.join(params).replace(' ', '%20')
        return BASE_URL + all

    def _load_page(self, page):
        resp = self._br.open(self._get_url(page))
        s = resp.read()
        resp.close()

        (total_pages, s) = html_helper.advance_and_find(s, PAGE_PLACE_MARKER, 'of', '(')
        total_pages = int(total_pages.strip())

        listings = []
        while True:
            (listing, s) = self._find_listing(s)
            if listing == None:
                break
            listings.append(listing)
        return (listings, total_pages)

    def _find_listing(self, s):
        (url, s) = html_helper.advance_and_find(s, TITLE_PLACE_MARKER, 'href="', '"')
        (title, s) = html_helper.find_in_between(s, '>', '<')
        if url == None or title == None:
            return (None, s)
        title = html_helper.strip_tags(title)

        (price, s) = html_helper.advance_and_find(s, 'color-fg-green', '$', '<')
        price = int(float(price.strip().replace(',', '')))

        (_, s) = html_helper.advance_and_find(s, '<td', '', '<div')
        (recency, s) = html_helper.advance_and_find(s, '"bold font-size-100"', '>', '</div')
        recency = html_helper.strip_tags(recency).lower()
        dt = self._understand_recency(recency)

        listing = Apartment(title, price, url)
        listing.set_posting_date(dt.strftime('%s'))
        return (listing, s)

    def _understand_recency(self, recency):
        now = datetime.datetime.now()
        number = int(recency.split(' ')[0])

        if 'sec' in recency:
            return now - datetime.timedelta(seconds=number)
        if 'min' in recency:
            return now - datetime.timedelta(minutes=number)
        if 'hour' in recency:
            return now - datetime.timedelta(hours=number)
        if 'day' in recency:
            return now - datetime.timedelta(days=number)
        if 'week' in recency:
            return now - datetime.timedelta(days=7 * number)

        print 'unknown recency:', recency
        return now

    def _load_details(self, listing):
        resp = self._br.open(listing.url)
        s = resp.read()
        resp.close()

        (features, s) = html_helper.find_in_between(s, 'Features &amp; Amenities', '<div style="width: 640px')
        blurb = html_helper.strip_tags(features.replace('<td', '\n<td'))

        has_no_fee = 'No Fee\n' in blurb
        listing.set_has_fee(not has_no_fee)

        (desc, s) = html_helper.find_in_between(s, '  Description', '<div id="panels"')
        if desc != None:
            blurb += '\n\n' + html_helper.strip_tags(desc)
        listing.set_blurb(blurb)

        (address, s) = html_helper.find_in_between(s, "var report_listing_address = '", "'")
        (long, s) = html_helper.find_in_between(s, "longitude = '", "'")
        (lat, s) = html_helper.find_in_between(s, "latitude = '", "'")
        listing.set_location(lat, long, address)

    def load_data(self):
        (listings, total_pages) = self._load_page(1)
        for page in range(2, total_pages + 1):
            (page_listings, _) = self._load_page(page)
            listings += page_listings

        map(lambda i: self._load_details(i), listings)
        return listings

if __name__ == '__main__':
    listings = RenthopLoader().load_data()
    print "\n\n".join(map(lambda i: str(i), listings))