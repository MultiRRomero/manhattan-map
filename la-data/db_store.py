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

