import json

from apartment import Apartment
from browser import get_browser, open_page
from craigslist_constants import Neighborhoods, Fees
import html_helper

SOURCE = 'craigslist'

MAX_PRICE = 4300
NEIGHBORHOODS = [
  Neighborhoods.UPPER_EAST_SIDE,
  Neighborhoods.EAST_VILLAGE,
  Neighborhoods.WEST_VILLAGE
]
SEARCH_QUERY = 'doorman'

CL_URL = 'http://newyork.craigslist.org/jsonsearch/%s/mnh?%s'
BASE_URL = 'http://newyork.craigslist.org'

SECTION_MARKER = '<section id="postingbody">'
SECTION_END = '</section'

class CLDataLoader:
  def __init__(self):
    self._params = self._form_params()
    self._browser = get_browser()

  def load_data(self):
    return self._load_data_fee(Fees.NO_FEE) + self._load_data_fee(Fees.FEE)

  def _form_params(self):
    params = map(lambda nh: 'nh=%d' % nh, NEIGHBORHOODS)
    params.append('query=%s' % SEARCH_QUERY)
    params.append('maxAsk=%d' % MAX_PRICE)
    params.append('hasPic=1')
    params.append('bedrooms=1')
    return '&'.join(params)

  def _load_data(self, fee, url_part=None):
    params = self._params
    if url_part != None:
      params = '%s&%s' % (url_part[url_part.find('?') + 1:], params)
    url = CL_URL % (fee, params)

    s = open_page(self._browser, url)
    return self._format_data(fee, json.loads(s)[0])

  def _format_data(self, fee, list):
    urls = []
    listings = []

    for item in list:
      if 'NumPosts' in item:
        urls.append(item['url'])
        continue

      bedrooms = int(float(item['Bedrooms']))
      if bedrooms != 1 or 'studio' in item['PostingTitle'].lower():
        continue

      apartment = Apartment(
        SOURCE,
        item['PostingTitle'],
        int(float(item['Ask'])),
        BASE_URL + item['PostingURL'])
      apartment.set_location(item['Latitude'], item['Longitude'])
      apartment.set_posting_timestamp(item['PostedDate'])
      apartment.set_has_fee(fee == Fees.FEE)
      listings.append(apartment)

    map(lambda listing: self._load_more_data(listing), listings)
    return (listings, urls)

  def _load_data_fee(self, fee):
    (listings, urls) = self._load_data(fee)

    # Decluster any clusters returned
    while len(urls) > 0:
      next_urls = []
      for url in urls:
        (new_lists, new_urls) = self._load_data(fee, url)
        listings += new_lists
        next_urls += new_urls
      urls = next_urls

    return listings

  def _load_more_data(self, listing):
    if listing.is_fully_loaded():
      return
    s = open_page(self._browser, listing.url)

    (section, s) = html_helper.find_in_between(s, SECTION_MARKER, SECTION_END)
    section = html_helper.strip_tags(section)
    listing.set_blurb(section)
    listing.save_to_db()

if __name__ == '__main__':
  listings = CLDataLoader().load_data()
  print ' ----- GOT %d LISTINGS ----- ' % len(listings)
  print "\n\n".join(map(lambda i: str(i), listings))
