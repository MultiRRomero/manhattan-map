import datetime
import sqlite3

class DBStore:
  def __init__(self):
    self._conn = sqlite3.connect('apartment_data.db')

  def save_address(self, address, latitude, longitude):
    self._conn.execute(
      'INSERT INTO addresses (address, latitude, longitude) ' +
      'VALUES (?, ?, ?)',
      (address, latitude, longitude)
      )
    self._conn.commit()

  def save_apartment(self, apartment):
    self._conn.execute(
      'INSERT INTO apartments ' +
      '(source, title, price, url, address_id,' +
      ' has_fee, blurb, posting_date, sqft, broker, brokerage) ' +
      'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ',
      (apartment.source,
       apartment.title,
       apartment.price,
       apartment.url,
       apartment.get_address_id(),
       apartment.has_fee,
       apartment.blurb,
       apartment.posting_date,
       apartment.sqft,
       apartment.broker)
      )
    self._conn.commit()

  def save_transaction(self, apartments):
    timestamp = int(datetime.datetime.now().strftime('%s'))
    log_values = map(
      lambda a: (timestamp, self.get_apartment_id(a)),
      apartments)
    self._conn.executemany(
      'INSERT INTO search_log (timestamp, apartment_id) VALUES (?, ?)',
      log_values
      )
    self._conn.commit()

  def get_apartment_full_data(self, url):
    cursor = self._conn.execute(
      'SELECT address_id, has_fee, blurb, posting_date, sqft, broker, brokerage ' +
      'FROM apartments WHERE url=?',
      (url, )
      )
    return cursor.fetchone()

  def get_address_from_id(self, id):
    cursor = self._conn.execute(
      'SELECT latitude, longitude, address FROM addresses WHERE id=?',
      (id, )
      )
    return cursor.fetchone()

  def get_id_for_address(self, lat, long, address):
    if lat != None and long != None:
      sql = 'SELECT id FROM addresses WHERE latitude=? AND longitude=?'
      data = (lat, long)
    else:
      sql = 'SELECT id FROM addresses WHERE address=?'
      data = (address,)
    cursor = self._conn.execute(sql, data)
    return cursor.fetchone()

  def get_apartment_id(self, listing):
    cursor = self._conn.execute('SELECT id FROM apartments WHERE url=?', (listing.url, ))
    return cursor.fetchone()[0]

  def get_coords(self, address):
    cursor = self._conn.execute(
      'SELECT latitude, longitude FROM addresses WHERE address=?',
      (address, ) # Need trailing comma or it treats address as an array -_-
      )
    return cursor.fetchone()

  def get_address(self, lat, long):
    cursor = self._conn.execute(
      'SELECT address FROM addresses WHERE latitude=? AND longitude=?',
      (lat, long)
      )
    results = cursor.fetchone()
    return None if results == None else results[0]

  def update_broker(self, url, broker, brokerage):
    cursor = self._conn.execute(
      'UPDATE apartments SET broker=?, brokerage=? WHERE url=?',
      (broker, brokerage, url)
      )
    self._conn.commit()

  def save_annotations(self, annotations):
    self._conn.executemany(
      'INSERT INTO annotations ' +
      '(timestamp, url, rating, comments, contacted) ' +
      'VALUES (?, ?, ?, ?, ?)',
      annotations
      )
    self._conn.commit()

  """ This is for debugging """
  def get_all_stored_listings(self):
    from apartment import Apartment
    listings = []

    cursor = self._conn.execute('SELECT source, title, price, url FROM apartments')
    while True:
      data = cursor.fetchone()
      if data == None: break
      listings.append(Apartment(data[0], data[1], data[2], data[3]))
    return listings
