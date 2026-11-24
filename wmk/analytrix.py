"""ANALYTRIX: classificação lexical incremental, sem chamadas externas."""
import sqlite3,re,json,time,logging
from contextlib import closing
from datetime import datetime,timezone
from .settings import DB,ROOT
from .discovery import TOPICS,classify
OUT=ROOT/'dados'/'analytrix.sqlite3'
VERSION=1
TYPES={'Problema':r'\b(problem|issue|bug|failure|error|problema|erro|falha)\b','Solução':r'\b(solution|solved|fix|workaround|solução|corrigido)\b','Tutorial':r'\b(tutorial|guide|how to|guia|passo a passo)\b','Experimento':r'\b(experiment|benchmark|tested|experimento|teste)\b','Hipótese':r'\b(hypothesis|hypothesize|hipótese)\b','Ferramenta':r'\b(tool|library|framework|ferramenta|biblioteca)\b','Pergunta':r'\?'}
EXTRA={'Memória e RAG':r'\b(rag|embedding|context window|persistent memory|memória persistente)\b','MCP e integração':r'\b(mcp|webhook|interoperability|integração)\b','Desempenho':r'\b(latency|throughput|optimization|performance|latência|otimização)\b'}
def analyze(title,body):
    t=(title or '')+' '+(body or '')
    topics=classify(t,{**TOPICS,**EXTRA})
    kinds=classify(t,TYPES)
    return topics or {'Não classificado':[]},kinds or {'Não identificado':[]}
def output():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(OUT,timeout=10)
    c.row_factory=sqlite3.Row
    c.executescript("""CREATE TABLE IF NOT EXISTS results(source TEXT,id TEXT,title TEXT,url TEXT,captured TEXT,version INTEGER,topics TEXT,kinds TEXT,excerpt TEXT,analyzed TEXT,PRIMARY KEY(source,id));
    CREATE TABLE IF NOT EXISTS topic(source TEXT,id TEXT,name TEXT,PRIMARY KEY(source,id,name));
    CREATE TABLE IF NOT EXISTS kind(source TEXT,id TEXT,name TEXT,PRIMARY KEY(source,id,name));
    CREATE INDEX IF NOT EXISTS topic_name ON topic(name);
    CREATE INDEX IF NOT EXISTS kind_name ON kind(name);""")
    return c
def original():
    c=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro',uri=True,timeout=10)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA query_only=ON')
    return c
def batch():
    with closing(output()) as dst, closing(original()) as src:
        # Cursor persistente por rowid; items usa INSERT OR IGNORE.
        dst.execute('CREATE TABLE IF NOT EXISTS cursor_state(version INTEGER PRIMARY KEY,last_row INTEGER)')
        row=dst.execute('SELECT last_row FROM cursor_state WHERE version=?',(VERSION,)).fetchone()
        last=row[0] if row else 0
        rows=src.execute('SELECT rowid AS rid,source,id,title,body,source_url,captured_at FROM items WHERE rowid>? ORDER BY rowid LIMIT 100',(last,)).fetchall()
        with dst:
            for p in rows:
                topics,kinds=analyze(p['title'],p['body'])
                dst.execute('INSERT OR REPLACE INTO results VALUES(?,?,?,?,?,?,?,?,?,?)',(p['source'],p['id'],p['title'],p['source_url'],p['captured_at'],VERSION,json.dumps(topics,ensure_ascii=False),json.dumps(kinds,ensure_ascii=False),(p['body'] or '')[:700],datetime.now(timezone.utc).isoformat()))
                for table,labels in [('topic',topics),('kind',kinds)]:
                    dst.execute('DELETE FROM '+table+' WHERE source=? AND id=?',(p['source'],p['id']))
                    dst.executemany('INSERT INTO '+table+' VALUES(?,?,?)',[(p['source'],p['id'],k) for k in labels])
            if rows:dst.execute('INSERT OR REPLACE INTO cursor_state VALUES(?,?)',(VERSION,rows[-1]['rid']))
        return len(rows)
def overview(topic='',kind=''):
    with closing(output()) as c,closing(original()) as src:
        total=src.execute('SELECT count(*) FROM items').fetchone()[0]
        n=c.execute('SELECT count(*) FROM results').fetchone()[0]
        ranks={t:[dict(r) for r in c.execute('SELECT name,count(*) AS count FROM '+t+' GROUP BY name ORDER BY count DESC,name')] for t in ('topic','kind')}
        rows=c.execute("""SELECT * FROM results r WHERE (?='' OR EXISTS(SELECT 1 FROM topic t WHERE t.source=r.source AND t.id=r.id AND t.name=?)) AND (?='' OR EXISTS(SELECT 1 FROM kind k WHERE k.source=r.source AND k.id=r.id AND k.name=?)) ORDER BY captured DESC LIMIT 100""",(topic,topic,kind,kind))
        return {'total':total,'analyzed':n,**ranks,'posts':[dict(r) for r in rows],'method':'lexical-v1'}
def worker():
    while True:
        try:time.sleep(1 if batch() else 15)
        except Exception:
            logging.exception('ANALYTRIX: falha no processamento')
            time.sleep(30)
