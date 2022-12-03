import json
from copy import deepcopy
from geopy import distance

with open('overpass.json') as f:
    overpass_data = json.load(f)

untagged_villages = [element for element in overpass_data['elements'] if 'wikidata' not in element['tags']]

wikidata_municipalities = []
with open('wikidata.csv') as f:
    lines = f.readlines()[1:]
    for line in lines:
        link, name, point = line.split(',')
        wikidata = link.split('/')[-1]
        lon, lat = point.split(' ')
        lon = float(lon[6:])
        lat = float(lat[:-2])
        wikidata_municipalities.append({
            'lat': lat,
            'lon': lon,
            'tags': {
                'name': name,
                'wikidata': wikidata
            }
        })

matched_villages = []

for untagged_village in untagged_villages:
    suggestions = []
    for wikidata_municipality in wikidata_municipalities:
        if 'name' in untagged_village['tags'] and wikidata_municipality['tags']['name'] == untagged_village['tags']['name']:
            suggestions.append(deepcopy(wikidata_municipality))
            suggestions[-1]['tags']['@distance'] = distance.distance(
                (untagged_village['lat'], untagged_village['lon']),
                (wikidata_municipality['lat'], wikidata_municipality['lon'])
            ).km
    suggestions.sort(key=lambda suggestion: suggestion['tags']['@distance'])
    if len(suggestions) > 0 and suggestions[0]['tags']['@distance'] < 1.0:
        matched_village = deepcopy(untagged_village)
        matched_village['tags']['wikidata'] = suggestions[0]['tags']['wikidata']
        matched_village['tags']['@distance'] = suggestions[0]['tags']['@distance']
        matched_villages.append(matched_village)

matched_villages.sort(key=lambda village: village['tags']['@distance'])
with open('output.csv', 'w') as f:
    f.write('name,osm_id,suggested_wikidata_id,distance_in_m\n')
    for matched_village in matched_villages:
        f.write(f'{matched_village["tags"]["name"]},{matched_village["id"]},{matched_village["tags"]["wikidata"]},{matched_village["tags"]["@distance"]*1000:.0f}\n')
