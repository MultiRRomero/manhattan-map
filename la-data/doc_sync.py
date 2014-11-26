import datetime
import gspread

from db_store import DBStore

KEY = '1S1Wnhgn9EwuWnK2gFwjTwhIJDKr0hJrg-zzB9VTFw_s'
FILE = '.credentials.secret'

SEEN_COL = 0
URL_COL = 1

class DocSyncer:
  def __init__(self):
    self._credentials = self._get_credentials()
    self._last_seen = datetime.datetime.now().strftime('%d/%b %H:%M')

  def sync_listings(self, listings):
    ws = self._get_worksheet()
    sheet_data = self._get_sheet_data(ws)

    by_url = self._get_diff(listings, sheet_data)
    self._write_new_rows(ws, by_url)
    self._update_seen_time(ws, by_url)
    self._store_annotations(by_url)

  def _get_diff(self, listings, sheet_data):
    by_url = {}
    for listing in listings:
      by_url[listing.url] = (listing, None)
    for listing in sheet_data:
      key = listing[URL_COL]
      if key in by_url:
        by_url[key] = (by_url[key][0], listing)
      else:
        by_url[key] = (None, listing)
    return by_url

  def _write_new_rows(self, ws, by_url):
    added = filter(lambda i: i[1] == None, by_url.values())
    if len(added) == 0:
      return

    added_values = map(lambda item: item[0].get_row_values(self._last_seen), added)
    values = reduce(lambda a, b: a + b, added_values)

    cols = ws.col_values(1)
    end = chr(ord('A') + len(added_values[0]) - 1)
    list = ws.range('A%d:%s%d' % (len(cols) + 1, end, len(cols) + len(added)))

    for i in range(len(values)):
      list[i].value = values[i]
    ws.update_cells(list)

  def _update_seen_time(self, ws, by_url):
    cells = ws.range('A%d:B%d' % (2, len(by_url) + 1))
    i = 0
    while i < len(cells):
      (seen_cell, url_cell) = cells[i:i+2]
      i += 2

      (listing, existing) = by_url[url_cell.value]
      if listing != None:
        seen_cell.value = self._last_seen
    ws.update_cells(cells)

  def _store_annotations(self, by_url):
    now = int(datetime.datetime.now().strftime('%s'))
    annotations = []
    for key in by_url:
      (_, existing) = by_url[key]
      if existing == None:
        continue
      url = existing[URL_COL]
      (rating, comments, contacted) = existing[16:19]
      annotations.append((now, url, int(rating), comments, contacted))
    DBStore().save_annotations(annotations)

  def _get_credentials(self):
    f = open(FILE, 'r')
    s = f.read()
    f.close()
    return s.strip().split(',')

  def _get_worksheet(self):
    client = gspread.login(self._credentials[0], self._credentials[1])
    sheet = client.open_by_key(KEY)
    return sheet.get_worksheet(0)

  def _get_sheet_data(self, ws):
    rows = ws.get_all_values()
    return rows[1:] # Remove header row

