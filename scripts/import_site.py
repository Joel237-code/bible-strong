"""One-time import of the published application, with pinned SHA-256 checks."""
import hashlib,json,time,urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
SOURCE='https://bible-strong-etude-joel.sunnylamp68.chatgpt.site/'
files=json.loads((ROOT/'scripts/migration-files.json').read_text())
def transfer(item):
    name,expected=item
    target=ROOT/'docs'/name
    if target.is_file():
        # Already imported files are authoritative; future edits need no old host.
        return
    for attempt in range(3):
        try:
            req=urllib.request.Request(SOURCE+name,headers={'User-Agent':'BibleStrong-Migration/1.0'})
            with urllib.request.urlopen(req,timeout=60) as response: content=response.read()
            if hashlib.sha256(content).hexdigest()!=expected: raise ValueError('Source differs from verified version: '+name)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(content)
            return
        except Exception:
            if attempt==2: raise
            time.sleep(2)
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(transfer,files.items()))
    (ROOT/'docs/.nojekyll').touch()
    print(f'{len(files)} application files present; migration complete.')
