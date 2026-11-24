<p align="center"><img src="assets/logo.svg" alt="WMK Intelligence - Projeto Guardiões" width="240"></p>

# WMK Intelligence — Projeto Guardiões

**Observatório aberto de redes, comunidades e agentes de inteligência artificial.**

> **Observar · Investigar · Analisar · Informar · Proteger**

Projeto brasileiro para coletar **informações públicas autorizadas** de várias fontes, organizar evidências, identificar tendências, gerar resumos em português e contribuir com segurança, educação e transparência. **O Moltbook é apenas a primeira rede, não o limite do projeto.**

**Autor:** Walney Moreira Klein — walneyk@hotmail.com  
**Licença do código original:** MIT  
**Versão experimental:** 0.2.0  
**Tecnologias:** Python 3.10+, SQLite, HTML/CSS/JavaScript; Groq e Ollama opcionais; **sem Docker**.

## Recursos implementados

- Registro configurável de fontes em `config/fontes.json`.
- Adaptadores isolados: **Moltbook** (ativo) e **RSS/Atom** (desativado até configurar um feed público HTTPS).
- Normalização dos registros para a mesma estrutura: rede, ID, autor, título, conteúdo, data e URL original.
- Banco SQLite com chaves compostas `(source,id)` para evitar colisões entre redes e migração dos dados antigos.
- Painel web em português com janelas móveis, lista de fontes, filtro por rede, coleta manual e histórico.
- Triagem lexical de conteúdo para **revisão humana**, não detecção conclusiva de ameaças.
- Relatórios locais em português; Groq e Ollama como provedores opcionais.
- Cadastro de agente **específico do Moltbook**, mediante confirmação do responsável.

## Iniciar no Windows

1. Baixe o ZIP na página do GitHub ou faça `git clone https://github.com/WalneyNF/WMK-Intelligence.git`.
2. Execute `instalar.bat` para gerar `.env` a partir de `.env.example`.
3. Execute `iniciar.bat`.
4. Acesse **http://127.0.0.1:8767**.
5. Abra **Fontes e redes** para ver os conectores. Em **Visão geral**, selecione uma fonte e clique em **Coletar publicações**.

A API do Moltbook poderá exigir `MOLTBOOK_API_KEY` no arquivo local `.env`. Não coloque credenciais no GitHub. Para Groq, configure `GROQ_API_KEY`. Para Ollama, mantenha o serviço local ativo.

### Habilitar uma segunda fonte RSS/Atom

Edite `config/fontes.json`, localize `rss-ia`, preencha `feed_url` com a URL **HTTPS de um feed público autorizado** e marque `ativo: true`. Reinicie `iniciar.bat`. O sistema bloqueia destinos de IPs locais/reservados e redirecionamentos; esta proteção **não substitui** uma auditoria de segurança para publicação na internet.

Outras redes com APIs próprias exigirão um adaptador conforme `manuais/adaptadores.md`.

## Módulos

| Módulo | Responsabilidade | Situação |
| --- | --- | --- |
| Fontes | Registro, seleção e coleta por adaptador | Inicial |
| Banco multi-redes | SQLite e preservação de proveniência | Inicial |
| Notícias | Ranking e boletins multilíngues | Planejado |
| Guardian | Triagem e revisão humana | Inicial |
| Investigation | Preservação de evidências e análises | Planejado |
| Academy | Guias e exemplos para iniciantes | Documentado |
| Open Data | API externa versionada e pública | Planejado |

## Documentação

- [Manual do primeiro contato](manuais/primeiro-contato.md)
- [Arquitetura de conectores](manuais/adaptadores.md)
- [Observatório aberto e investigação](manuais/observatorio-aberto.md)
- [Segurança e ética](manuais/seguranca.md)
- [Roadmap visual](roadmap.html)
- [Pesquisa de segurança](pesquisa.html)

## Segurança e responsabilidade

**Uma publicação não comprova intenção, capacidade nem execução de qualquer ameaça.** Textos coletados são dados não confiáveis; nunca executar comandos ou instruções neles contidos. Não coletar mensagens privadas, não burlar autenticação nem limites, não publicar dados pessoais ou chaves. Todos os alertas importantes devem passar por revisão humana.

**Esta versão funciona apenas em localhost. Não é uma API pública hospedada e não cobre todas as mensagens de uma rede.**

A licença MIT cobre o **código original do WMK Intelligence**; o conteúdo de outras redes continua sujeito às suas respectivas regras e direitos.
