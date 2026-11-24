"""SQLite local, amostragem e deduplicação."""
import sqlite3,json
from datetime import datetime,timezone
from .settings import DB
def now():return datetime.now(timezone.utc).isoformat()
def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB,timeout=10);db.row_factory=sqlite3.Row
    db.executescript("""CREATE TABLE IF NOT EXISTS posts(id TEXT PRIMARY KEY,title TEXT,body TEXT,author TEXT,submolt TEXT,source_url TEXT,created_at TEXT,captured_at TEXT,raw_json TEXT);
    CREATE TABLE IF NOT EXISTS assessments(post_id TEXT PRIMARY KEY,risk INTEGER,terms TEXT,summary TEXT,updated_at TEXT);
    CREATE TABLE IF NOT EXISTS comments(id TEXT PRIMARY KEY,post_id TEXT,body TEXT,raw_json TEXT,captured_at TEXT);""")
    return db
def save_posts(posts):
    db=connect();count=0
    try:
        for p in posts:
            if not isinstance(p,dict) or not p.get('id'):continue
            ident=str(p['id']);a=p.get('author') or p.get('agent') or {}
            author=a.get('name','') if isinstance(a,dict) else str(a)
            sub=p.get('submolt') or p.get('submolt_name') or ''
            if isinstance(sub,dict):sub=sub.get('name','')
            count+=db.execute('INSERT OR IGNORE INTO posts VALUES(?,?,?,?,?,?,?,?,?)',(ident,str(p.get('title') or '')[:2000],str(p.get('content') or p.get('body') or '')[:100000],author,str(sub),'https://www.moltbook.com/post/'+ident,str(p.get('created_at') or ''),now(),json.dumps(p,ensure_ascii=False))).rowcount
        db.commit()
    finally:db.close()
    return count
def save_assessment(ident,risk,terms):
    db=connect()
    try:
        db.execute("""INSERT INTO assessments VALUES(?,?,?,?,?) ON CONFLICT(post_id) DO UPDATE SET risk=excluded.risk,terms=excluded.terms,updated_at=excluded.updated_at""",(ident,risk,json.dumps(terms,ensure_ascii=False),'',now()))
        db.commit()
    finally:db.close()
def list_posts(limit=100,q=''):
    db=connect()
    try:
        rows=db.execute("""SELECT p.id,title,body,author,submolt,source_url,created_at,captured_at,COALESCE(a.risk,0) risk,COALESCE(a.terms,'[]') terms FROM posts p LEFT JOIN assessments a ON p.id=a.post_id WHERE p.title LIKE ? OR p.body LIKE ? ORDER BY captured_at DESC LIMIT ?""",('%'+q+'%','%'+q+'%',max(1,min(limit,300)))).fetchall()
        return [dict(x) for x in rows]
    finally:db.close()
def save_comments(post_id,comments):
    db=connect();count=0
    def walk(items):
        nonlocal count
        for c in items:
            if not isinstance(c,dict):continue
            if c.get('id'):count+=db.execute('INSERT OR IGNORE INTO comments VALUES(?,?,?,?,?)',(str(c['id']),post_id,str(c.get('content') or ''),json.dumps(c,ensure_ascii=False),now())).rowcount
            walk(c.get('replies') or [])
    try:walk(comments);db.commit()
    finally:db.close()
    return count
def stats():
    db=connect()
    try:return {'posts':db.execute('SELECT count(*) FROM posts').fetchone()[0],'comments':db.execute('SELECT count(*) FROM comments').fetchone()[0],'alerts':db.execute('SELECT count(*) FROM assessments WHERE risk>=2').fetchone()[0]}
    finally:db.close()
