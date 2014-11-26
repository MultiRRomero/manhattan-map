import re

def advance_and_find(s, advance, start, end):
  pos = s.find(advance)
  if pos < 0: return (None, s)
  return find_in_between(s[pos:], start, end)

def find_in_between(s, start_marker, end_marker):
  start = s.find(start_marker)
  if start < 0: return (None, s)
  start += len(start_marker)

  end = s.find(end_marker, start + 1)
  if end < 0: return (None, s)

  return (s[start:end].strip(), s[end:])

def strip_tags(s):
  s = s.replace('<br>', '\n')
  s = s.replace('<br />', '\n')
  while True:
    start = s.find('<')
    if start < 0:
      break

    end = s.index('>', start)
    s = s[:start] + ' ' + s[end + 1:]

  s = s.replace('&#39;', "'")
  s = s.replace('&nbsp;', ' ')
  s = s.replace('&amp;', '&')
  s = re.sub(r'\n+', '\n', s)
  s = re.sub(r'\t+', ' ', s)
  s = re.sub(r'\ +', ' ', s)
  s = re.sub(r'(\n )+', '\n', s)
  return s.strip()

def fix_spaces(s):
  singly_spaced = re.sub(r'\s+', ' ', s)
  return re.sub(r'\s,', ',', singly_spaced)
