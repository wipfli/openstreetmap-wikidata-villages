import requests
from credentials import username, password
import xml.etree.ElementTree as ET

session = requests.Session()
session.auth = (username, password)

r = session.put('https://api.openstreetmap.org/api/0.6/changeset/create', data='''
<osm>
	<changeset>
		<tag k="created_by" v="python script"/>
		<tag k="comment" v="Adds wikidata tags to place=village when the wikidata entry is less than 1 km away and has identical name"/>
	</changeset>
</osm>
''', headers={'Content-Type': 'application/xml'})
print(r.text)

changeset = r.text

with open('output.csv') as f:
    lines = f.readlines()[1:] 
    for line in lines:
        name, osm_id, suggested_wikidata_id, distance_in_m = line.split(',')
        print(osm_id)
        r = session.get(f'https://api.openstreetmap.org/api/0.6/node/{osm_id}')
        text = r.text
        root = ET.fromstring(text)
        root[0].set('changeset', str(changeset))
        root[0].append(ET.Element('tag', {'k': 'wikidata', 'v': f'{suggested_wikidata_id}'}))
        r = session.put(f'https://api.openstreetmap.org/api/0.6/node/{osm_id}', data=ET.tostring(root), headers={'Content-Type': 'application/xml'})
        print(r.status_code, r.text)

r = session.put(f'https://api.openstreetmap.org/api/0.6/changeset/{changeset}/close')
print(r.status_code, r.text)
