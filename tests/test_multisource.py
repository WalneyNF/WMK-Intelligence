"""Testes offline dos contratos multi-redes (sem conectar ao Moltbook)."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from wmk.sources.registry import get_adapter,list_sources
from wmk.sources.moltbook import MoltbookAdapter
from wmk.analyzer import classify

class MultiSourceTests(unittest.TestCase):
    def test_registry_has_moltbook_and_rss(self):
        ids={x["id"] for x in list_sources()}
        self.assertIn("moltbook",ids)
        self.assertIn("rss-ia",ids)
    def test_registry_rejects_inactive_rss(self):
        with self.assertRaisesRegex(ValueError,"desativada"):
            get_adapter("rss-ia")
    def test_registry_rejects_unknown_source(self):
        with self.assertRaises(ValueError):
            get_adapter("../etc/passwd")
    def test_normalize_moltbook(self):
        with patch("wmk.sources.moltbook.MoltbookClient") as client:
            client.return_value.posts.return_value={"posts":[{"id":"123","title":"Teste","content":"texto","author":{"name":"robot"}}]}
            adapter=MoltbookAdapter({})
            item=adapter.collect()[0]
            self.assertEqual(item["source"],"moltbook")
            self.assertEqual(item["body"],"texto")
            self.assertIn("/post/123",item["url"])
    def test_separate_ids_for_different_sources(self):
        from wmk import store
        with tempfile.TemporaryDirectory() as directory,patch.object(store,"DB",Path(directory)/"test.sqlite3"):
            items=[{"source":"moltbook","id":"42","title":"post","body":"texto","url":"https://www.moltbook.com/post/42"},
                   {"source":"rss-ia","id":"42","title":"rss","body":"outra notícia","url":"https://example.org/42"}]
            self.assertEqual(store.save_posts(items),2)
            self.assertEqual(store.save_posts(items),0)
            self.assertEqual(store.stats()["sources"],2)
            self.assertEqual(len(store.list_posts(source="moltbook")),1)
            self.assertEqual(len(store.list_posts(source="rss-ia")),1)
            store.save_assessment("42",2,["phishing"],"moltbook")
            self.assertEqual(store.stats()["alerts"],1)
    def test_migrate_legacy_database(self):
        import sqlite3
        from wmk import store
        with tempfile.TemporaryDirectory() as folder,patch.object(store,"DB",Path(folder)/"old.sqlite3"):
            db=sqlite3.connect(store.DB)
            db.execute("""CREATE TABLE posts(id TEXT PRIMARY KEY,title TEXT,body TEXT,author TEXT,submolt TEXT,source_url TEXT,created_at TEXT,captured_at TEXT,raw_json TEXT)""")
            db.execute("INSERT INTO posts VALUES(?,?,?,?,?,?,?,?,?)",("old1","Antigo","Texto","bot","general","https://www.moltbook.com/post/old1","","","{}"))
            db.commit();db.close()
            self.assertEqual(store.stats()["posts"],1)
            rows=store.list_posts(source="moltbook")
            self.assertEqual(rows[0]["id"],"old1")
            db=sqlite3.connect(store.DB)
            self.assertIsNotNone(db.execute("SELECT name FROM migrations WHERE name='legacy_v01'").fetchone())
            db.close()
    def test_no_evidence_claim(self):
        self.assertEqual(classify("phishing")["risk"],1)

if __name__=="__main__":
    unittest.main()
