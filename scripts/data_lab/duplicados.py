def run(rows):
    from collections import defaultdict
    import hashlib
    groups=defaultdict(list)
    for r in rows:
        body=(r["body"] or "").strip()
        if body:groups[hashlib.sha256(body.encode()).hexdigest()].append(r["id"])
    return {"columns":["Hash","Total","IDs"],"rows":[[h,len(ids),", ".join(ids)] for h,ids in groups.items() if len(ids)>1]}
