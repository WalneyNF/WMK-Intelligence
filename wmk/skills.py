"""CRUD administrativo isolado da memória original."""
import sqlite3,json,uuid
from contextlib import closing
from .settings import ROOT

DB=ROOT/'dados'/'skills.sqlite3'
def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB,timeout=10)
    db.execute("CREATE TABLE IF NOT EXISTS skills(id TEXT PRIMARY KEY, data TEXT NOT NULL)")
    db.commit()
    return db

def catalog():
    with closing(connect()) as db:
        return {'skills':[json.loads(row[0]) for row in db.execute("SELECT data FROM skills ORDER BY id")]}

def action(body):
    op=body.get('op')
    ident=str(body.get('id',''))
    with closing(connect()) as db, db:
        if op=='delete':
            if not db.execute("DELETE FROM skills WHERE id=?",(ident,)).rowcount:raise ValueError('Skill inexistente')
            return {'ok':True}
        if op not in ('create','update'):raise ValueError('Operação inválida')
        item=body.get('skill')
        if not isinstance(item,dict):raise ValueError('Skill inválida')
        fields={'name':120,'category':80,'description':1000,'prompt':6000,'agents':500,'inputs':500,'outputs':500,'tools':500,'mcp':500,'version':40}
        clean={}
        for key,limit in fields.items():
            value=item.get(key,'')
            if not isinstance(value,str) or len(value)>limit:raise ValueError('Campo inválido: '+key)
            clean[key]=value.strip()
        if not clean['name'] or not clean['prompt']:raise ValueError('Nome e prompt obrigatórios')
        clean.update(active=item.get('active') is True,memory_access='read_only',external_actions=False)
        if op=='create':
            ident=uuid.uuid4().hex
        else:
            if not db.execute("SELECT 1 FROM skills WHERE id=?",(ident,)).fetchone():raise ValueError('Skill inexistente')
        clean['id']=ident
        data=json.dumps(clean,ensure_ascii=False)
        if op=='create':db.execute("INSERT INTO skills VALUES(?,?)",(ident,data))
        else:db.execute("UPDATE skills SET data=? WHERE id=?",(data,ident))
        return {'ok':True,'skill':clean}
