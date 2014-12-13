from apartment import Apartment
from craigslist import CLDataLoader
from db_store import DBStore
from nybits import NYBitsLoader
from streeteasy import StreeteasyLoader
from renthop import RenthopLoader

URLS = [
    'http://www.renthop.com/listings/east_63rd_street/9j/4921841',
    'http://www.renthop.com/listings/east_12th_street/7m/5000300',
    ]

def main():
    # Bucket by source!
    renthop = []
    streeteasy = []
    nybits = []
    craigslist = []

    lollists = [renthop, streeteasy, nybits, craigslist]
    lolsources = [
        RenthopLoader(),
        StreeteasyLoader(),
        NYBitsLoader(),
        CLDataLoader(),
        ]

    for url in URLS:
        mock_listing = Apartment('source', 'title', 1234, url, True)
        if 'renthop.com' in url:
            renthop.append(mock_listing)
        elif 'streeteasy.com' in url:
            streeteasy.append(mock_listing)
        elif 'nybits.com' in url:
            nybits.append(mock_listing)
        elif 'craigslist.com' in url:
            craigslist.append(mock_listing)
        else:
            print 'wtf???????', url
            return

    brokers = {}
    db = DBStore()

    #    for i in range(len(lolsources)):
    for i in range(1):
        source_brokers = lolsources[i].get_brokers(lollists[i])
        print source_brokers
        for url in source_brokers:
            brokers[url] = source_brokers[url]
            db.update_broker(url, source_brokers[url][0], source_brokers[url][1])

    for url in URLS:
        print "%s\t%s" % brokers[url]
        
main()
