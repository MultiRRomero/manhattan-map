import datetime

from db_store import DBStore
from geocode import get_address
from manhattan_dist import get_distance_to_nearest_subway_stop

"""
" Just a simple class to keep namings between different apartment features consistent
"""

db = DBStore()

class Apartment:
  def __init__(self, source, title, price, url):
    self.title = title
    self.price = price
    self.url = url
    self.source = source
    self._init_from_db()

  def _init_from_db(self):
    global db
    data = db.get_apartment_full_data(self.url)
    if data == None:
      self.latitude = None
      self.longitude = None
      self.address = None
      self.has_fee = None
      self.blurb = ''
      self.posting_date = None
      self.sqft = -1
      self.address_id = None
      self.stop_distance = None
      self.stop = None
      self._has_full_data = False
    else:
      self._init_address_from_db(data[0])
      self.has_fee = data[1]
      self.blurb = data[2]
      self.posting_date = data[3]
      self.sqft = data[4]
      self._has_full_data = True

  def _init_address_from_db(self, address_id):
    global db
    data = db.get_address_from_id(address_id)
    self.address_id = address_id
    self.latitude = float(data[0])
    self.longitude = float(data[1])
    self.address = data[2]
    self._init_distance()

  def _init_distance(self):
    (distance, stop) = get_distance_to_nearest_subway_stop(self.latitude, self.longitude)
    self.stop_distance = distance
    self.stop = stop

  def get_address_id(self):
    if self.address_id != None:
      return self.address_id
    global db
    data = db.get_id_for_address(self.latitude, self.longitude, self.address)
    self.address_id = None if data == None else data[0]
    return self.address_id

  def is_fully_loaded(self):
    return self._has_full_data

  def save_to_db(self):
    global db
    self._has_full_data = True
    db.save_apartment(self)

  def set_location(self, latitude, longitude, address=None):
    self.latitude = float(latitude)
    self.longitude = float(longitude)

    if address == None:
      address = get_address(latitude, longitude)
    self.address = address
    self._init_distance()
    return self

  def set_address(self, address):
    self.address = address
    return self

  def set_has_fee(self, has_fee):
    self.has_fee = has_fee
    return self

  def set_posting_date(self, date):
    self.posting_date = date
    return self

  def set_posting_timestamp(self, timestamp):
    date_time = datetime.datetime.fromtimestamp(int(timestamp))
    self.posting_date = date_time.strftime('%d/%b/%Y')
    return self

  def set_sqft(self, sqft):
    self.sqft = sqft
    return self

  def set_blurb(self, blurb):
    self.blurb = blurb
    return self

  def get_str_lines(self):
    price = self.price if self.has_fee != True else '%d*' % self.price
    return ('%s\t%s' % (str(price), self.title),
            '\t%s'   % (self.url))

  def __str__(self):
    return '\n'.join(self.get_str_lines())
