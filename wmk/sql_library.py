import json,sqlite3,uuid
from contextlib import closing
from .settings import ROOT
from .database_studio import query
EXAMPLES=[
  {
    "id": "example-1",
    "category": "Fundamentos",
    "name": "Total de publicações",
    "description": "COUNT conta registros.",
    "sql": "SELECT count(*) AS total FROM items"
  },
  {
    "id": "example-2",
    "category": "Fundamentos",
    "name": "Últimas publicações",
    "description": "ORDER BY ordena; LIMIT restringe.",
    "sql": "SELECT source,id,title,source_url FROM items ORDER BY captured_at DESC LIMIT 30"
  },
  {
    "id": "example-3",
    "category": "BI",
    "name": "Comunidades mais ativas",
    "description": "GROUP BY agrega por comunidade.",
    "sql": "SELECT community,count(*) AS total FROM items GROUP BY community ORDER BY total DESC"
  },
  {
    "id": "example-4",
    "category": "BI",
    "name": "Coleta por dia",
    "description": "date extrai a data de coleta.",
    "sql": "SELECT date(captured_at) AS dia,count(*) AS total FROM items GROUP BY date(captured_at) ORDER BY dia DESC"
  },
  {
    "id": "example-5",
    "category": "BI",
    "name": "Fontes",
    "description": "Contagem por origem.",
    "sql": "SELECT source,count(*) AS total FROM items GROUP BY source ORDER BY total DESC"
  },
  {
    "id": "example-6",
    "category": "Memória",
    "name": "Cobertura de indexação",
    "description": "LEFT JOIN encontra registros sem índice.",
    "sql": "SELECT count(*) AS pendentes FROM items i LEFT JOIN knowledge_memory m ON i.source=m.source AND i.id=m.id WHERE m.id IS NULL"
  },
  {
    "id": "example-7",
    "category": "Memória",
    "name": "Temas indexados",
    "description": "Pesquisa lexical nas etiquetas JSON.",
    "sql": "SELECT i.source,i.id,i.title,m.topics,i.source_url FROM items i JOIN knowledge_memory m ON i.source=m.source AND i.id=m.id WHERE m.topics LIKE '%Programação%' LIMIT 100"
  },
  {
    "id": "example-8",
    "category": "Segurança",
    "name": "Avaliações de risco",
    "description": "Risco lexical não comprova incidente.",
    "sql": "SELECT i.source,i.id,i.title,a.risk,i.source_url FROM items i JOIN assessments_v2 a ON i.source=a.source AND i.id=a.post_id ORDER BY a.risk DESC LIMIT 50"
  },
  {
    "id": "example-9",
    "category": "Mineração",
    "name": "RAG e memória",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%rag%' OR lower(body) LIKE '%rag%') OR (lower(title) LIKE '%retrieval%' OR lower(body) LIKE '%retrieval%') OR (lower(title) LIKE '%embedding%' OR lower(body) LIKE '%embedding%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-10",
    "category": "Mineração",
    "name": "MCP",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%model context protocol%' OR lower(body) LIKE '%model context protocol%') OR (lower(title) LIKE '%mcp%' OR lower(body) LIKE '%mcp%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-11",
    "category": "Mineração",
    "name": "Python",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%python%' OR lower(body) LIKE '%python%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-12",
    "category": "Mineração",
    "name": "SQLite",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%sqlite%' OR lower(body) LIKE '%sqlite%') OR (lower(title) LIKE '%database index%' OR lower(body) LIKE '%database index%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-13",
    "category": "Mineração",
    "name": "Ollama",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%ollama%' OR lower(body) LIKE '%ollama%') OR (lower(title) LIKE '%local model%' OR lower(body) LIKE '%local model%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-14",
    "category": "Mineração",
    "name": "Jogos",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%game engine%' OR lower(body) LIKE '%game engine%') OR (lower(title) LIKE '%godot%' OR lower(body) LIKE '%godot%') OR (lower(title) LIKE '%three.js%' OR lower(body) LIKE '%three.js%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-15",
    "category": "Mineração",
    "name": "Soluções",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%solution%' OR lower(body) LIKE '%solution%') OR (lower(title) LIKE '%workaround%' OR lower(body) LIKE '%workaround%') OR (lower(title) LIKE '%fixed%' OR lower(body) LIKE '%fixed%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-16",
    "category": "Mineração",
    "name": "Problemas",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%problem%' OR lower(body) LIKE '%problem%') OR (lower(title) LIKE '%failure%' OR lower(body) LIKE '%failure%') OR (lower(title) LIKE '%bug%' OR lower(body) LIKE '%bug%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-17",
    "category": "Mineração",
    "name": "Experimentos",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%experiment%' OR lower(body) LIKE '%experiment%') OR (lower(title) LIKE '%benchmark%' OR lower(body) LIKE '%benchmark%') OR (lower(title) LIKE '%baseline%' OR lower(body) LIKE '%baseline%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-18",
    "category": "Mineração",
    "name": "Ferramentas",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%library%' OR lower(body) LIKE '%library%') OR (lower(title) LIKE '%framework%' OR lower(body) LIKE '%framework%') OR (lower(title) LIKE '%tool%' OR lower(body) LIKE '%tool%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-19",
    "category": "Mineração",
    "name": "Desempenho",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%latency%' OR lower(body) LIKE '%latency%') OR (lower(title) LIKE '%performance%' OR lower(body) LIKE '%performance%') OR (lower(title) LIKE '%optimization%' OR lower(body) LIKE '%optimization%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-20",
    "category": "Mineração",
    "name": "Arquitetura",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%architecture%' OR lower(body) LIKE '%architecture%') OR (lower(title) LIKE '%design pattern%' OR lower(body) LIKE '%design pattern%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-21",
    "category": "Mineração",
    "name": "APIs",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%rest api%' OR lower(body) LIKE '%rest api%') OR (lower(title) LIKE '%endpoint%' OR lower(body) LIKE '%endpoint%') ORDER BY captured_at DESC LIMIT 100"
  },
  {
    "id": "example-22",
    "category": "Mineração",
    "name": "Segurança defensiva",
    "description": "Busca por termos em inglês; resultados são candidatos, não evidências verificadas.",
    "sql": "SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%least privilege%' OR lower(body) LIKE '%least privilege%') OR (lower(title) LIKE '%authorization%' OR lower(body) LIKE '%authorization%') OR (lower(title) LIKE '%input validation%' OR lower(body) LIKE '%input validation%') ORDER BY captured_at DESC LIMIT 100"
  }
]
def db():
    p=ROOT/'dados'/'sql-library.sqlite3'
    p.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(p,timeout=5)
    c.execute('CREATE TABLE IF NOT EXISTS queries(id TEXT PRIMARY KEY,data TEXT NOT NULL)')
    return c
def catalog():
    with closing(db()) as c:
        return EXAMPLES+[json.loads(x[0]) for x in c.execute('SELECT data FROM queries ORDER BY rowid DESC')]
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
