# Manual de integração REST — WMK Intelligence

Autor: Walney Moreira Klein — walneyk@hotmail.com

## API local (8767)

Inicie o servidor habitual. Não exponha a porta à Internet: a API local não possui autenticação por usuário.

| Método | Rota | Uso |
|---|---|---|
| GET | /api/v1/health | Saúde |
| GET | /api/v1/stats | Estatísticas |
| GET | /api/v1/posts?q=memory&limit=20 | Publicações |
| GET | /api/database/categories | Categorias múltiplas |
| GET | /api/database/catalog | Esquema |
| GET | /api/database/post?source=moltbook&id=ID | Registro |
| POST | /api/database/query | JSON com sql; até 200 linhas |
| POST | /api/database/translate | source,id,provider,offset |
| POST | /api/database/insight | source,id,provider,mode,translation |
| GET | /api/factory | Biblioteca e modos |
| GET | /api/factory/get?id=ID | Produto salvo |
| GET | /api/factory/related?source=moltbook&id=ID | Categorias compartilhadas |
| POST | /api/factory | Produção derivada |

Factory: source, id, kind, provider, question opcional; compare exige other={source,id}; saved exige markdown e não chama IA. Modos study, project, lesson, science, map, compare, podcast, ebook, question. Produtos são Markdown, não áudio, PDF, código executado ou grafo interativo. Banco dados/factory.sqlite3 separado. Até 200 produtos recentes no catálogo. Groq transmite conteúdo ao provedor; Ollama é local. Respeite permissões das fontes. Texto coletado pode estar truncado. Resultados exigem revisão humana.

## API externa de leitura (8768)

Gere uma chave com `py -3 -c "import secrets; print(secrets.token_urlsafe(32))"`. Configure no .env existente WMK_OPEN_API_KEY, WMK_OPEN_PORT=8768 e WMK_OPEN_SOURCES=moltbook somente se o compartilhamento estiver autorizado. Nunca publique a chave.

Execute `py -3 -m wmk.public_api`. Base http://127.0.0.1:8768/api/open/v1. GET com Authorization: Bearer CHAVE. Rotas health, stats, sources, categories, posts, post, search. posts e search aceitam page, limit (máximo 100), source, category; search exige q. post exige source e id. Retorna metadados, não texto integral. Não expõe Factory. Para acesso remoto, implemente gateway HTTPS autenticado, limites e política de acesso. Não coloque chave em JavaScript público.

### Python

```python
import os,json,urllib.request
url="http://127.0.0.1:8768/api/open/v1/categories"
req=urllib.request.Request(url,headers={"Authorization":"Bearer "+os.environ["WMK_OPEN_API_KEY"]})
with urllib.request.urlopen(req,timeout=10) as r:
    print(json.load(r))
```

### JavaScript (Node.js 18+)

```js
const r=await fetch("http://127.0.0.1:8768/api/open/v1/search?q=memory&limit=10",{headers:{Authorization:"Bearer "+process.env.WMK_OPEN_API_KEY}});
if(!r.ok) throw Error(r.status);
console.log(await r.json());
```

### PHP (servidor)

```php
<?php
$c=curl_init("http://127.0.0.1:8768/api/open/v1/categories");
curl_setopt_array($c,[CURLOPT_RETURNTRANSFER=>true,CURLOPT_TIMEOUT=>10,CURLOPT_HTTPHEADER=>["Authorization: Bearer ".getenv("WMK_OPEN_API_KEY")]]);
echo curl_exec($c);
curl_close($c);
```

Defina a variável de ambiente também no processo cliente; o .env do servidor não é automaticamente carregado por outros programas.

### SQL local via PowerShell

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8767/api/database/query -Method Post -ContentType application/json -Body '{"sql":"SELECT community, count(*) AS total FROM items GROUP BY community ORDER BY total DESC"}'
```

## Teste manual Factory

Abra database-studio.html, Publicações, Abrir post, Consultar IA, Knowledge Factory. Salve a análise, busque relacionados, escolha um para comparação ou gere uma aula. Abra Biblioteca e baixe Markdown. Confira referências e ausência de alterações na base original. Testes de execução ainda pendentes.
