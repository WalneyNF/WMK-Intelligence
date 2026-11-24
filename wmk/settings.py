import os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
f=ROOT/'.env'
if f.exists():
    for line in f.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k,v=line.split('=',1)
            os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))
DB=ROOT/'dados'/'wmk.sqlite3'
API_BASE='https://www.moltbook.com/api/v1'
HOST=os.getenv('WMK_HOST','127.0.0.1')
PORT=int(os.getenv('WMK_PORT','8767'))
