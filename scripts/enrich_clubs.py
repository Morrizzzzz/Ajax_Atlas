"""Resolve missing club coordinates through explicit Wikidata stadium links (P115)."""
import json,subprocess,urllib.parse,collections
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
R=Path(__file__).resolve().parents[1]
r=json.loads((R/'data/coordinate_sources.json').read_text());p=json.loads((R/'data/players.json').read_text())
counts=collections.Counter(c['url'] for x in p['players'] for c in x['clubs'])
# Focus enrichment on repeated clubs; less common unlocated clubs stay in career lists.
clubs={u:r[u]['qid'] for u,n in counts.items() if n>=3 and r.get(u,{}).get('qid') and not r[u]['coords']}
def batch(ids):
 url='https://www.wikidata.org/w/api.php?'+urllib.parse.urlencode(dict(action='wbgetentities',ids='|'.join(ids),props='claims',format='json'))
 x=subprocess.run(['curl','-Ls','--compressed','--fail','--retry','1','--max-time','30',url],capture_output=True)
 try:return json.loads(x.stdout).get('entities',{})
 except:return {}
def entities(ids):
 out={};ids=list(set(ids))
 with ThreadPoolExecutor(max_workers=4) as pool:
  for f in as_completed([pool.submit(batch,ids[i:i+20]) for i in range(0,len(ids),20)]):out.update(f.result())
 return out
print('Club entities',len(clubs),flush=True)
e=entities(clubs.values());stadiums={}
for u,q in clubs.items():
 claims=e.get(q,{}).get('claims',{}).get('P115',[])
 # Use a current (no end date), non-deprecated venue if present, without inventing historical grounds.
 cs=[c for c in claims if c.get('rank')!='deprecated' and 'P582' not in c.get('qualifiers',{})]
 cs.sort(key=lambda c:c.get('rank')!='preferred')
 if cs:
  v=cs[0].get('mainsnak',{}).get('datavalue',{}).get('value',{})
  if 'id' in v:stadiums[u]=v['id']
print('Stadium entities',len(stadiums),flush=True)
se=entities(stadiums.values());added=0
for u,s in stadiums.items():
 cs=se.get(s,{}).get('claims',{}).get('P625',[])
 cs=[c for c in cs if c.get('rank')!='deprecated' and c.get('mainsnak',{}).get('datavalue')]
 if cs:
  c=cs[0]['mainsnak']['datavalue']['value'];r[u].update(coords=[c['latitude'],c['longitude']],source='https://www.wikidata.org/wiki/'+s,clubSource='https://www.wikidata.org/wiki/'+clubs[u],granularity='current stadium linked via Wikidata P115');added+=1
# Reload freshest player data after coordinate retry completes before running this script.
for x in p['players']:
 for c in x['clubs']:
  v=r.get(c['url'],{})
  if v.get('coords'):c['coords']=v['coords'];c['coordinateSource']=v['source'];c['coordinateType']=v['granularity']
(R/'data/coordinate_sources.json').write_text(json.dumps(r))
(R/'data/players.json').write_text(json.dumps(p,ensure_ascii=False,separators=(',',':')))
print('Additional mapped clubs',added,flush=True)
