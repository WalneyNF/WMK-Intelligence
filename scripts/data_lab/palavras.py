def run(rows):
    import re
    from collections import Counter
    stop=set("about there their which would could should these those have with from this that your into when what were been they them more than only same every where because before first then also just some such much many very most other after while both each over under through between being does doing done will can cannot must might may make made get got using used use here well really even still like want need know think said says tell something anything nothing everything".split())
    counts=Counter(w for r in rows for w in set(re.findall(r'\b[a-z]{4,}\b',((r["title"] or "")+" "+(r["body"] or "")).lower())) if w not in stop)
    return {"columns":["Termo","Publicações"],"rows":counts.most_common(100)}
