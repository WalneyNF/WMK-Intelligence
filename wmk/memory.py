"""Memória persistente incremental, pesquisa local e proveniência."""
import json,re,sqlite3,threading
from .store import connect,now
from .discovery import classify,TOPICS
from .radar import RULES
LOCK=threading.Lock()
VERSION=1
def schema(db):
    db.execute("""CREATE TABLE IF NOT EXISTS knowledge_memory(
      source TEXT NOT NULL,id TEXT NOT NULL,version INTEGER NOT NULL,
      topics TEXT NOT NULL,security TEXT NOT NULL,indexed_at TEXT NOT NULL,
      PRIMARY KEY(source,id))""")
    try:
        db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(source UNINDEXED,id UNINDEXED,title,body,tags,tokenize='unicode61 remove_diacritics 2')")
        return True
    except sqlite3.OperationalError as e:
        if 'no such module' not in str(e):raise
        return False
def index_batch(limit=100):
    with LOCK:
        db=connect()
        try:
            fts=schema(db)
            rows=db.execute("""SELECT p.* FROM items p LEFT JOIN knowledge_memory m
              ON p.source=m.source AND p.id=m.id
              WHERE m.id IS NULL OR m.version<>? LIMIT ?""",(VERSION,limit)).fetchall()
            for p in rows:
                title=p['title'] or '';body=p['body'] or ''
                topics=classify(title+' '+body,TOPICS);security=classify(title+' '+body,RULES)
                db.execute("INSERT OR REPLACE INTO knowledge_memory VALUES(?,?,?,?,?,?)",(p['source'],p['id'],VERSION,json.dumps(topics,ensure_ascii=False),json.dumps(security,ensure_ascii=False),now()))
                if fts:
                    db.execute("DELETE FROM knowledge_fts WHERE source=? AND id=?",(p['source'],p['id']))
                    db.execute("INSERT INTO knowledge_fts VALUES(?,?,?,?,?)",(p['source'],p['id'],title,body,' '.join(list(topics)+list(security))))
            db.commit()
            return len(rows)
        finally:db.close()
def search(q='',page=1):
    db=connect()
    try:
        fts=schema(db);db.commit()
        total=db.execute("SELECT count(*) FROM items").fetchone()[0]
        indexed=db.execute("SELECT count(*) FROM knowledge_memory WHERE version=?",(VERSION,)).fetchone()[0]
        words=re.findall(r'\w+',q[:200])[:20];offset=(max(1,min(page,100000))-1)*30
        base="SELECT p.source,p.id,p.title,substr(p.body,1,600) AS excerpt,p.source_url,p.captured_at,m.topics,m.security FROM items p JOIN knowledge_memory m ON p.source=m.source AND p.id=m.id"
        if words and fts:
            rows=db.execute(base+" JOIN knowledge_fts f ON f.source=p.source AND f.id=p.id WHERE knowledge_fts MATCH ? ORDER BY bm25(knowledge_fts) LIMIT 30 OFFSET ?",(' AND '.join('"'+w+'"' for w in words),offset))
        elif words:
            rows=db.execute(base+" WHERE "+' AND '.join("(p.title LIKE ? OR p.body LIKE ? OR m.topics LIKE ?)" for w in words)+" ORDER BY p.captured_at DESC LIMIT 30 OFFSET ?",tuple('%'+w+'%' for w in words for _ in range(3))+(offset,))
        else:rows=db.execute(base+" ORDER BY p.captured_at DESC LIMIT 30 OFFSET ?",(offset,))
        return {'total':total,'indexed':indexed,'engine':'FTS5' if fts else 'LIKE','posts':[dict(p) for p in rows]}
    finally:db.close()
def worker():
    import time,logging
    while True:
        try:time.sleep(1 if index_batch() else 15)
        except Exception:
            logging.exception('Falha na indexação da memória WMK')
            time.sleep(30)
