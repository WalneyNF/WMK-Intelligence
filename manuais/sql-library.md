# WMK SQL Library — Manual de aprendizagem

Walney Moreira Klein — walneyk@hotmail.com

Abra http://127.0.0.1:8767/sql-library.html após reiniciar o servidor. Selecione uma consulta, leia a descrição e execute. Edite e salve uma cópia; exemplos oficiais são imutáveis. Consultas pessoais ficam em dados/sql-library.sqlite3. Exporte JSON para compartilhar somente a definição, não os resultados. Importe como rascunho e revise.

## Estrutura

items: publicações; knowledge_memory: índice temático; assessments_v2: avaliações lexicais; comments_v2: comentários. Relacione registros por source e id (post_id nas avaliações). A memória original é somente leitura. O executor limita a 200 linhas e 3 segundos. Consultas de memória dependem da indexação. Busca lexical não comprova utilidade nem veracidade.

## Exemplos comentados

### Total de publicações — Fundamentos

COUNT conta registros.

```sql
SELECT count(*) AS total FROM items
```

### Últimas publicações — Fundamentos

ORDER BY ordena; LIMIT restringe.

```sql
SELECT source,id,title,source_url FROM items ORDER BY captured_at DESC LIMIT 30
```

### Comunidades mais ativas — BI

GROUP BY agrega por comunidade.

```sql
SELECT community,count(*) AS total FROM items GROUP BY community ORDER BY total DESC
```

### Coleta por dia — BI

date extrai a data de coleta.

```sql
SELECT date(captured_at) AS dia,count(*) AS total FROM items GROUP BY date(captured_at) ORDER BY dia DESC
```

### Fontes — BI

Contagem por origem.

```sql
SELECT source,count(*) AS total FROM items GROUP BY source ORDER BY total DESC
```

### Cobertura de indexação — Memória

LEFT JOIN encontra registros sem índice.

```sql
SELECT count(*) AS pendentes FROM items i LEFT JOIN knowledge_memory m ON i.source=m.source AND i.id=m.id WHERE m.id IS NULL
```

### Temas indexados — Memória

Pesquisa lexical nas etiquetas JSON.

```sql
SELECT i.source,i.id,i.title,m.topics,i.source_url FROM items i JOIN knowledge_memory m ON i.source=m.source AND i.id=m.id WHERE m.topics LIKE '%Programação%' LIMIT 100
```

### Avaliações de risco — Segurança

Risco lexical não comprova incidente.

```sql
SELECT i.source,i.id,i.title,a.risk,i.source_url FROM items i JOIN assessments_v2 a ON i.source=a.source AND i.id=a.post_id ORDER BY a.risk DESC LIMIT 50
```

### RAG e memória — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%rag%' OR lower(body) LIKE '%rag%') OR (lower(title) LIKE '%retrieval%' OR lower(body) LIKE '%retrieval%') OR (lower(title) LIKE '%embedding%' OR lower(body) LIKE '%embedding%') ORDER BY captured_at DESC LIMIT 100
```

### MCP — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%model context protocol%' OR lower(body) LIKE '%model context protocol%') OR (lower(title) LIKE '%mcp%' OR lower(body) LIKE '%mcp%') ORDER BY captured_at DESC LIMIT 100
```

### Python — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%python%' OR lower(body) LIKE '%python%') ORDER BY captured_at DESC LIMIT 100
```

### SQLite — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%sqlite%' OR lower(body) LIKE '%sqlite%') OR (lower(title) LIKE '%database index%' OR lower(body) LIKE '%database index%') ORDER BY captured_at DESC LIMIT 100
```

### Ollama — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%ollama%' OR lower(body) LIKE '%ollama%') OR (lower(title) LIKE '%local model%' OR lower(body) LIKE '%local model%') ORDER BY captured_at DESC LIMIT 100
```

### Jogos — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%game engine%' OR lower(body) LIKE '%game engine%') OR (lower(title) LIKE '%godot%' OR lower(body) LIKE '%godot%') OR (lower(title) LIKE '%three.js%' OR lower(body) LIKE '%three.js%') ORDER BY captured_at DESC LIMIT 100
```

### Soluções — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%solution%' OR lower(body) LIKE '%solution%') OR (lower(title) LIKE '%workaround%' OR lower(body) LIKE '%workaround%') OR (lower(title) LIKE '%fixed%' OR lower(body) LIKE '%fixed%') ORDER BY captured_at DESC LIMIT 100
```

### Problemas — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%problem%' OR lower(body) LIKE '%problem%') OR (lower(title) LIKE '%failure%' OR lower(body) LIKE '%failure%') OR (lower(title) LIKE '%bug%' OR lower(body) LIKE '%bug%') ORDER BY captured_at DESC LIMIT 100
```

### Experimentos — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%experiment%' OR lower(body) LIKE '%experiment%') OR (lower(title) LIKE '%benchmark%' OR lower(body) LIKE '%benchmark%') OR (lower(title) LIKE '%baseline%' OR lower(body) LIKE '%baseline%') ORDER BY captured_at DESC LIMIT 100
```

### Ferramentas — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%library%' OR lower(body) LIKE '%library%') OR (lower(title) LIKE '%framework%' OR lower(body) LIKE '%framework%') OR (lower(title) LIKE '%tool%' OR lower(body) LIKE '%tool%') ORDER BY captured_at DESC LIMIT 100
```

### Desempenho — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%latency%' OR lower(body) LIKE '%latency%') OR (lower(title) LIKE '%performance%' OR lower(body) LIKE '%performance%') OR (lower(title) LIKE '%optimization%' OR lower(body) LIKE '%optimization%') ORDER BY captured_at DESC LIMIT 100
```

### Arquitetura — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%architecture%' OR lower(body) LIKE '%architecture%') OR (lower(title) LIKE '%design pattern%' OR lower(body) LIKE '%design pattern%') ORDER BY captured_at DESC LIMIT 100
```

### APIs — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%rest api%' OR lower(body) LIKE '%rest api%') OR (lower(title) LIKE '%endpoint%' OR lower(body) LIKE '%endpoint%') ORDER BY captured_at DESC LIMIT 100
```

### Segurança defensiva — Mineração

Busca por termos em inglês; resultados são candidatos, não evidências verificadas.

```sql
SELECT source,id,title,substr(body,1,500) AS trecho,source_url FROM items WHERE (lower(title) LIKE '%least privilege%' OR lower(body) LIKE '%least privilege%') OR (lower(title) LIKE '%authorization%' OR lower(body) LIKE '%authorization%') OR (lower(title) LIKE '%input validation%' OR lower(body) LIKE '%input validation%') ORDER BY captured_at DESC LIMIT 100
```

## API REST local

GET /api/sql-library lista definições. POST /api/sql-library com op=run e sql executa; op=save com name, category, description, sql e id opcional cadastra; op=delete com id exclui consulta pessoal.

```powershell
Invoke-RestMethod http://127.0.0.1:8767/api/sql-library
```

## Exercícios

1. Altere LIMIT 30 para 10.
2. Troque python por javascript em uma cópia da busca.
3. Compare total de publicações com pendentes de indexação.
4. Crie uma consulta por comunidade e compartilhe seu JSON.

Não publique dados privados ou credenciais. Não exponha o servidor diretamente à internet.
