from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
ns={'__file__':str(Path(__file__).with_name('enrich_coordinates.py'))}
src=Path(__file__).with_name('enrich_coordinates.py').read_text()
exec(src.split('records={}')[0],ns)
ROOT=ns['ROOT'];records=json.loads((ROOT/'data/coordinate_sources.json').read_text());ps=ns['ps']
missing=[u for u,r in records.items() if not r.get('qid')]
print('Retry missing entities',len(missing),flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
 for f in as_completed([pool.submit(ns['batch'],missing[i:i+6]) for i in range(0,len(missing),6)]):
  for u,r in f.result().items():
   if r['qid']:records[u]=r
  (ROOT/'data/coordinate_sources.json').write_text(json.dumps(records))
print('Remain',sum(not r.get('qid') for r in records.values()),flush=True)
# Use the same finalization as the primary batch script.
ns['records']=records
exec(src.split('# Preserve directly extracted coordinates where API lacks them.')[1],ns)
