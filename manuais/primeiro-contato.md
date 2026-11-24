# Primeiro contato — WMK Intelligence

**Projeto Guardiões · Observatório de múltiplas redes de IA · v0.2.0**

1. Instale Python 3.10 ou mais novo no Windows.
2. Baixe o repositório [WMK-Intelligence](https://github.com/WalneyNF/WMK-Intelligence).
3. Extraia e execute `instalar.bat`, que criará `.env` com valores locais.
4. Execute `iniciar.bat` e abra http://127.0.0.1:8767.
5. No menu **Fontes e redes**, veja as redes configuradas. Por padrão, Moltbook é a primeira e RSS está desligado.
6. Selecione a fonte na tela inicial e clique em **Coletar publicações**.
7. Os registros são salvos com fonte e ID exclusivos em `dados/wmk.sqlite3`.
8. Use **Publicações** para filtrar por rede, **Guardiões** para triagem e **Relatórios** para síntese em português.
9. Para ativar um RSS público, edite `config/fontes.json`, coloque `feed_url` HTTPS real e altere `ativo` para `true`.
10. O cadastro de agentes é específico do Moltbook por enquanto e requer confirmação humana.

**Não é necessário Docker.** Painéis podem ser movidos e redimensionados. Salve sua chave de API apenas em `.env`.

**Limitações:** esta versão coleta amostras manualmente, não monitora toda a internet e não confirma ameaças automaticamente.
