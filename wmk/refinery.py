"""Refinaria local: indicadores derivados, sem alterar a memória."""
import sqlite3,json,time,logging
from contextlib import closing
from datetime import datetime,timezone
from .settings import ROOT
from .analytrix import OUT
DEST=ROOT/'dados'/'refinery.sqlite3'
def read(path):
    c=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True,timeout=5)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA query_only=ON')
    return c
def refresh():
    if not OUT.is_file():return
    with closing(read(OUT)) as c:
        c.execute('BEGIN')
        total=c.execute('SELECT count(*) FROM results').fetchone()[0]
        topics=[dict(x) for x in c.execute('SELECT name,count(*) AS n FROM topic GROUP BY name ORDER BY n DESC,name')]
        kinds=[dict(x) for x in c.execute('SELECT name,count(*) AS n FROM kind GROUP BY name ORDER BY n DESC,name')]
        pairs=[dict(x) for x in c.execute("""SELECT t.name,count(*) AS n FROM topic t JOIN kind k ON t.source=k.source AND t.id=k.id WHERE k.name='Problema' AND t.name!='Não classificado' GROUP BY t.name ORDER BY n DESC LIMIT 20""")]
        candidates=[dict(x) for x in c.execute("""SELECT r.source,r.id,r.title,r.url,r.topics,r.kinds,r.captured FROM results r WHERE EXISTS(SELECT 1 FROM kind k WHERE k.source=r.source AND k.id=r.id AND k.name IN ('Problema','Solução','Experimento','Hipótese','Ferramenta')) ORDER BY r.captured DESC LIMIT 80""")]
    data={'total':total,'topics':topics,'kinds':kinds,'problem_topics':pairs,'candidates':candidates,'updated':datetime.now(timezone.utc).isoformat(),'method':'lexical-v1'}
    DEST.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(DEST,timeout=5)) as c, c:
        c.execute('CREATE TABLE IF NOT EXISTS snapshot(id INTEGER PRIMARY KEY CHECK(id=1),payload TEXT NOT NULL)')
        c.execute('INSERT OR REPLACE INTO snapshot VALUES(1,?)',(json.dumps(data,ensure_ascii=False),))
def overview():
    if not DEST.is_file():return {'status':'waiting'}
    with closing(read(DEST)) as c:
        row=c.execute('SELECT payload FROM snapshot WHERE id=1').fetchone()
        return {'status':'ready',**json.loads(row[0])} if row else {'status':'waiting'}
def worker():
    while True:
        try:refresh()
        except Exception:logging.exception('Refinaria: falha na atualização')
        time.sleep(60)
