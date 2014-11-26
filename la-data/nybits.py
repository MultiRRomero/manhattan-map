import time

from apartment import Apartment
from browser import get_browser, open_page
from geocode import get_latlong
import html_helper

SOURCE = 'nybits'

MAX_PRICE = 4300
NEIGHBORHOODS = [
  'upper_east_side',
  'west_village',
  'east_village',
  ]

URL = 'http://www.nybits.com/search/?_a%21process=y&_rid_=3&_ust_todo_=65733&_xid_=ptCI9UDbvPJ7TP-1416803342&%21%21atypes=1br&%21%21rmin=&%21%21rmax=&doorman=on&elevator=on&%21%21fee=any&%21%21orderby=rent'

# List of apartments
MARKER = '"toprentalcell"'
LINK_START = 'HREF="'
FEE_START = '<b>'
LINE_END = '</td></tr>'

# Apartment details
COL_START = '<td>'
COL_END = '</td>'
BREAK = '<br>'
SQFT_MARKER = 'Size (sq/ft)'
BLDG_MARKER = '<b>Building</b>'
COMMENTS_MARKER = '<b>Comments</b>'

class NYBitsLoader:
  def __init__(self):
    self._url = self._get_url()
    self._br = get_browser()

  def load_data(self):
    listings = self._call_internets()
    print ' ----- GOT %d LISTINGS ----- ' % len(listings)
    return map(lambda listing: self._load_more_listing_data(listing), listings)

  def _get_url(self):
    params = [URL] + map(lambda i: '!!nsearch=%s' % i, NEIGHBORHOODS)
    return '&'.join(params)

  def _call_internets(self):
    s = open_page(self._br, self._url)
    return self._format(s)

  def _get_fields(self, s):
    start = s.find(MARKER)
    if start < 0:
      return (None, '')
    s = s[start + len(MARKER):]

    (price, s) = html_helper.find_in_between(s, '$', '<')
    price = int(float(price.replace(',', '')))
    if price > MAX_PRICE:
      return (None, '')

    (link, s) = html_helper.find_in_between(s, LINK_START, '"')
    (title, s) = html_helper.find_in_between(s, '>', '<')
    (fee_text, s) = html_helper.find_in_between(s, FEE_START, '<')
    no_fee = 'no' in fee_text.lower()

    ending = s.find(LINE_END)
    end_listing = s[:ending]
    start = end_listing.rfind('  ')
    posting_date = end_listing[start:].strip()

    listing = Apartment(SOURCE, title, price, link)
    listing.set_has_fee(not no_fee)
    listing.set_posting_date(posting_date)
    return (listing, s)

  def _format(self, s):
    listings = []
    while True:
      (next, s) = self._get_fields(s)
      if next == None:
        break
      listings.append(next)
    return listings

  def _load_more_listing_data(self, listing):
    if listing.is_fully_loaded():
      return listing
    s = open_page(self._br, listing.url)

    pos = s.find(SQFT_MARKER)
    if pos >= 0:
      (sqft, s) = html_helper.find_in_between(s[pos:], COL_START, COL_END)
      listing.set_sqft(int(sqft))

    s = s[s.find(BLDG_MARKER):]
    (address, s) = html_helper.find_in_between(s, COL_START, COL_END)
    self._set_formatted_address(address, listing)

    pos = s.find(COMMENTS_MARKER)
    if pos >= 0:
      (blurb, s) = html_helper.find_in_between(s[pos:], ':', '<div class="cleanbreakdiv">')
      listing.set_blurb(html_helper.strip_tags(blurb))

    listing.save_to_db()
    return listing
  
  def _set_formatted_address(self, address, listing):
    # Strip off first line if it has a building in it (>2 lines)
    num_breaks = address.count(BREAK)
    if num_breaks > 1:
      address = address[address.index(BREAK) + len(BREAK) :]

    # Strip out HTML tags, add NY if it's not there, fix extra spacing
    address = html_helper.strip_tags(address).replace('( map )', ', ')
    if num_breaks == 0:
      address += ', NY'
    address.replace('\n', ', ')
    address = html_helper.fix_spaces(address)

    location = get_latlong(address)
    if location != None:
      listing.set_location(location[0], location[1], address)
    else:
      listing.set_address(address)
      print 'error getting', address, listing.url

if __name__ == '__main__':
  listings = NYBitsLoader().load_data()
  print "\n\n".join(map(lambda i: str(i), listings))
