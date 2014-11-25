import math
from subway_data import subway_data

def getDistanceToNearestSubwayStop(lat, lng, subwayLines = ['6','R','L']):
  structs = getAllSubwayStructsForLines(subwayLines)
  dists = map(lambda s: manhattanDistMeters(lat, lng, s['lat'], s['lng']), structs)
  zipped = zip(dists, structs)
  return reduce(lambda a,b: a if a[0]<b[0] else b, zipped)

def getAllSubwayStructsForLines(lines):
  return filter(lambda s: len(filter(lambda l: l in s['lines'], lines)), subway_data)

def manhattanDistMeters(lat1, lng1, lat2, lng2, axisTiltRadians = 29 * math.pi/180):
  metersPerLat = 111049.43673993941 # at NYC's latitude; got these from an online calc
  metersPerLng = 84426.94296769376

  dy = (lat1 - lat2) * metersPerLat
  dx = (lng1 - lng2) * metersPerLng

  dist = math.sqrt(dy*dy + dx*dx)
  angle = math.atan2(dy, dx) + axisTiltRadians # rotate

  return dist * (abs(math.sin(angle)) + abs(math.cos(angle)))
