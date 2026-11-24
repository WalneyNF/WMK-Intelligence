"""Exportação local, somente leitura, sem raw_json ou autor."""
import csv,io,json,sqlite3
from contextlib import closing
from .settings import DB
FIELDS={
'posts':('items',('source','id','title','body','community','source_url','created_at','captured_at')),
'comments':('comments_v2',('source','id','post_id','body','captured_at')),
'assessments':('assessments_v2',('source','post_id','risk','terms','summary','updated_at')),
'memory':('knowledge_memory',('source','id','version','topics','security','indexed_at'))}
def export(q):
    def arg(k,d=''):return q.get(k,[d])[0]
    dataset=arg('dataset','posts');fmt=arg('format','json')
    if dataset not in FIELDS or fmt not in ('json','jsonl','csv','sql'):raise ValueError('Formato ou conjunto inválido')
    table,cols=FIELDS[dataset]
    limit=max(1,min(int(arg('limit','1000')),10000))
    offset=max(0,min(int(arg('offset','0')),10000000))
    source=arg('source')[:64]
    out=io.StringIO()
    with closing(sqlite3.connect(DB.resolve().as_uri()+'?mode=ro',uri=True,timeout=5)) as db:
        db.execute('PRAGMA query_only=ON')
        db.row_factory=sqlite3.Row
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone():raise ValueError('Conjunto ainda indisponível')
        rows=db.execute('SELECT '+','.join(cols)+' FROM '+table+" WHERE (?='' OR source=?) ORDER BY source,"+('post_id' if dataset=='assessments' else 'id')+' LIMIT ? OFFSET ?',(source,source,limit,offset))
        if fmt=='csv':
            writer=csv.writer(out);writer.writerow(cols)
        elif fmt=='json':out.write('[')
        elif fmt=='sql':
            out.write('BEGIN;\nCREATE TABLE IF NOT EXISTS wmk_export_'+dataset+' ('+','.join('"'+c+'" '+('INTEGER' if c in ('risk','version') else 'TEXT') for c in cols)+');\n')
        count=0
        for row in rows:
            if fmt=='csv':
                writer.writerow([("'"+v if isinstance(v,str) and (v.lstrip().startswith(('=','+','-','@')) or v.startswith(('\t','\r','\n'))) else v) for v in row])
            elif fmt=='json':
                out.write((',' if count else '')+json.dumps(dict(row),ensure_ascii=False))
            elif fmt=='jsonl':out.write(json.dumps(dict(row),ensure_ascii=False)+'\n')
            else:
                vals=[('NULL' if v is None else str(v) if isinstance(v,int) else "CAST(X'"+str(v).encode('utf-8').hex()+"' AS TEXT)") for v in row]
                out.write('INSERT INTO wmk_export_'+dataset+' VALUES ('+','.join(vals)+');\n')
            count+=1
            if out.tell()>16000000:raise ValueError('Exportação muito grande; reduza o limite')
        if fmt=='json':out.write(']')
        if fmt=='sql':out.write('COMMIT;\n')
    return out.getvalue().encode('utf-8-sig' if fmt=='csv' else 'utf-8'), 'wmk_'+dataset+'_'+str(offset)+'.'+fmt
