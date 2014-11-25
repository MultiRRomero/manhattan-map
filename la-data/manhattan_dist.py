import math
from subway_data import subway_data

"""
  Returns: (distance in meters, subway stop data)
  Subway stop data has: lat, lng, stop (name), lines
  Lines is: string of all lines, i.e, '456'
"""
def get_distance_to_nearest_subway_stop(lat, lng, subway_lines = ['6','R','L']):
  structs = get_all_subway_structs_for_lines(subway_lines)
  dists = map(lambda s: manhattan_dist_meters(lat, lng, s['lat'], s['lng']), structs)
  zipped = zip(dists, structs)
  return reduce(lambda a,b: a if a[0]<b[0] else b, zipped)

def get_all_subway_structs_for_lines(lines):
  return filter(lambda s: len(filter(lambda l: l in s['lines'], lines)), subway_data)

def manhattan_dist_meters(lat1, lng1, lat2, lng2, axis_tilt_radians = 29 * math.pi/180):
  meters_per_lat = 111049.43673993941 # at NYC's latitude; got these from an online calc
  meters_per_lng = 84426.94296769376

  dy = (lat1 - lat2) * meters_per_lat
  dx = (lng1 - lng2) * meters_per_lng

  dist = math.sqrt(dy*dy + dx*dx)
  angle = math.atan2(dy,dx) + axis_tilt_radians # rotate

  return dist * (abs(math.sin(angle)) + abs(math.cos(angle)))
