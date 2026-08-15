import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from rag_engine import UXLensEngine  # noqa: E402


class UXLensEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = UXLensEngine(enable_models=False)

    def test_knowledge_base_loads(self):
        self.assertGreaterEqual(len(self.engine.chunks), 20)

    def test_feedback_query_retrieves_status_guidance(self):
        results = self.engine.retrieve("save button gives no feedback after click", top_k=5)
        titles = {result.chunk.title for result in results}
        self.assertIn("Visibility of System Status", titles)

    def test_color_query_retrieves_accessibility_guidance(self):
        results = self.engine.retrieve("error shown only with red color", top_k=5)
        titles = {result.chunk.title for result in results}
        self.assertIn("Do Not Rely on Color Alone", titles)

    def test_empty_query_is_handled(self):
        self.assertIn("describe", self.engine.answer("").lower())

    def test_prompt_is_grounded(self):
        results = self.engine.retrieve("form clears valid input after an error", top_k=3)
        prompt = self.engine.build_prompt("form clears valid input", results)
        self.assertIn("Use ONLY the supplied HCI context", prompt)
        self.assertIn("### Recommended redesign", prompt)


if __name__ == "__main__":
    unittest.main()
