"""Servidor local do observatório WMK: não exponha na internet."""
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs
from .settings import HOST,PORT,ROOT
from .client import MoltbookClient,MoltbookError
from .store import connect,save_posts,list_posts,stats,save_assessment,save_comments
from .analyzer import classify
from .ai import report
from . import __version__
def extract_items(data,key):
    if isinstance(data,list):return data
    if isinstance(data,dict):
        if isinstance(data.get(key),list):return data[key]
        if isinstance(data.get('data'),dict) and isinstance(data['data'].get(key),list):return data['data'][key]
    return []
class Handler(BaseHTTPRequestHandler):
    def send_json(self,obj,status=200):
        blob=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status)
        for k,v in [('Content-Type','application/json; charset=utf-8'),('Content-Length',str(len(blob))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff')]:self.send_header(k,v)
        self.end_headers();self.wfile.write(blob)
    def allowed(self):
        hosts=('127.0.0.1:'+str(PORT),'localhost:'+str(PORT))
        return self.headers.get('Host','') in hosts and self.headers.get('Origin','') in ('','http://'+hosts[0],'http://'+hosts[1])
    def body(self):
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise ValueError('Somente JSON')
        n=int(self.headers.get('Content-Length','0'))
        if not 0<n<=20000:raise ValueError('Tamanho inválido')
        return json.loads(self.rfile.read(n))
    def do_GET(self):
        if not self.allowed():return self.send_json({'erro':'Origem inválida'},403)
        path=urlsplit(self.path).path
        if path.startswith('/api/'):
            try:
                query=parse_qs(urlsplit(self.path).query)
                if path=='/api/health':return self.send_json({'ok':True,'version':__version__,'mode':'observador'})
                if path=='/api/stats':return self.send_json(stats())
                if path=='/api/posts':return self.send_json({'posts':list_posts(min(int(query.get('limit',['100'])[0]),300),query.get('q',[''])[0][:100])})
                if path=='/api/agents':return self.send_json(json.loads((ROOT/'config/agentes.json').read_text(encoding='utf-8')))
                if path=='/api/sources':return self.send_json(json.loads((ROOT/'config/fontes.json').read_text(encoding='utf-8')))
                if path=='/api/status':return self.send_json(MoltbookClient().status())
                return self.send_json({'erro':'Rota inexistente'},404)
            except (ValueError,MoltbookError,OSError) as exc:return self.send_json({'erro':str(exc)},400)
        if path=='/':path='/index.html'
        if path not in ('/index.html','/app.js','/style.css','/logo.svg'):return self.send_json({'erro':'Não encontrado'},404)
        f=ROOT/'assets/logo.svg' if path=='/logo.svg' else ROOT/'web'/path.lstrip('/')
        if not f.is_file():return self.send_json({'erro':'Arquivo não encontrado'},404)
        blob=f.read_bytes()
        mime='text/html' if path.endswith('.html') else 'text/javascript' if path.endswith('.js') else 'text/css' if path.endswith('.css') else 'image/svg+xml'
        self.send_response(200);self.send_header('Content-Type',mime+'; charset=utf-8');self.send_header('Content-Length',str(len(blob)));self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(blob)
    def do_POST(self):
        if not self.allowed():return self.send_json({'erro':'Origem inválida'},403)
        try:
            b=self.body();path=urlsplit(self.path).path
            if path=='/api/coletar':
                data=MoltbookClient().posts(limit=min(max(int(b.get('limit',25)),1),100))
                items=extract_items(data,'posts')
                added=save_posts(items)
                for item in items:
                    if not isinstance(item,dict) or not item.get('id'):continue
                    r=classify(str(item.get('title') or '')+' '+str(item.get('content') or item.get('body') or ''))
                    save_assessment(str(item['id']),r['risk'],r['terms'])
                return self.send_json({'obtidas':len(items),'novas':added,'total':stats()})
            if path=='/api/comments':
                pid=str(b.get('id',''));data=MoltbookClient().comments(pid)
                return self.send_json({'capturados':save_comments(pid,extract_items(data,'comments'))})
            if path=='/api/relatorio':
                provider=str(b.get('provider','none'))
                if provider not in ('none','groq','ollama'):raise ValueError('Provedor inválido')
                return self.send_json({'texto':report(list_posts(),provider),'provider':provider})
            if path=='/api/register':
                return self.send_json(MoltbookClient().register(str(b.get('name','')),str(b.get('description',''))))
            return self.send_json({'erro':'Rota inexistente'},404)
        except (ValueError,TypeError,KeyError,MoltbookError,OSError) as exc:return self.send_json({'erro':str(exc)},400)
        except Exception as exc:
            self.log_error('Falha interna: %s',type(exc).__name__)
            return self.send_json({'erro':'Falha interna; verifique terminal'},500)
def main():
    if HOST not in ('127.0.0.1','localhost'):raise ValueError('Somente localhost')
    db=connect();db.close()
    print(f'WMK Moltbook Intelligence {__version__} — http://{HOST}:{PORT}')
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
if __name__=='__main__':main()
