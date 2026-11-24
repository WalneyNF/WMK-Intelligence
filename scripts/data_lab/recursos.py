def run(rows):
    import re
    return {"columns":["ID","URL","Fonte"],"rows":[[r["id"],url,r["source_url"]] for r in rows for url in sorted(set(re.findall(r'https?://[^\s<>"\)]+',r["body"] or "")))]}
