# Expansão para outras redes sociais de IA
A arquitetura planejada separa **coletores por fonte** de **normalização, armazenamento, análise, relatórios e UI**.

Interface sugerida de adaptador Python:

```python
class SourceAdapter:
    id: str
    def list_public_posts(self, cursor=None, limit=25): ...
    def list_public_comments(self, post_id): ...
    def capabilities(self): ...
```

Cada adaptador terá termos, versão, métodos de autenticação, limites de taxa, paginação, status, janela de coleta e campos suportados.
O esquema normalizado terá: source_id, post_id, autor_público, título, texto, timestamp e url. A proveniência original deverá ser preservada.
Só ativar adaptadores com API pública ou autorização explícita. Não burlar bloqueios ou proteções.
O arquivo config/fontes.json já registra Moltbook e uma entrada futura desabilitada.
