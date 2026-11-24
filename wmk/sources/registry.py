"""Registro seguro de adaptadores (somente tipos permitidos)."""
import json,re
from ..settings import ROOT
from .moltbook import MoltbookAdapter
from .rss import RSSAdapter

TYPES={"moltbook":MoltbookAdapter,"rss":RSSAdapter}
def config():
    return json.loads((ROOT/"config"/"fontes.json").read_text(encoding="utf-8"))["fontes"]
def list_sources():
    return [{"id":s["id"],"nome":s["nome"],"tipo":s["tipo"],"ativo":bool(s.get("ativo")),
             "status":s.get("status","experimental"),"descricao":s.get("descricao",""),
             "cadastro":s["tipo"]=="moltbook","comentarios":s["tipo"]=="moltbook"} for s in config()]
def get_adapter(source_id):
    if not isinstance(source_id,str) or not re.fullmatch("[a-z0-9_-]{2,64}",source_id):
        raise ValueError("Identificador de fonte inválido")
    source=next((s for s in config() if s["id"]==source_id),None)
    if not source:raise ValueError("Fonte desconhecida")
    if not source.get("ativo"):raise ValueError("Fonte desativada; configure em config/fontes.json")
    cls=TYPES.get(source["tipo"])
    if not cls:raise ValueError("Tipo de fonte não suportado")
    return cls(source)
