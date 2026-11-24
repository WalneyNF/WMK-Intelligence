"""API Moltbook: host fixo, sem redirecionamentos, apenas leitura e cadastro voluntário."""
import os,json,time,urllib.request,urllib.parse,urllib.error
from .settings import API_BASE
class MoltbookError(Exception):pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):raise MoltbookError('Redirecionamento bloqueado')
class MoltbookClient:
    def __init__(self,api_key=None):
        self.api_key=api_key if api_key is not None else os.getenv('MOLTBOOK_API_KEY','')
        self.opener=urllib.request.build_opener(NoRedirect())
        self.last=0
    def _request(self,path,method='GET',params=None,payload=None,authenticated=True):
        if not path.startswith('/') or '..' in path or '://' in path:raise MoltbookError('Rota inválida')
        url=API_BASE+path
        if params:url+='?'+urllib.parse.urlencode(params)
        headers={'Accept':'application/json','User-Agent':'WMK-Moltbook-Intelligence/0.1'}
        if authenticated and self.api_key:headers['Authorization']='Bearer '+self.api_key
        data=None if payload is None else json.dumps(payload).encode()
        if data is not None:headers['Content-Type']='application/json'
        wait=1-(time.monotonic()-self.last)
        if self.last and wait>0:time.sleep(wait)
        self.last=time.monotonic()
        req=urllib.request.Request(url,data=data,headers=headers,method=method)
        try:
            with self.opener.open(req,timeout=20) as r:
                data=r.read(2000001)
                if len(data)>2000000:raise MoltbookError('Resposta grande demais')
                return json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as e:raise MoltbookError('Moltbook HTTP '+str(e.code)) from e
        except (urllib.error.URLError,TimeoutError,ValueError) as e:raise MoltbookError('Erro de conexão ou resposta '+type(e).__name__) from e
    def posts(self,sort='new',limit=25,cursor=None):
        if sort not in ('new','top','hot','rising'):raise ValueError('Ordenação inválida')
        p={'sort':sort,'limit':max(1,min(int(limit),100))}
        if cursor:p['cursor']=cursor
        return self._request('/posts',params=p)
    def comments(self,post_id):
        if not post_id or not all(x.isalnum() or x in '-_' for x in str(post_id)):raise ValueError('ID inválido')
        return self._request('/posts/'+post_id+'/comments',params={'sort':'new','limit':35})
    def status(self):return self._request('/agents/status')
    def me(self):return self._request('/agents/me')
    def register(self,name,description):
        if not 3<=len(name)<=40 or not name.replace('_','').isalnum():raise ValueError('Nome inválido')
        if not 10<=len(description)<=500:raise ValueError('Descrição inválida')
        return self._request('/agents/register','POST',payload={'name':name,'description':description},authenticated=False)
