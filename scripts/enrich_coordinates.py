"""Batch MediaWiki coordinate lookup, with per-entity provenance. Python standard library only."""
import json,subprocess,urllib.parse,time,re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parents[1]
ps=json.loads((ROOT/'data/profiles.json').read_text())
urls=sorted(set(p['birthURL'] for p in ps if p['birthURL'])|{c['url'] for p in ps for c in p['clubs']})
def get(params):
 u='https://en.wikipedia.org/w/api.php?'+urllib.parse.urlencode(params)
 r=subprocess.run(['curl','-Ls','--fail','--retry','2','--retry-delay','1','--max-time','25',u],capture_output=True)
 try:return json.loads(r.stdout)
 except:return {}
def batch(us):
 titles=[urllib.parse.unquote(u.split('/wiki/')[-1]).replace('_',' ') for u in us]
 d=get(dict(action='query',format='json',titles='|'.join(titles),prop='coordinates|pageprops',colimit='max',redirects=1)).get('query',{})
 aliases={x['from']:x['to'] for k in ['normalized','redirects'] for x in d.get(k,[])}
 pages={x['title']:x for x in d.get('pages',{}).values()};out={}
 for u,t in zip(us,titles):
  for _ in range(10):
   if t not in aliases:break
   t=aliases[t]
  p=pages.get(t,{});coords=p.get('coordinates',[])
  out[u]={'coords':[coords[0]['lat'],coords[0]['lon']] if coords else None,'qid':p.get('pageprops',{}).get('wikibase_item'),'source':u,'granularity':'article coordinate'}
 return out
records={}
with ThreadPoolExecutor(max_workers=6) as pool:
 for f in as_completed([pool.submit(batch,urls[i:i+40]) for i in range(0,len(urls),40)]):
  records.update(f.result());(ROOT/'data/coordinate_sources.json').write_text(json.dumps(records));print('Batch locations',len(records),'/',len(urls),flush=True)
# Preserve directly extracted coordinates where API lacks them.
old=json.loads((ROOT/'data/locations.json').read_text())
for u,c in old.items():
 if c and u in records and not records[u]['coords']:records[u]['coords']=c
for p in ps:
 if not p['ajax']:
  for a,b in re.findall(r'(\d{4})(?:[–-](\d{4}|present))?',p['ajaxText']):p['ajax'].append([int(a),2025 if b=='present' else int(b or a)])
  p['datesSource']='roster'
 p['coords']=records.get(p['birthURL'],{}).get('coords')
 for c in p['clubs']:c['coords']=records.get(c['url'],{}).get('coords')
meta={'title':'Ajax Atlas','start':1950,'end':2025,'retrieved':'2026-10-26','source':'https://en.wikipedia.org/wiki/List_of_AFC_Ajax_players','license':'CC BY-SA 4.0 (Wikipedia-derived compilation).','scope':'636 listed Ajax players with careers overlapping 1950–2025; not an exhaustive verified senior-appearance register.','coordinateMeaning':'Birthplace settlement/article coordinates. Club article coordinates where provided. Not exact birth addresses.','missingBirthplaces':sum(not p['coords'] for p in ps)}
data={'meta':meta,'players':ps}
(ROOT/'data/coordinate_sources.json').write_text(json.dumps(records))
(ROOT/'data/players.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
(ROOT/'data/players.js').write_text('window.AJAX_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
print('DONE',len(ps),'mapped',sum(bool(p['coords']) for p in ps),'clubspells mapped',sum(bool(c['coords']) for p in ps for c in p['clubs']),flush=True)
