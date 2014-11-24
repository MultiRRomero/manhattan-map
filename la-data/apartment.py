"""
" Just a simple class to keep namings between different apartment features consistent
"""

class Apartment:
    def __init__(self, title, price, url):
        self.title = title
        self.price = price
        self.url = url

        # Defaults
        self.latitude = None
        self.longitude = None
        self.has_fee = None
        self.blurb = ''
        self.posting_date = None
        self.posting_timestamp = None # TODO
        self.sqft = -1

    def set_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        return self

    def set_has_fee(self, has_fee):
        self.has_fee = has_fee
        return self

    def set_posting_date(self, date):
        self.posting_date = date
        return self

    def set_posting_timestamp(self, timestamp):
        # TODO: Convert to a format
        self.posting_timestamp = timestamp
        return self

    def set_sqft(self, sqft):
        self.sqft = sqft
        return self

    def set_blurb(self, blurb):
        self.blurb = blurb
        return self

    def __str__(self):
        price = self.price if self.has_fee != True else '%d*' % self.price
        return '%s\t%s\n\t%s' % (str(price), self.title, self.url)
