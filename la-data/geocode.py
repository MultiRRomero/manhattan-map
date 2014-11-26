from db_store import DBStore
import geopy

# Don't read this line:
API_KEY = 'AIzaSyBYjZNI2mPrku1dsJuv6Rd10cAL0wx3BV0'

_geos = None
_db = DBStore()

def _fill_geos():
  global _geos
  _geos = [
    geopy.geocoders.ArcGIS(),
    geopy.geocoders.OpenMapQuest(),
    geopy.geocoders.GoogleV3(API_KEY),
    ]

def get_latlong(address):
  saved_coords = _db.get_coords(address)
  if saved_coords != None:
    return saved_coords
  print 'cache miss', address

  coords = _get_geo_latlong(address)
  if coords != None:
    _db.save_address(address, coords[0], coords[1])
  return coords

def _get_geo_latlong(address):
  global _geos
  if _geos == None:
    _fill_geos()

  for geocoder in _geos:
    try:
      location = geocoder.geocode(address)
      if location != None:
        return (location.latitude, location.longitude)
    except:
      pass
  return None

def get_address(lat, long):
  (lat, long) = (str(lat), str(long))

  saved_address = _db.get_address(lat, long)
  if saved_address != None:
    return saved_address
  print 'cache miss', lat, long

  address = _get_geo_address(lat, long)
  if address != None:
    _db.save_address(address, lat, long)
  return address

def _get_geo_address(lat, long):
  global _geos
  if _geos == None:
    _fill_geos()

  for geocoder in _geos:
    try:
      location = geocoder.reverse('%s, %s' % (lat, long))
      if location != None:
        if isinstance(location, type([])):
          return location[0].address
        return location.address
    except:
      pass
  return None
