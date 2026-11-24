def run(rows):
    import re
    from collections import Counter
    stop=set("about there their which would could should these those have with from this that your into when what were been they them more than".split())
    counts=Counter(w for r in rows for w in set(re.findall(r'\b[a-z]{4,}\b',((r["title"] or "")+" "+(r["body"] or "")).lower())) if w not in stop)
    return {"columns":["Termo","Publicações"],"rows":counts.most_common(100)}
