"""Validate local data, refresh browser bundle, and report omissions. No dependencies."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'data/players.json').read_text(encoding='utf-8'))
ps=data['players']
for p in ps:
 assert p['name'] and p['url'].startswith('https://en.wikipedia.org/wiki/'),p
 for coords in [p['coords']]+[c['coords'] for c in p['clubs']]:
  if coords:assert len(coords)==2 and -90<=coords[0]<=90 and -180<=coords[1]<=180,coords
 assert p['ajax'] and all(a<=b for a,b in p['ajax']),p
 for c in p['clubs']:assert c['start']<=c['end']<=2025,c
report={'players':len(ps),'mappedBirthplaces':sum(bool(p['coords']) for p in ps),'distinctMappedBirthplaces':len({tuple(p['coords']) for p in ps if p['coords']}),'playersWithClubHistory':sum(bool(p['clubs']) for p in ps),'clubSpells':sum(len(p['clubs']) for p in ps),'mappedClubSpells':sum(bool(c['coords']) for p in ps for c in p['clubs']),'missingBirthplaces':[{'name':p['name'],'birthplace':p['birthplace'],'source':p['url']} for p in ps if not p['coords']],'missingClubHistories':[{'name':p['name'],'source':p['url']} for p in ps if not p['clubs']]}
(root/'data/coverage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'data/players.js').write_text('window.AJAX_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';',encoding='utf-8')
print({k:v for k,v in report.items() if not isinstance(v,list)})
