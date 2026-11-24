"""Radar defensivo: referências públicas, não atribuição de intenção."""
import re,hashlib,json
from .store import connect
RULES={
 'Injeção de prompt':r'prompt injection|injection de prompt|ignore previous instructions',
 'Integridade de dados':r'data poisoning|memory poisoning|contaminação de dados',
 'Controle de acesso':r'privilege escalation|allowlist|authorization|access control',
 'Exposição de dados':r'data leak|credential leak|secret exposure',
 'Vulnerabilidades':r'\bCVE-\d{4}-\d{4,}\b',
 'Segurança de ferramentas':r'tool abuse|MCP security|tool injection',
 'Fraude e engano':r'phishing|fraud|disinformation'
}
def overview():
    c=connect()
    try: rows=[dict(x) for x in c.execute('SELECT source,id,title,body,source_url FROM items ORDER BY captured_at DESC LIMIT 1000')]
    finally:c.close()
    events=[]; counts={k:0 for k in RULES}
    for p in rows:
        body=str(p.get('body') or ''); title=str(p.get('title') or '')
        tags=[k for k,v in RULES.items() if re.search(v,title+' '+body,re.I)]
        for k in tags:counts[k]+=1
        if tags:
            events.append({'source':p['source'],'id':p['id'],'title':title,'url':p['source_url'],'topics':tags,'excerpt':body[:700],'sha256':hashlib.sha256(json.dumps(p,sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
    return {'sample':len(rows),'counts':counts,'events':events}
