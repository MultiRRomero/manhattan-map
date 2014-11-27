import datetime

from apartment import Apartment
from browser import get_browser, open_page
from geocode import get_address
import html_helper

SOURCE = 'streeteasy'

MAX_PRICE = 4300
FEATURES = ['dishwasher', 'doorman']
AREAS = [
  117, # East Village
  116, # Greenwich Village
  157, # West Village
  139, # UES
  ]

HREF = 'href="'
SEPARATOR = "<span class='separator'>"
DETAILS_INFO = "<div class='details_info'"
DESCRIPTION = '<h2>Description</h2>'

BASE_URL = 'http://streeteasy.com'
URL = 'http://streeteasy.com/for-rent/nyc/status:open|price:-%d|area:%s|beds:1|amenities:%s?page=%d'

class StreeteasyLoader:
  def __init__(self):
    self._br = get_browser()

  def _get_url(self, page=1):
    return URL % (
      MAX_PRICE,
      ','.join(map(lambda i: str(i), AREAS)),
      ','.join(FEATURES),
      page,
      )

  def _get_result(self, s):
    (latlong, s) = html_helper.find_in_between(s, "se:map:point='", "'")
    if latlong == None:
      return (None, s)
    (lat, long) = latlong.split(',')

    end = s.find("<div class='photo'>")
    has_no_fee = 'banner no_fee' in s[:end]
    s = s[end:]

    (url, s) = html_helper.find_in_between(s, 'href="', '"')
    url = BASE_URL + url

    (title, s) = html_helper.advance_and_find(s, '"details-title">', '"true">', '<')
    (price, s) = html_helper.advance_and_find(s, "'price'", '$', '<')
    price = int(float(price.replace(',', '')))
    
    listing = Apartment(SOURCE, title, price, url)
    listing.set_location(float(lat), float(long))
    listing.set_has_fee(not has_no_fee)

    start = s.find("class='first_detail_cell'")
    section_end = s.find('</div', start)
    end = s[:section_end].find('&sup2;')
    if end >= 0:
      section = s[:end]
      start = section.rfind('>') + 1
      end = section.find(' ', start)
      listing.set_sqft(int(section[start:end].replace(',', '')))
      print listing.sqft

    return (listing, s)

  def _load_search_results(self, page):
    s = open_page(self._br, self._get_url(page))
    listings = []
    while True:
      (listing, s) = self._get_result(s)
      if listing == None:
        break
      listings.append(listing)

    end = s.find("<i class='icon-caret-right'>")
    section = s[:end]
    end = section.rfind(HREF)
    section = s[:end]
    start = section.rfind(HREF)
    section = s[start:]
    (num_pages, _) = html_helper.find_in_between(s[start:], '>', '<')

    return (listings, int(num_pages))

  def _load_full_data(self, listing):
    if listing.is_fully_loaded():
      return
    s = open_page(self._br, listing.url)

    (days, s) = html_helper.advance_and_find(s, '<h6>Days On Market</h6>', 'p>', ' day')
    post_timestamp = self._get_post_timestamp(days)

    (descr, s) = html_helper.find_in_between(s, '<h2>Description</h2>', '</section>')
    descr = html_helper.strip_tags(descr)

    (amenities, s) = html_helper.find_in_between(s, '<h2>Amenities</h2>', '</section>')
    amenities = amenities.replace('</li>', ', ').replace('</h6>', ': ').replace('<h6>', '\n')
    amenities = html_helper.strip_tags(amenities)
    amenities = amenities.replace("googletag.cmd.push(function() {googletag.display('ad_amenity');});", '')
    amenities = amenities.replace(' \n', ' ').replace(', \n', '. ')

    listing.set_blurb(descr + '\n\n' + amenities)
    listing.set_posting_timestamp(post_timestamp)
    listing.save_to_db()

  def _get_post_timestamp(self, days):
    now = datetime.datetime.now()
    return int((now - datetime.timedelta(days=int(days))).strftime('%s'))

  def load_data(self):
    (listings, total_pages) = self._load_search_results(1)
    print 'streeteasy has %d total pages' % total_pages

    for page in range(2, total_pages + 1):
      (page_listings, _) = self._load_search_results(page)
      listings += page_listings

    map(lambda i: self._load_full_data(i), listings)
    return listings

if __name__ == '__main__':
  loader = StreeteasyLoader()
  listings = loader.load_data()
  print "\n\n".join(map(lambda i: str(i), listings))
