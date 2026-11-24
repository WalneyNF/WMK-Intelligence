"""Triagem lexical; NÃO comprova ameaças ou intenções."""
import re
TERMS={'phishing':['phishing','credential theft'],'malware':['ransomware','keylogger','botnet','malware'],'violencia':['kill humans','harm humans','attack humans'],'manipulacao':['prompt injection','social engineering'],'vazamento':['leaked api key','exposed token','data breach']}
def classify(text):
    found=[k for k,patterns in TERMS.items() if any(re.search(r'(?i)\b'+re.escape(s)+r'\b',text) for s in patterns)]
    return {'risk':2 if len(found)>1 else 1 if found else 0,'terms':found,'notice':'Triagem temática, sujeito a falso positivo'}
def summarize_local(posts):
    freq={}
    for p in posts:
        for term in classify(str(p.get('title',''))+' '+str(p.get('body','')))['terms']:freq[term]=freq.get(term,0)+1
    return '\n'.join([f'Boletim WMK — {len(posts)} publicações na amostra.','Esta coleta não representa toda a rede.','Tópicos para revisão humana:']+[f'- {k}: {v} menções' for k,v in sorted(freq.items())]) if freq else f'Boletim WMK: {len(posts)} publicações analisadas. Nenhum termo da lista detectado.'
