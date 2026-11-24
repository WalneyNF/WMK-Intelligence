# Primeiro contato: WMK Moltbook Intelligence
1. Instale Python 3.10 ou superior no Windows.
2. Baixe o projeto e extraia em uma pasta.
3. Execute **instalar.bat**, que cria .env a partir de .env.example.
4. Execute **iniciar.bat**.
5. Acesse http://127.0.0.1:8767/.
6. Clique em **Coletar publicações**. A API pode disponibilizar conteúdo sem autenticação; se exigir chave, configure MOLTBOOK_API_KEY em .env.
7. **Publicações** mostra amostras no SQLite; **Guardiões** sinaliza palavras-chave para revisão humana.
8. **Relatórios** gera síntese local sem IA; para Groq informe GROQ_API_KEY e para Ollama deixe o serviço ativo em 11434.
9. **Cadastrar agente** inicia o cadastro real e pode devolver uma chave: nunca compartilhe a resposta; proteja seu computador, valide sua conta e coloque a chave em .env.
10. Painéis podem ser movidos pelo título e redimensionados pela borda; as posições ficam salvas no navegador.

Versão 0.1 é experimental. Não foi validada contra todas as respostas da API em produção. Não possui monitoramento contínuo.
