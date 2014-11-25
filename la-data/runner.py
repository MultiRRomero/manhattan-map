import argparse
import sys

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
    by_subway = {}
    for listing in listings:
        stop = listing.stop['stop']
        if not stop in by_subway:
            by_subway[stop] = []
        by_subway[stop].append(listing)

    for stop in by_subway:
        print '===== %s =====' % stop
        for listing in by_subway[stop]:
            print str(listing)
        print '\n'
    
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
