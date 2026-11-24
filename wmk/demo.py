"""Importação explícita de dados sintéticos em instalação vazia."""
import json
from .settings import ROOT,DB
from .store import connect,save_posts,save_assessment
from .analyzer import classify
def main():
    if DB.exists():
        import sqlite3
        from contextlib import closing
        with closing(sqlite3.connect(DB.resolve().as_uri()+'?mode=ro',uri=True)) as db:
            tables=db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
            if tables:
                print('Banco existente: importação recusada. Use uma nova cópia do projeto, sem a pasta dados.')
                return
    posts=json.loads((ROOT/'exemplos/base_demo.json').read_text(encoding='utf-8'))
    assert all(p['source']=='demo-sintetico' for p in posts)
    count=save_posts(posts,'demo-sintetico')
    for p in posts:
        result=classify(p['title']+' '+p['body'])
        save_assessment(p['id'],result['risk'],result['terms'],'demo-sintetico')
    print(f'{count} registros SINTÉTICOS importados. Inicie o servidor para indexar.')
if __name__=='__main__':main()
