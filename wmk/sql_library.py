import json,sqlite3,uuid
from contextlib import closing
from .settings import ROOT
from .database_studio import query
def examples():
    out=[]
    seen=set()
    for path in sorted((ROOT/'config'/'sql').glob('*.json')):
        try:
            data=json.loads(path.read_text(encoding='utf-8'))
            if data.get('version')!=1 or not isinstance(data.get('queries'),list):raise ValueError('Formato inválido')
            for d in data['queries']:
                if not isinstance(d,dict) or any(not isinstance(d.get(k),str) for k in ('id','name','category','description','sql')):raise ValueError('Consulta inválida')
                if not d['id'].startswith('example-') or d['id'] in seen or not d['sql'].strip() or len(d['sql'])>8000:raise ValueError('ID duplicado ou SQL inválido')
                seen.add(d['id'])
                out.append(d)
        except (ValueError,TypeError,AttributeError,OSError) as e:
            raise ValueError('Biblioteca SQL: '+path.name+': '+str(e)) from e
    return out

def db():
    p=ROOT/'dados'/'sql-library.sqlite3'
    p.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(p,timeout=5)
    c.execute('CREATE TABLE IF NOT EXISTS queries(id TEXT PRIMARY KEY,data TEXT NOT NULL)')
    return c
def catalog():
    with closing(db()) as c:
        return examples()+[json.loads(x[0]) for x in c.execute('SELECT data FROM queries ORDER BY rowid DESC')]
def action(b):
    op=b.get('op')
    if op=='run':return query(b.get('sql'))
    ident=b.get('id','')
    with closing(db()) as c:
        if op=='delete':
            c.execute('DELETE FROM queries WHERE id=?',(ident,))
        elif op=='save':
            if not isinstance(ident,str) or not ident.startswith('user-'):ident='user-'+uuid.uuid4().hex
            d={'id':ident}
            for k,n in [('name',120),('category',80),('description',2000),('sql',8000)]:
                v=b.get(k,'')
                if not isinstance(v,str) or len(v)>n:raise ValueError('Campo inválido: '+k)
                d[k]=v.strip()
            if not d['name'] or not d['sql']:raise ValueError('Nome e SQL obrigatórios')
            c.execute('INSERT OR REPLACE INTO queries VALUES (?,?)',(ident,json.dumps(d,ensure_ascii=False)))
        else:raise ValueError('Operação inválida')
        c.commit()
    return catalog()
