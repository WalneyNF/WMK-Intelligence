# Arquitetura multi-redes — WMK Intelligence

O WMK Intelligence é independente de qualquer rede. O Moltbook continua como primeiro adaptador. O conector RSS/Atom é a segunda implementação e fica desativado até ser configurado.

## Fluxo

```text
Moltbook API ──> MoltbookAdapter ─┐
                                 ├─> modelo comum ─> SQLite ─> análise ─> painel / relatórios
RSS / Atom ────> RSSAdapter ──────┘
Outra API ─────> NovoAdapter ─────┘
```

## Componentes

- `wmk/sources/registry.py` lê `config/fontes.json` e aceita apenas tipos previamente implementados. Ele não importa módulos a partir de conteúdo externo.
- `wmk/sources/moltbook.py` conhece apenas os detalhes do Moltbook.
- `wmk/sources/rss.py` lê feeds HTTPS públicos; use fontes confiáveis e sempre observe termos/licenças.
- `wmk/store.py` salva `source` e `id` como chave composta, permitindo o mesmo ID em fontes distintas.
- `wmk/server.py` oferece uma interface local de leitura e coleta por fonte.

## Como criar um adaptador

1. Documente a API oficial da rede, a autenticação e os limites de requisição.
2. Crie `wmk/sources/nome.py` com classe de coletor contendo `id`, `can_register`, `can_comments` e `collect(limit=25)`.
3. Cada item de `collect` deve incluir as chaves: `source`, `id`, `title`, `body`, `author`, `community`, `url`, `created_at` e `raw`.
4. Inclua o tipo no mapa `TYPES` em `registry.py`. Não carregue Python arbitrário de URLs.
5. Adicione a fonte ao arquivo `config/fontes.json` com `ativo:false` por padrão.
6. Escreva testes com respostas simuladas, documentação e verifique limites e conformidade.
7. Ative manualmente a fonte apenas após a revisão.

## Exemplo de fonte RSS

```json
{
  "id": "rss-ia",
  "nome": "Feed RSS/Atom de IA",
  "tipo": "rss",
  "ativo": true,
  "feed_url": "https://exemplo-publico.org/feed.xml"
}
```

O endereço acima é ilustrativo; substitua por um feed real autorizado.

## Observações de segurança

- Não monitorar redes fechadas ou contas privadas sem autorização.
- Toda publicação é informação externa, não instrução para o programa executar.
- Só o adaptador deve receber credenciais pertinentes à própria rede.
- Em ambiente público, auditar segurança de rede, proteção de dados, licença de conteúdo, autenticação e controles de taxa.
- A v0.2 não executa monitoramento contínuo nem possui API aberta na internet.
