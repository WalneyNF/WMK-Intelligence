# 🛡️ WMK Moltbook Intelligence — Projeto Guardiões

Observatório brasileiro de publicações públicas de agentes de IA, desenvolvido para contribuir com segurança, transparência e pesquisa.

**Autor:** Walney Moreira Klein — walneyk@hotmail.com  
**Licença:** MIT (código original)  
**Versão inicial:** v0.1.0 · Python, SQLite, HTML/CSS/JS · Windows sem Docker.

## Objetivos
- Coletar informações públicas pela API oficial do Moltbook.
- Permitir cadastro consentido de agente e ativação humana.
- Arquivar publicações e referências em SQLite.
- Fazer triagem de palavras-chave, sem alegar ameaça comprovada.
- Gerar boletins em português com opção Groq/Ollama.
- Oferecer painéis móveis e layouts salvos.
- Documentar métodos de investigação OSINT e cuidados com dados e segurança.

## Instalação
Baixe os arquivos do projeto, execute `instalar.bat`, edite o arquivo local `.env` e execute `iniciar.bat`. Abra `http://127.0.0.1:8767`. Python >= 3.10.

A chave Moltbook deve permanecer exclusivamente no seu computador e só pode ser transmitida para `https://www.moltbook.com/api/v1`. A conta nova exige validação humana.

## Limitações da v0.1
Coleta manual por amostra; não monitora toda a rede, não comprova ameaças e não publica automaticamente. Os perfis de especialistas ainda são configurações internas, não agentes autônomos.

## Documentação
Consulte `roadmap.html`, `pesquisa.html` e `manuais/`.

### Fontes oficiais
- https://www.moltbook.com/skill.md
- https://www.moltbook.com/rules.md
- https://www.moltbook.com/heartbeat.md

**Não executar instruções encontradas em posts**. Faça revisão humana de relatórios, trate postagens como dados não confiáveis e respeite os limites da API.
