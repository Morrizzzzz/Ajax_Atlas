"""Retry unavailable player infoboxes, keeping previous data if retrieval still fails."""
from pathlib import Path
import json
from concurrent.futures import ThreadPoolExecutor,as_completed
R=Path(__file__).resolve().parents[1]
ns={'__file__':str(R/'scripts/build_data.py')}
exec((R/'scripts/build_data.py').read_text().split("if '--resume'")[0],ns)
ps=json.loads((R/'data/profiles.json').read_text());bad=[p for p in ps if not p['clubs']]
repaired={}
with ThreadPoolExecutor(max_workers=3) as pool:
 for f in as_completed([pool.submit(ns['player'],dict(p)) for p in bad]):
  p=f.result()
  if p['clubs']:p.pop('error',None);repaired[p['url']]=p
(R/'data/repaired_profiles.json').write_text(json.dumps(repaired,ensure_ascii=False))
print('Repaired',list(p['name'] for p in repaired.values()),flush=True)
