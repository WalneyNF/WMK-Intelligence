# Observatório aberto — Projeto Guardiões

## Missão
Democratizar o acesso em português a informações públicas de redes de agentes de IA, com educação, transparência, segurança humana e investigação verificável.

## Produtos planejados
WMK News (notícias), Investigation (OSINT), Guardian (triagem de riscos), Network (grafo público), Academy (ensino), Open Data (API), Laboratory (experimentos controlados).

## Metodologia de investigação
1. Formular pergunta verificável e delimitar fonte, período e amostra.
2. Coletar somente dados públicos autorizados; respeitar limites e termos.
3. Registrar identificador, URL, data UTC, contexto e versão do coletor.
4. Preservar original localmente com hash SHA-256; minimizar dados pessoais.
5. Traduzir e resumir separadamente, indicando uso de IA.
6. Comparar fontes independentes e buscar explicações alternativas: ficção, spam, automação, erro ou ação real.
7. Classificar evidência como alegação, indício, corroborada ou verificada. Não confundir linguagem incomum com ameaça.
8. Revisão humana antes da divulgação de incidentes; corrigir erros publicamente.
9. Encaminhar riscos concretos a responsáveis adequados, sem retaliação ou invasão.

## Portal editorial
Categorias: tecnologia, programação, ciência, segurança, comunicação entre agentes, modelos locais, cooperação humano-IA. Ranking por relevância, novidade, qualidade das evidências e diversidade de fontes, não por sensacionalismo. Cada notícia terá título PT-BR, resumo, fontes, data, limitações e status editorial.

## API pública proposta (ainda não implementada)
GET /api/v1/news
GET /api/v1/news/{id}
GET /api/v1/topics
GET /api/v1/sources
GET /api/v1/reports
GET /api/v1/methodology
GET /api/v1/coverage

Paginação, limites de taxa, versão, proveniência, documentação OpenAPI, cache e política de correções. Publicar resumos e referências, não credenciais, dados privados ou cópias integrais indiscriminadas. A licença MIT cobre o código original, não os direitos de terceiros sobre conteúdo coletado.

## Academia
Módulo 1: HTTP, JSON e APIs. Módulo 2: autenticação segura. Módulo 3: coleta e SQLite. Módulo 4: tradução e síntese. Módulo 5: OSINT e verificação. Módulo 6: prompt injection defensiva. Módulo 7: publicação responsável e API.

## Limitações
Não há garantia de cobertura total, acesso a mensagens privadas ou identificação de intenções internas. O observatório analisa evidências públicas, não presume conspirações. A versão inicial é local; hospedagem pública e revisão editorial são etapas futuras.
