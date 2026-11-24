"""API de leitura independente. Execute python -m wmk.public_api."""
import os,json,sqlite3,hmac,time,re
from http.server import HTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
from .settings import DB
PREFIX='/api/open/v1'
def query(path,q):
    def arg(k,d=''):return q.get(k,[d])[0]
    if path=='/health':return {'ok':True,'version':'1','mode':'read-only'}
    with sqlite3.connect(DB.resolve().as_uri()+'?mode=ro',uri=True,timeout=3) as db:
        try:
            db.row_factory=sqlite3.Row
            db.execute('PRAGMA query_only=ON')
            deadline=time.monotonic()+3
            db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
            cols='source,id,title,source_url,created_at,captured_at'
            source=arg('source')[:64]
            # Explicit opt-in per source; never expose raw JSON, credentials or authors.
            allowed=[s.strip() for s in os.getenv('WMK_OPEN_SOURCES','').split(',') if s.strip()][:50]
            if not allowed:return {'items':[],'notice':'Nenhuma fonte autorizada para compartilhamento'}
            scope='source IN ('+','.join('?' for _ in allowed)+')'
            if path=='/categories':
                from collections import Counter
                counts=Counter()
                indexed=0
                exists=db.execute("SELECT 1 FROM sqlite_master WHERE name='knowledge_memory' AND type='table'").fetchone()
                if exists:
                    for row in db.execute('SELECT topics FROM knowledge_memory WHERE '+scope,allowed):
                        indexed+=1
                        try: tags=json.loads(row[0] or '{}')
                        except (ValueError,TypeError): tags={}
                        counts.update(tags.keys() if isinstance(tags,dict) and tags else ['Não classificado'])
                return {'items':[{'category':k,'total':v} for k,v in counts.most_common()],'indexed':indexed,'multi_label':True}
            if path=='/sources':
                return {'items':[dict(x) for x in db.execute('SELECT source,count(*) AS total FROM items WHERE '+scope+' GROUP BY source',allowed)]}
            if path=='/stats':
                return dict(db.execute('SELECT count(*) AS total,count(DISTINCT source) AS sources FROM items WHERE '+scope,allowed).fetchone())
            if path=='/post':
                row=db.execute('SELECT '+cols+' FROM items WHERE '+scope+' AND source=? AND id=?',allowed+[source,arg('id')[:500]]).fetchone()
                return {'item':dict(row) if row else None}
            if path not in ('/posts','/search'):raise KeyError(path)
            limit=max(1,min(100,int(arg('limit','20'))));page=max(1,min(10000,int(arg('page','1'))))
            words=re.findall(r'\w+',arg('q')[:200])[:12]
            where=scope+' AND (?=\'\' OR source=?)'
            params=allowed+[source,source]
            category=arg('category')[:120]
            if category:
                if not db.execute("SELECT 1 FROM sqlite_master WHERE name='knowledge_memory' AND type='table'").fetchone():return {'items':[],'page':page,'limit':limit,'has_more':False}
                safe="CASE WHEN json_valid(m.topics) THEN m.topics ELSE '{}' END"
                where+=' AND EXISTS (SELECT 1 FROM knowledge_memory m WHERE m.source=items.source AND m.id=items.id AND '+("("+safe+" = '{}' OR m.topics IS NULL)" if category=='Não classificado' else 'json_type('+safe+',?) IS NOT NULL')+')'
                if category!='Não classificado':params+=['$.'+json.dumps(category,ensure_ascii=False)]
            if path=='/search':
                if not words:raise ValueError('Informe q')
                for word in words:
                    where+=' AND (title LIKE ? OR body LIKE ?)'
                    params+=['%'+word+'%']*2
            rows=db.execute('SELECT '+cols+' FROM items WHERE '+where+' ORDER BY captured_at DESC,source,id LIMIT ? OFFSET ?',params+[limit+1,(page-1)*limit]).fetchall()
            return {'items':[dict(x) for x in rows[:limit]],'page':page,'limit':limit,'has_more':len(rows)>limit}
        finally:db.close()
class Handler(BaseHTTPRequestHandler):
    def reply(self,status,data):
        b=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(b)));self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(b)
    def do_GET(self):
        key=os.getenv('WMK_OPEN_API_KEY','')
        if not key or not hmac.compare_digest(self.headers.get('Authorization','').encode(),('Bearer '+key).encode()):
            return self.reply(401,{'error':'Não autorizado'})
        u=urlsplit(self.path)
        if not u.path.startswith(PREFIX+'/'):return self.reply(404,{'error':'Rota inexistente'})
        try:self.reply(200,query(u.path[len(PREFIX):],parse_qs(u.query,max_num_fields=20)))
        except KeyError:self.reply(404,{'error':'Rota inexistente'})
        except ValueError:self.reply(400,{'error':'Parâmetros inválidos'})
        except sqlite3.Error:self.reply(503,{'error':'Banco indisponível ou consulta excedeu limite'})
    def do_POST(self):self.reply(405,{'error':'Somente leitura'})
    do_PUT=do_DELETE=do_PATCH=do_POST
def main():
    if len(os.getenv('WMK_OPEN_API_KEY',''))<32:raise SystemExit('Configure WMK_OPEN_API_KEY com pelo menos 32 caracteres aleatórios')
    port=int(os.getenv('WMK_OPEN_PORT','8768'))
    print('WMK Open Knowledge API: http://127.0.0.1:'+str(port)+PREFIX)
    HTTPServer(('127.0.0.1',port),Handler).serve_forever()
if __name__=='__main__':main()
