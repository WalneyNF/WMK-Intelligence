def run(rows):
    from collections import Counter
    return {"columns":["Comunidade","Total"],"rows":Counter(r["community"] or "(sem comunidade)" for r in rows).most_common()}
