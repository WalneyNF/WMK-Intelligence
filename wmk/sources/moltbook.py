"""Primeiro conector de rede, isolado do núcleo do WMK Intelligence."""
from urllib.parse import quote
from ..client import MoltbookClient

def extract(result,key):
    if isinstance(result,list):return result
    if isinstance(result,dict):
        if isinstance(result.get(key),list):return result[key]
        if isinstance(result.get("data"),dict) and isinstance(result["data"].get(key),list):return result["data"][key]
    return []

class MoltbookAdapter:
    id="moltbook"
    can_register=True
    can_comments=True
    def __init__(self,settings):
        self.client=MoltbookClient()
    def collect(self,limit=25):
        posts=extract(self.client.posts(limit=limit),"posts")
        output=[]
        for p in posts:
            if not isinstance(p,dict) or not p.get("id"):continue
            author=p.get("author") or p.get("agent") or {}
            community=p.get("submolt") or p.get("submolt_name") or ""
            output.append({"source":self.id,"id":str(p["id"]),
              "title":str(p.get("title") or ""),"body":str(p.get("content") or p.get("body") or ""),
              "author":str(author.get("name","") if isinstance(author,dict) else author),
              "community":str(community.get("name","") if isinstance(community,dict) else community),
              "url":"https://www.moltbook.com/post/"+quote(str(p["id"]),safe=""),
              "created_at":str(p.get("created_at") or ""),"raw":p})
        return output
    def comments(self,post_id):
        return extract(self.client.comments(post_id),"comments")
    def register(self,name,description):
        return self.client.register(name,description)
    def status(self):
        return self.client.status()
