"""Servidor local WMK Intelligence: fontes por adaptadores, sem publicação externa."""
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,parse_qs
from . import __version__
from .settings import HOST,PORT,ROOT
from .store import connect,save_posts,list_posts,stats,save_assessment,save_comments
from .sources import list_sources,get_adapter
from .analyzer import classify
from .ai import report,complete
from . import studio,nexus,command,research,cyber,radar,discovery,memory
from . import arena,skills,data_export,analytrix,reactor,refinery,database_studio,factory,cognitryx

import threading,time
from datetime import datetime
collection_lock=threading.Lock()
schedule_lock=threading.Lock()
wake=threading.Event()
schedule={'enabled':False,'minutes':10,'next':None,'last':None,'message':'Desativado','busy':False}
def collect_once(body):
    source=str(body.get('source','moltbook'))
    adapter=get_adapter(source)
    items=adapter.collect(limit=max(1,min(int(body.get('limit',25)),100)))
    added=save_posts(items,source)
    for item in items:
        result=classify(str(item.get('title') or '')+' '+str(item.get('body') or ''))
        save_assessment(item['id'],result['risk'],result['terms'],source)
    return {'source':source,'obtidas':len(items),'novas':added,'total':stats()}

def configure(body):
    minutes=int(body.get('minutes',10))
    if not 10<=minutes<=1440:raise ValueError('Intervalo entre 10 e 1440 minutos')
    with schedule_lock:
        schedule.update(enabled=body.get('enabled') is True,minutes=minutes,next=time.time() if body.get('enabled') is True else None,message='Agendado' if body.get('enabled') is True else 'Desativado')
        wake.set()
        return dict(schedule)
def collector_loop():
    while True:
        with schedule_lock:
            due=schedule['enabled'] and schedule['next'] is not None and time.time()>=schedule['next']
            if due:schedule['busy']=True
        if not due:
            wake.wait(1);wake.clear();continue
        try:
            with collection_lock:
                result=collect_once({'source':'moltbook','limit':25})
            message=f"{result['obtidas']} recebidas; {result['novas']} novas"
        except Exception as exc:
            message='Falha na coleta: '+type(exc).__name__
        with schedule_lock:
            schedule.update(busy=False,last=datetime.now().isoformat(timespec='seconds'),message=message,next=time.time()+schedule['minutes']*60 if schedule['enabled'] else None)

class Handler(BaseHTTPRequestHandler):
    def send_json(self,payload,status=200):
        blob=json.dumps(payload,ensure_ascii=False).encode()
        self.send_response(status)
        for k,v in [('Content-Type','application/json; charset=utf-8'),
                    ('Content-Length',str(len(blob))),('Cache-Control','no-store'),
                    ('X-Content-Type-Options','nosniff')]:self.send_header(k,v)
        self.end_headers();self.wfile.write(blob)
    def allowed(self):
        hosts=('127.0.0.1:'+str(PORT),'localhost:'+str(PORT))
        return self.headers.get('Host','') in hosts and self.headers.get('Origin','') in ('','http://'+hosts[0],'http://'+hosts[1])
    def body(self):
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':
            raise ValueError('Somente JSON')
        n=int(self.headers.get('Content-Length','0'))
        if not 0<n<=20000:raise ValueError('Payload inválido')
        value=json.loads(self.rfile.read(n))
        if not isinstance(value,dict):raise ValueError('Objeto JSON esperado')
        return value
    def do_GET(self):
        if not self.allowed():return self.send_json({'erro':'Origem inválida'},403)
        path=urlsplit(self.path).path
        # API de leitura versionada, somente local; operações administrativas não têm alias.
        if path in ('/api/v1/health','/api/v1/stats','/api/v1/posts','/api/v1/sources'):
            path='/api/'+path.rsplit('/',1)[-1]
        if path.startswith('/api/'):
            try:
                q=parse_qs(urlsplit(self.path).query)
                if path=='/api/health':
                    return self.send_json({'ok':True,'name':'WMK Intelligence','version':__version__,'mode':'observador'})
                if path=='/api/export':
                    data,name=data_export.export(q)
                    self.send_response(200)
                    self.send_header('Content-Type','application/octet-stream')
                    self.send_header('Content-Disposition','attachment; filename="'+name+'"')
                    self.send_header('Content-Length',str(len(data)))
                    self.send_header('Cache-Control','no-store')
                    self.send_header('X-Content-Type-Options','nosniff')
                    self.end_headers();self.wfile.write(data);return
                if path=='/api/factory':return self.send_json(factory.catalog())
                if path=='/api/factory/get':return self.send_json(factory.get(q.get('id',[''])[0]))
                if path=='/api/factory/related':return self.send_json(factory.related(q.get('source',[''])[0],q.get('id',[''])[0]))
                if path=='/api/database/post':return self.send_json(database_studio.post(q.get('source',[''])[0],q.get('id',[''])[0]))
                if path=='/api/database/categories':return self.send_json(database_studio.categories())
                if path=='/api/database/catalog':return self.send_json(database_studio.catalog())
                if path=='/api/refinery':return self.send_json(refinery.overview())
                if path=='/api/reactor':return self.send_json(reactor.overview())
                if path=='/api/analytrix':return self.send_json(analytrix.overview(q.get('topic',[''])[0][:100],q.get('kind',[''])[0][:100]))
                if path=='/api/skills':return self.send_json(skills.catalog())
                if path=='/api/arena/catalog':return self.send_json({'agents':arena.catalog()})
                if path=='/api/nexus/history':return self.send_json(nexus.history())
                if path=='/api/nexus/get':return self.send_json(nexus.get(q.get('id',[''])[0]))
                if path=='/api/research/search':return self.send_json(research.search(q.get('q',[''])[0][:200]))
                if path=='/api/research/history':return self.send_json(research.history())
                if path=='/api/memory':return self.send_json(memory.search(q.get('q',[''])[0],int(q.get('page',['1'])[0])))
                if path=='/api/discovery':return self.send_json(discovery.overview())
                if path=='/api/radar':return self.send_json(radar.overview())
                if path=='/api/cyber':return self.send_json(cyber.overview())
                if path=='/api/collector':
                    with schedule_lock:return self.send_json(dict(schedule))
                if path=='/api/command':return self.send_json(command.overview())
                if path=='/api/studio':return self.send_json(studio.overview())
                if path=='/api/stats':return self.send_json(stats())
                if path=='/api/posts':
                    return self.send_json({'posts':list_posts(int(q.get('limit',['100'])[0]),q.get('q',[''])[0][:100],q.get('source',[''])[0][:64])})
                if path=='/api/agents':
                    return self.send_json(json.loads((ROOT/'config/agentes.json').read_text(encoding='utf-8')))
                if path=='/api/sources':return self.send_json({'sources':list_sources()})
                if path=='/api/status':
                    source=q.get('source',['moltbook'])[0]
                    adapter=get_adapter(source)
                    if not hasattr(adapter,'status'):raise ValueError('Fonte sem status de conta')
                    return self.send_json(adapter.status())
                return self.send_json({'erro':'Endpoint inexistente'},404)
            except (ValueError,OSError,KeyError) as exc:return self.send_json({'erro':str(exc)},400)
            except Exception as exc:
                self.log_error('Erro API GET: %s',type(exc).__name__)
                return self.send_json({'erro':'Falha ao consultar fonte'},502)
        if path=='/assets/nexus-brain.jpg':path='/nexus-brain.jpg'
        if path=='/':path='/prime.html'
        if path not in ('/cognitryx.html','/cognitryx.js','/cognitryx.png','/index.html','/app.js','/style.css','/logo.svg','/wmk_logo.png','/wmk_logo_capa.png','/arena.html','/arena.js','/arena-manual.html','/propostas.html','/nexus.html','/nexus.js','/nexus-manual.html','/command.html','/command.css','/command.js','/research.html','/research.js','/cyber.html','/cyber.js','/cyber-manual.html','/radar.html','/radar.js','/radar-manual.html','/discovery.html','/discovery.js','/discovery-manual.html','/memory.html','/memory.js','/memory-manual.html','/skills.html','/skills.js','/export.html','/analytrix.html','/analytrix.js','/reactor.html','/reactor.js','/coretrix.png','/nexus-brain.jpg','/refinery.html','/refinery.js','/refinery-manual.html','/prime.html','/prime.js','/labs.html','/labs.js','/living.html','/living.js','/scene-brain.svg','/scene-dna.svg','/scene-network.svg','/scene-globe.svg','/scene-galaxy.svg','/scene-reactor.svg','/scene-factory.svg','/scene-archive.svg','/scene-time.svg','/database-studio.html','/database-studio.js','/operations.html','/operations.js','/database-lab.png'):
            return self.send_json({'erro':'Arquivo não encontrado'},404)
        target=ROOT/'assets'/path.lstrip('/') if path in ('/cognitryx.png','/logo.svg','/wmk_logo.png','/wmk_logo_capa.png','/coretrix.png','/nexus-brain.jpg','/database-lab.png') else ROOT/'web'/path.lstrip('/')
        if path=='/cognitryx.png' and not target.is_file():
            target=ROOT/'web'/'scene-brain.svg'
            path='/scene-brain.svg'
        if not target.is_file():return self.send_json({'erro':'Arquivo não encontrado'},404)
        data=target.read_bytes()
        content_type='text/html' if path.endswith('.html') else 'text/javascript' if path.endswith('.js') else 'text/css' if path.endswith('.css') else 'image/png' if path.endswith('.png') else 'image/jpeg' if path.endswith(('.jpg','.jpeg')) else 'image/svg+xml'
        self.send_response(200)
        self.send_header('Content-Type',content_type if content_type.startswith('image/') else content_type+'; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if not self.allowed():return self.send_json({'erro':'Origem inválida'},403)
        try:
            body=self.body()
            path=urlsplit(self.path).path
            if path=='/api/cognitryx':return self.send_json(cognitryx.explore(body))
            if path=='/api/factory':return self.send_json(factory.action(body))
            if path=='/api/database/insight':return self.send_json(database_studio.insight(body))
            if path=='/api/database/copilot':return self.send_json(database_studio.copilot(body))
            if path=='/api/database/translate':return self.send_json(database_studio.translate(body))
            if path=='/api/database/query':return self.send_json(database_studio.query(body.get('sql')))
            if path=='/api/skills':return self.send_json(skills.action(body))
            if path=='/api/collector':return self.send_json(configure(body))
            if path=='/api/cyber/analyze':return self.send_json(cyber.analyze(body))
            if path=='/api/research/ask':return self.send_json(research.ask(body))
            if path=='/api/command/start':return self.send_json(command.start(body))
            if path=='/api/command/stop':return self.send_json(command.stop())
            if path=='/api/nexus/start':return self.send_json(nexus.start(body))
            if path=='/api/nexus/step':return self.send_json(nexus.step(body))
            if path=='/api/studio/post':return self.send_json(studio.action(body))
            if path=='/api/arena/turn':return self.send_json(arena.turn(body))
            if path=='/api/coletar':
                with collection_lock:return self.send_json(collect_once(body))
            if path=='/api/comments':
                source=str(body.get('source','moltbook'))
                adapter=get_adapter(source)
                if not adapter.can_comments:raise ValueError('Fonte sem comentários')
                ident=str(body.get('id') or '')
                return self.send_json({'capturados':save_comments(ident,adapter.comments(ident),source)})
            if path=='/api/relatorio':
                provider=str(body.get('provider','none'))
                if provider not in ('none','groq','ollama'):raise ValueError('Provedor inválido')
                source=str(body.get('source',''))
                return self.send_json({'texto':report(list_posts(source=source),provider),'provider':provider,'source':source})
            if path=='/api/register':
                source=str(body.get('source','moltbook'))
                adapter=get_adapter(source)
                if not adapter.can_register:raise ValueError('Fonte sem cadastro de agente')
                return self.send_json(adapter.register(str(body.get('name','')),str(body.get('description',''))))
            return self.send_json({'erro':'Endpoint inexistente'},404)
        except (ValueError,TypeError,KeyError,OSError) as exc:return self.send_json({'erro':str(exc)},400)
        except Exception as exc:
            self.log_error('Falha interna: %s',type(exc).__name__)
            return self.send_json({'erro':'Falha na operação; verifique o terminal'},502)

def main():
    if HOST not in ('127.0.0.1','localhost'):raise ValueError('Somente localhost')
    db=connect();db.close()
    print(f'WMK Intelligence {__version__} — http://{HOST}:{PORT}')
    threading.Thread(target=collector_loop,daemon=True).start()
    threading.Thread(target=memory.worker,daemon=True).start()
    threading.Thread(target=analytrix.worker,daemon=True).start()
    threading.Thread(target=refinery.worker,daemon=True).start()
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
if __name__=='__main__':main()
