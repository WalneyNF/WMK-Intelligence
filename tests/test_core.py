import unittest,tempfile
from unittest.mock import patch
from wmk.analyzer import classify,summarize_local
from wmk.client import MoltbookClient,MoltbookError
class CoreTests(unittest.TestCase):
    def test_neutral(self):self.assertEqual(classify('python and blender')['risk'],0)
    def test_signal_not_proof(self):self.assertEqual(classify('A discussion of phishing')['risk'],1)
    def test_double_signal(self):self.assertEqual(classify('phishing and ransomware')['risk'],2)
    def test_report(self):self.assertIn('1 publicações',summarize_local([{'title':'Teste'}]))
    def test_reject_invalid_sort(self):
        with self.assertRaises(ValueError):MoltbookClient().posts(sort='hack')
    def test_reject_invalid_id(self):
        with self.assertRaises(ValueError):MoltbookClient().comments('https://elsewhere.test/')
if __name__=='__main__':unittest.main()
