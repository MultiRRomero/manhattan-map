import argparse
import sys
import termcolor

from craigslist import CLDataLoader
from db_store import DBStore
from manhattan_dist import get_distance_to_nearest_subway_stop
from nybits import NYBitsLoader
from renthop import RenthopLoader

DATA_SOURCE_TEST = 'test'
DATA_SOURCE_REAL = 'real'

OUTPUT_DEBUG = 'debug'
OUTPUT_CSV = 'csv'

MAX_DIST_MILES = .3
METERS_IN_MILE = 1609.344

def main(data_source, output, distance):
  if data_source == DATA_SOURCE_TEST:
    listings = _get_test_listings()
  else:
    listings = _get_listings()
    DBStore().save_transaction(listings)

  meters_distance = METERS_IN_MILE * distance
  listings = filter(lambda l: l.stop_distance < meters_distance, listings)

  if output == OUTPUT_DEBUG:
    _print_out(listings)
  else:
    # TODO: Implement Real Output
    pass

def _print_out(listings):
  aggregated = _aggregate_by(listings,
                             lambda l: l.stop['stop'],
                             lambda l: (l.price,l.has_fee,l.title)) # for now, these 3 fields

  for stop in aggregated:
    print '===== %s =====\n' % stop

    price_fee_title_s = aggregated[stop].keys()
    price_fee_title_s.sort()

    for price_fee_title in price_fee_title_s:
      for listing in aggregated[stop][price_fee_title]:
        (first, second) = listing.get_str_lines()
        if listing is aggregated[stop][price_fee_title][0]: # first
          print first # print first line (price+fee+title)

        color = None
        if 'craigslist.org' in second: color = 'red'
        if 'renthop.com'    in second: color = 'blue'
        print termcolor.colored(second, color) # print second line (url)

      print
    print '\n'

def _aggregate_by(array, *fns):
  ret = {}
  for elem in array:
    keys = map(lambda fn: fn(elem), fns)

    container = ret
    for k in keys:
      if k not in container:
        container[k] = {} if (k is not keys[-1]) else [] # if last key, then array
      container = container[k]

    container.append(elem)
  return ret
    
def _get_listings():
  loaders = [
    CLDataLoader(),
    NYBitsLoader(),
    RenthopLoader(),
    ]
  all_listings = map(lambda l: l.load_data(), loaders)
  return reduce(lambda a, b: a + b, all_listings)

def _get_test_listings():
  return DBStore().get_all_stored_listings()

parser = argparse.ArgumentParser(description='Apartments stuff')
parser.add_argument(
  '--source',
  dest='data_source',
  default=DATA_SOURCE_TEST,
  help='[test, real]'
  )
parser.add_argument(
  '--out',
  dest='output',
  default=OUTPUT_DEBUG,
  help='[debug, csv]'
  )
parser.add_argument(
  '--within',
  dest='distance',
  default=MAX_DIST_MILES,
  help='Required distance from subway stop (miles)'
  )

args = parser.parse_args()
main(args.data_source, args.output, float(args.distance))
