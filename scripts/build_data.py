"""Rebuild the static atlas. Requires Python 3, lxml and curl. Cached, bounded fetches."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
import json,re,subprocess,hashlib,time,sys,os
ROOT=Path(__file__).resolve().parents[1]
CACHE=Path(os.environ.get('AJAX_CACHE',str(ROOT/'.cache'))); CACHE.mkdir(exist_ok=True)
def fetch(url):
 p=CACHE/(hashlib.sha256(url.encode()).hexdigest()+'.html')
 if not p.exists():
  r=subprocess.run(['curl','-L','-s','--fail','--max-time','35',url],capture_output=True)
  if r.returncode or len(r.stdout)<200:return None
  p.write_bytes(r.stdout)
 try:return html.fromstring(p.read_bytes())
 except:return None
def clean(el):
 for x in el.xpath('.//style|.//sup'):x.getparent().remove(x)
 return ' '.join(el.text_content().split())
def link(a):
 u=a.get('href','');return 'https://en.wikipedia.org'+u if u.startswith('/wiki/') else u
source='https://en.wikipedia.org/wiki/List_of_AFC_Ajax_players'
s=html.parse(str(ROOT/'data/source.html'))
rows=[]
for tr in s.xpath('//table[contains(@class,"wikitable")]')[0].xpath('.//tr'):
 td=tr.xpath('./td')
 if len(td)<6:continue
 a=td[0].xpath('.//a')
 if not a:continue
 career=clean(td[3]); yy=[int(y) for y in re.findall(r'\d{4}',career)]
 if not yy or min(yy)>2025 or (max(yy)<1950 and 'present' not in career):continue
 rows.append(dict(name=clean(a[0]),url=link(a[0]),ajaxText=career,position=clean(td[2]),leagueApps=clean(td[5])))
print('Roster',len(rows),flush=True)
def player(p):
 s=fetch(p['url']); p.update(clubs=[],birthplace=None,birthURL=None,coords=None,ajax=[])
 if s is None:p['error']='Profile unavailable';return p
 box=s.xpath('//table[contains(@class,"infobox")]')
 if not box:p['error']='No structured profile';return p
 senior=False
 for tr in box[0].xpath('.//tr'):
  txt=clean(tr); cells=tr.xpath('./th|./td')
  if txt.startswith('Place of birth') and len(cells)>1:
   p['birthplace']=clean(cells[-1]); a=cells[-1].xpath('.//a[not(starts-with(@href,"#"))]');p['birthURL']=link(a[0]) if a else None
  if txt.startswith('Date of birth'):
   b=tr.xpath('.//*[contains(@class,"bday")]');p['born']=clean(b[0]) if b else None
  if txt.startswith('Senior career'):senior=True;continue
  if senior and (txt.startswith('International career') or txt.startswith('Managerial career') or txt.startswith('Total')):senior=False
  if senior and len(cells)>=2:
   years=clean(cells[0]); yy=[int(x) for x in re.findall(r'\d{4}',years)]
   a=cells[1].xpath('.//a')
   if not yy or not a or yy[0]>2025:continue
   end=yy[-1] if len(yy)>1 else (2025 if re.search(r'[–-]\s*$',years) else yy[0])
   c={'name':clean(cells[1]),'url':link(a[0]),'start':yy[0],'end':min(end,2025),'years':years,'coords':None}
   p['clubs'].append(c)
   if c['url'].split('/')[-1]=='AFC_Ajax':p['ajax'].append([c['start'],c['end']])
 if not p['ajax']:
  # Roster dates remain usable, clearly flagged as roster-derived.
  for start,end in re.findall(r'(\d{4})(?:[–-](\d{4}|present))?',p['ajaxText']):p['ajax'].append([int(start),2025 if end=='present' else int(end or start)])
  p['datesSource']='roster'
 else:p['datesSource']='profile'
 return p
if '--resume' in sys.argv and (ROOT/'data/profiles.json').exists():
 players=json.loads((ROOT/'data/profiles.json').read_text())
else:
 players=[]
 with ThreadPoolExecutor(max_workers=20) as pool:
  for i,f in enumerate(as_completed([pool.submit(player,p) for p in rows])):
   players.append(f.result())
   if i%25==0:print('Profiles',i+1,flush=True)
 players.sort(key=lambda p:p['name'])
 (ROOT/'data/profiles.json').write_text(json.dumps(players,ensure_ascii=False))
urls=set(p['birthURL'] for p in players if p['birthURL'])|set(c['url'] for p in players for c in p['clubs'])
print('Locations',len(urls),flush=True)
def location(url):
 s=fetch(url)
 if s is None:return url,None
 lat=s.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," latitude ")]');lon=s.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," longitude ")]')
 def angle(x):
  t=clean(x); nums=[float(v) for v in re.findall(r'\d+(?:\.\d+)?',t)]
  return sum(v/(60**i) for i,v in enumerate(nums[:3]))*(-1 if re.search('[SW−-]',t) else 1)
 if lat and lon:return url,[angle(lat[0]),angle(lon[0])]
 geo=s.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," geo ")]')
 if geo:
  nums=re.findall(r'-?\d+(?:\.\d+)?',clean(geo[0]))
  if len(nums)==2:return url,list(map(float,nums))
 return url,None
locations=json.loads((ROOT/'data/locations.json').read_text()) if (ROOT/'data/locations.json').exists() else {}
urls=[u for u in sorted(urls,key=lambda u: (u not in set(p['birthURL'] for p in players),u)) if u not in locations]
with ThreadPoolExecutor(max_workers=20) as pool:
 for i,f in enumerate(as_completed([pool.submit(location,u) for u in urls])):
  u,coord=f.result();locations[u]=coord
  if i%50==0:
   print('Locations',i+1,flush=True)
   (ROOT/'data/locations.json').write_text(json.dumps(locations))
(ROOT/'data/locations.json').write_text(json.dumps(locations))
for p in players:
 if not p['ajax']:
  for start,end in re.findall(r'(\d{4})(?:[–-](\d{4}|present))?',p['ajaxText']):p['ajax'].append([int(start),2025 if end=='present' else int(end or start)])
  p['datesSource']='roster'
 p['coords']=locations.get(p['birthURL'])
 for c in p['clubs']:c['coords']=locations.get(c['url'])
data={'meta':{'title':'Ajax Atlas','start':1950,'end':2025,'retrieved':time.strftime('%Y-%m-%d'),'source':source,'license':'Wikipedia-derived factual compilation; attribution and CC BY-SA 4.0 for reused text.','scope':'Listed Ajax players with roster career overlap 1950–2025; not a verified exhaustive first-team appearance register.','coordinateMeaning':'Birthplace settlement coordinates; club coordinates from club article, typically stadium. Not exact birth addresses.','missingBirthplaces':sum(not p['coords'] for p in players)},'players':players}
(ROOT/'data/players.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
(ROOT/'data/players.js').write_text('window.AJAX_DATA='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
print('DONE',len(players),'mapped',sum(bool(p['coords']) for p in players),flush=True)
