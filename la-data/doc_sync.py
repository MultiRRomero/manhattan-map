import datetime
import gspread

from db_store import DBStore

KEY = '1S1Wnhgn9EwuWnK2gFwjTwhIJDKr0hJrg-zzB9VTFw_s'
FILE = '.credentials.secret'

SEEN_COL = 0
URL_COL = 1

NEW_WS_INDEX = 0
NUM_WORKSHEETS = 5

class DocSyncer:
  def __init__(self):
    self._credentials = self._get_credentials()
    self._last_seen = datetime.datetime.now().strftime('%d/%b %H:%M')

  def sync_listings(self, listings):
    worksheets = self._get_worksheets()
    list_by_sheet = self._get_all_rows(worksheets)

    listings_rows = map(lambda i: i.get_row_values(self._last_seen), listings)
    keyed_new_data = self._index_by_url(listings_rows)

    self._write_new_rows(worksheets[NEW_WS_INDEX], keyed_new_data, list_by_sheet)
    self._update_seen_times(worksheets, list_by_sheet, keyed_new_data)
    self._store_annotations(list_by_sheet)

  def _find_new_rows(self, new_data, old_data):
    old_by_url = {}
    for sheet in old_data:
      for row in sheet:
        old_by_url[row[URL_COL]] = row
    missing = []
    for url in new_data:
      if not url in old_by_url:
        missing.append(new_data[url])
    return missing

  def _index_by_url(self, data):
    by_url = {}
    for row in data:
      by_url[row[URL_COL]] = row
    return by_url

  def _write_new_rows(self, ws, new_data, old_data_by_sheet):
    new_rows = self._find_new_rows(new_data, old_data_by_sheet)
    print 'found %d new rows' % len(new_rows)
    if len(new_rows) == 0:
      return
    new_cells = reduce(lambda a, b: a + b, new_rows)

    cols = ws.col_values(1)
    end = chr(ord('A') + len(new_rows[0]) - 1)
    list = ws.range('A%d:%s%d' % (len(cols) + 1, end, len(cols) + len(new_rows)))

    for i in range(len(new_cells)):
      list[i].value = new_cells[i]
    ws.update_cells(list)

  def _update_seen_times(self, worksheets, ws_data, new_data):
    for i in range(len(worksheets)):
      self._update_seen_time_for_sheet(worksheets[i], ws_data[i], new_data)

  def _update_seen_time_for_sheet(self, ws, old_data, new_data):
    if len(old_data) == 0:
      return
    cells = ws.range('A%d:A%d' % (2, len(old_data) + 1))

    for i in range(len(cells)):
      url = old_data[i][URL_COL]
      if url in new_data:
        cells[i].value = self._last_seen
    ws.update_cells(cells)

  def _store_annotations(self, data_by_sheet):
    now = int(datetime.datetime.now().strftime('%s'))
    annotations = []
    for sheet in data_by_sheet:
      for row in sheet:
        url = row[URL_COL]
        (rating, comments, contacted) = row[16:19]
        annotations.append((now, url, float(rating), comments, contacted))
    DBStore().save_annotations(annotations)

  def _get_credentials(self):
    f = open(FILE, 'r')
    s = f.read()
    f.close()
    return s.strip().split(',')

  def _get_worksheets(self):
    client = gspread.login(self._credentials[0], self._credentials[1])
    sheet = client.open_by_key(KEY)
    sheets = []
    for i in range(NUM_WORKSHEETS):
      sheets.append(sheet.get_worksheet(i))
    return sheets

  def _get_all_rows(self, worksheets):
    by_ws = []
    for ws in worksheets:
      rows = ws.get_all_values()
      by_ws.append(rows[1:]) # Remove header row
    return by_ws
