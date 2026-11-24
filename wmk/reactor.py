import sqlite3
from contextlib import closing
from .settings import DB,ROOT
def count(path,table):
    if not path.is_file():return 0
    with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True,timeout=3)) as c:
        c.execute('PRAGMA query_only=ON')
        if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():return 0
        return c.execute('SELECT count(*) FROM '+table).fetchone()[0]
def overview():
    return {'collected':count(DB,'items'),'indexed':count(DB,'knowledge_memory'),'classified':count(ROOT/'dados'/'analytrix.sqlite3','results')}
