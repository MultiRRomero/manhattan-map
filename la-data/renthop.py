import datetime

from apartment import Apartment
from browser import get_browser, open_page
from geocode import get_address
import html_helper

SOURCE = 'renthop'

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
#  'has_floorplan',
  ]
FEATURES = [
  'Doorman',
  'Elevator',
  'Fitness Center',
  ]
NEIGHBORHOOD_FEATURES = [
  FEATURES,
  ['Doorman'],
  ['Doorman'],
  ]

BASE_URL = 'http://www.renthop.com/search/new-york-city-ny?'

PAGE_PLACE_MARKER = '"page_input_box"'
TITLE_PLACE_MARKER = '"listing-title-link"'

class RenthopLoader:
  def __init__(self):
    self._br = get_browser()

  def _get_url(self, neighborhood, page=1):
    nsids = []
    nsnames = []
    for id in CHOOSE_NEIGHBOORHOODS:
      nsids.append(str(NEIGHBORHOOD_IDS[id]))
      nsnames.append(NEIGHBORHOOD_NAMES[id])

    params = [
      'bedrooms[]=1',
      'neighborhoods_str=%d' % NEIGHBORHOOD_IDS[neighborhood],
      'sort=hopscore',
      'page=%d' % page,
      'search=0',
      ]
    params += 'neighborhoods[]=%s' % NEIGHBORHOOD_NAMES[neighborhood]
    params += map(lambda i: 'features[]=%s' % i, NEIGHBORHOOD_FEATURES[neighborhood])
    params += map(lambda i: '%s=on' % i, FILTERS)

    all = '&'.join(params).replace(' ', '%20')
    return BASE_URL + all

  def _load_page(self, neighborhood, page):
    s = open_page(self._br, self._get_url(neighborhood, page))

    (total_pages, s) = html_helper.advance_and_find(s, PAGE_PLACE_MARKER, 'of', '(')
    total_pages = int(total_pages.strip())

    listings = []
    while True:
      (listing, s) = self._find_listing(s)
      if listing == None:
        break
      if listing.price <= MAX_PRICE:
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
    dt = self._understand_recency(recency, url)

    listing = Apartment(SOURCE, title, price, url)
    listing.set_posting_timestamp(dt.strftime('%s'))
    return (listing, s)

  def _understand_recency(self, recency, url):
    now = datetime.datetime.now()
    try:
      number = int(recency.split(' ')[0])
    except:
      print 'error parsing %s for %s' % (recency, url)
      return now

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
    if listing.is_fully_loaded():
      return
    s = open_page(self._br, listing.url)

    (broker, s) = html_helper.advance_and_find(s, 'Save to Favorites', '<span class="bold">', '</span>')
    (brokerage, s) = html_helper.advance_and_find(s, 'Brokerage: ', '<span class="bold">', '</span>')
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
    address = get_address(lat, long)
    listing.set_location(lat, long, address)
    listing.set_broker(broker)
    listing.set_brokerage(brokerage)
    listing.save_to_db()

  def _load_neighborhood_data(self, neighborhood):
    (listings, total_pages) = self._load_page(neighborhood, 1)
    print 'renthop has %d pages for %s' % (total_pages, NEIGHBORHOOD_NAMES[neighborhood])

    for page in range(2, total_pages + 1):
      (page_listings, _) = self._load_page(neighborhood, page)
      listings += page_listings

    map(lambda i: self._load_details(i), listings)
    return listings

  def get_brokers(self, listings):
    brokers = {}
    for listing in listings:
      self._load_details(listing)
      brokers[listing.url] = (listing.broker, '') # TODO: brokerage
    return brokers

  def load_data(self):
    all_listings = [self._load_neighborhood_data(i) for i in range(len(NEIGHBORHOOD_NAMES))]
    return reduce(lambda a, b: a + b, all_listings)

if __name__ == '__main__':
  listings = RenthopLoader().load_data()
  print "\n\n".join(map(lambda i: str(i), listings))
