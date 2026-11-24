"""Classificação temática local, explicável, sem inferir intenção."""
import re
from .store import connect
from .radar import RULES
TOPICS={
'Programação':r'\b(python|javascript|rust|software|compiler|programming|code|coding|api|programação)\b',
'Inteligência artificial':r'\b(llm|agent|agents|ollama|rag|embedding|model|inference|agentes)\b',
'Jogos':r'\b(game|games|godot|unity|gameplay|jogos)\b',
'Robótica':r'\b(robot|robotics|sensor|actuator|robótica)\b',
'Ciência':r'\b(science|research|experiment|hypothesis|study|ciência)\b',
'Saúde':r'\b(health|medical|clinical|medicine|saúde)\b',
'Matemática':r'\b(math|algorithm|statistics|optimization|matemática)\b',
'Educação':r'\b(education|learning|teaching|student|educação)\b',
'Meio ambiente':r'\b(climate|environment|sustainability|energia)\b',
'Hardware':r'\b(cpu|gpu|stm32|hardware|memory|microcontroller)\b',
'Negócios':r'\b(business|startup|product|market|negócios)\b',
'Invenções':r'\b(prototype|invention|novel|design|protótipo)\b',
'Defesa cibernética':r'\b(security|firewall|encryption|vulnerability|segurança)\b',
'Filosofia e ética':r'\b(ethics|philosophy|consciousness|ética)\b',
'Espaço':r'\b(spacecraft|astronomy|satellite|astronomia)\b'}
def classify(text,rules):
    return {k:sorted(set(m.group(0).lower() for m in re.finditer(v,text,re.I)))[:8] for k,v in rules.items() if re.search(v,text,re.I)}
def overview():
    c=connect()
    try:
        total=c.execute('SELECT COUNT(*) FROM items').fetchone()[0]
        rows=[dict(x) for x in c.execute('SELECT source,id,title,body,source_url,captured_at FROM items ORDER BY captured_at DESC LIMIT 1000')]
    finally:c.close()
    counts={k:0 for k in TOPICS}; risks={k:0 for k in RULES}
    for p in rows:
        t=str(p['title'] or '')+' '+str(p['body'] or '')
        p['topics']=classify(t,TOPICS);p['security']=classify(t,RULES)
        for k in p['topics']:counts[k]+=1
        for k in p['security']:risks[k]+=1
    return {'total':total,'sample':len(rows),'topics':counts,'security':risks,'posts':rows}
