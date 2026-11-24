"""Armazenamento SQLite multi-redes; migração compatível com banco v0.1."""
import sqlite3,json
from datetime import datetime,timezone
from .settings import DB
def now():return datetime.now(timezone.utc).isoformat()
def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB,timeout=15);db.row_factory=sqlite3.Row
    db.executescript("""
      CREATE TABLE IF NOT EXISTS items(
        source TEXT NOT NULL,id TEXT NOT NULL,title TEXT,body TEXT,author TEXT,
        community TEXT,source_url TEXT,created_at TEXT,captured_at TEXT,raw_json TEXT,
        PRIMARY KEY(source,id));
      CREATE TABLE IF NOT EXISTS assessments_v2(
        source TEXT NOT NULL,post_id TEXT NOT NULL,risk INTEGER,terms TEXT,summary TEXT,updated_at TEXT,
        PRIMARY KEY(source,post_id));
      CREATE TABLE IF NOT EXISTS comments_v2(
        source TEXT NOT NULL,id TEXT NOT NULL,post_id TEXT,body TEXT,raw_json TEXT,captured_at TEXT,
        PRIMARY KEY(source,id));
      CREATE INDEX IF NOT EXISTS idx_items_time ON items(captured_at DESC);
    """)
    tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if 'posts' in tables:
        db.execute("""INSERT OR IGNORE INTO items SELECT
         'moltbook',id,title,body,author,submolt,source_url,created_at,captured_at,raw_json FROM posts""")
    if 'assessments' in tables:
        db.execute("""INSERT OR IGNORE INTO assessments_v2 SELECT
         'moltbook',post_id,risk,terms,summary,updated_at FROM assessments""")
    if 'comments' in tables:
        db.execute("""INSERT OR IGNORE INTO comments_v2 SELECT
         'moltbook',id,post_id,body,raw_json,captured_at FROM comments""")
    db.commit();return db
def save_posts(items,source=''):
    db=connect();added=0
    try:
        for p in items:
            if not isinstance(p,dict):continue
            origin=str(p.get('source') or source or '')
            ident=str(p.get('id') or '')
            if not ident or not origin:continue
            added+=db.execute("""INSERT OR IGNORE INTO items VALUES(?,?,?,?,?,?,?,?,?,?)""",
              (origin[:64],ident[:500],str(p.get('title') or '')[:2000],
              str(p.get('body') or '')[:100000],str(p.get('author') or '')[:200],
              str(p.get('community') or '')[:200],str(p.get('url') or '')[:1500],
              str(p.get('created_at') or '')[:120],now(),
              json.dumps(p.get('raw',p),ensure_ascii=False)[:250000])).rowcount
        db.commit()
    finally:db.close()
    return added
def save_assessment(ident,risk,terms,source='moltbook'):
    db=connect()
    try:
        db.execute("""INSERT INTO assessments_v2 VALUES(?,?,?,?,?,?)
          ON CONFLICT(source,post_id) DO UPDATE SET
          risk=excluded.risk,terms=excluded.terms,updated_at=excluded.updated_at""",
          (source,str(ident),int(risk),json.dumps(terms,ensure_ascii=False),'',now()))
        db.commit()
    finally:db.close()
def list_posts(limit=100,q='',source=''):
    db=connect()
    try:
        rows=db.execute("""SELECT p.id,p.source,p.title,p.body,p.author,p.community,
          p.community AS submolt,p.source_url,p.created_at,p.captured_at,
          COALESCE(a.risk,0) risk,COALESCE(a.terms,'[]') terms
          FROM items p LEFT JOIN assessments_v2 a ON a.source=p.source AND a.post_id=p.id
          WHERE (?='' OR p.source=?) AND (p.title LIKE ? OR p.body LIKE ?)
          ORDER BY p.captured_at DESC LIMIT ?""",
          (source,source,'%'+q+'%','%'+q+'%',max(1,min(int(limit),300)))).fetchall()
        return [dict(r) for r in rows]
    finally:db.close()
def save_comments(post_id,comments,source='moltbook'):
    db=connect();count=0
    def walk(items,depth=0):
        nonlocal count
        if depth>5:return
        for c in items:
            if not isinstance(c,dict):continue
            if c.get('id'):
                count+=db.execute("INSERT OR IGNORE INTO comments_v2 VALUES(?,?,?,?,?,?)",
                  (source,str(c['id']),post_id,str(c.get('content') or '')[:100000],
                   json.dumps(c,ensure_ascii=False)[:250000],now())).rowcount
            walk(c.get('replies') or [],depth+1)
    try:walk(comments);db.commit()
    finally:db.close()
    return count
def stats():
    db=connect()
    try:return {
       'posts':db.execute('SELECT COUNT(*) FROM items').fetchone()[0],
       'comments':db.execute('SELECT COUNT(*) FROM comments_v2').fetchone()[0],
       'alerts':db.execute('SELECT COUNT(*) FROM assessments_v2 WHERE risk>=2').fetchone()[0],
       'sources':db.execute('SELECT COUNT(DISTINCT source) FROM items').fetchone()[0]}
    finally:db.close()
