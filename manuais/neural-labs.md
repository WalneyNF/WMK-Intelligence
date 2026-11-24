# Laboratórios neurais v0.1

Walney Moreira Klein — walneyk@hotmail.com

Reinicie o servidor. Abra /universe.html ou /council.html pela central. Universo: arraste, zoom com scroll, clique em estrela, filtre comunidade. Projeção 3D em Canvas 2D, sem dependências externas. Posições ilustrativas, não similaridade semântica. Até 1000 registros por padrão.

Conselho: informe termo inglês (memory, security, MCP), pergunta em português e provedor. Seis chamadas sequenciais, acompanhe estados e histórico em dados/council. Groq exige consentimento. Respostas não são verificações independentes. Falha interrompe reunião e preserva turnos; reinício pode deixar estado running obsoleto. Não publique históricos.

## REST local

GET /api/universe?q=memory&limit=1000 (máximo 3000). GET /api/council/history. GET /api/council/get?id=ID. POST /api/council com JSON question, search, provider, consent. Retorna id; consulte estado a cada 3 segundos. Não exponha a porta local.

```js
const d=await fetch('/api/universe').then(r=>r.json());
console.log(d.nodes);
```

```powershell
Invoke-RestMethod http://127.0.0.1:8767/api/universe
```

Testes integrados pendentes. Markdown bruto no conselho, tradução e investigação por estrela planejadas.