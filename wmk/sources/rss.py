"""Conector opcional RSS/Atom com URL definida pelo proprietário local."""
import ipaddress,socket,urllib.request,xml.etree.ElementTree as ET
from urllib.parse import urlparse

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):raise ValueError("Redirecionamentos proibidos")
class RSSAdapter:
    can_register=False
    can_comments=False
    def __init__(self,settings):
        self.id=settings["id"]
        self.feed_url=settings.get("feed_url") or ""
    def collect(self,limit=25):
        url=urlparse(self.feed_url)
        if url.scheme!="https" or not url.hostname or url.port not in (None,443) or url.username or url.password:
            raise ValueError("Configure um feed HTTPS válido, sem credenciais")
        resolved=socket.getaddrinfo(url.hostname,443,type=socket.SOCK_STREAM)
        if not resolved or any(not ipaddress.ip_address(r[4][0]).is_global for r in resolved):
            raise ValueError("Feed com endereço reservado, privado ou local")
        request=urllib.request.Request(self.feed_url,headers={"User-Agent":"WMK-Intelligence/0.2"})
        with urllib.request.build_opener(NoRedirect).open(request,timeout=15) as resp:
            data=resp.read(1_000_001)
        if len(data)>1_000_000:raise ValueError("Feed excede 1 MB")
        root=ET.fromstring(data)
        ns="{http://www.w3.org/2005/Atom}"
        items=root.findall("./channel/item")
        atom=not bool(items)
        if atom:items=root.findall(ns+"entry")
        output=[]
        for item in items[:max(1,min(int(limit),100))]:
            if atom:
                title=item.findtext(ns+"title") or ""
                body=item.findtext(ns+"summary") or item.findtext(ns+"content") or ""
                link=next((x.get("href","") for x in item.findall(ns+"link") if x.get("rel","alternate")=="alternate"),"")
                ident=item.findtext(ns+"id") or link
                created=item.findtext(ns+"updated") or item.findtext(ns+"published") or ""
            else:
                title=item.findtext("title") or ""
                body=item.findtext("description") or ""
                link=item.findtext("link") or ""
                ident=item.findtext("guid") or link
                created=item.findtext("pubDate") or ""
            if not ident:continue
            if urlparse(link).scheme not in ("http","https"):link=""
            output.append({"source":self.id,"id":str(ident)[:500],"title":title,"body":body,
              "author":"","community":"","url":link,"created_at":created,
              "raw":{"title":title,"body":body,"link":link}})
        return output
