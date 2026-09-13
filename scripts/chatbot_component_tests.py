"""Offline tests of native accelerator components, NOT model/end-to-end tests."""
import ast
import os
from pathlib import Path
import sys
import unittest

REPO = Path(__file__).resolve().parents[3] / "repo" / "customer-chatbot-solution-accelerator"
os.environ["DEPLOYMENT_SCENARIO"] = "ecommerce"
sys.path.insert(0, str(REPO / "chat-app" / "backend"))
sys.path.insert(0, str(REPO))

from app.scenario_config import catalog_tool_name, policy_tool_name, welcome_config
from app.utils.product_catalog import ecommerce_catalog_by_title
from app.utils.product_text_parser import extract_recommended_products
from scenarios.scenario_loader import load_agent_instructions, policies_dir


class NativeEcommerceComponents(unittest.TestCase):
    def test_native_python_syntax(self):
        files = list((REPO / "chat-app/backend/app").rglob("*.py"))
        files += list((REPO / "scenario-app/backend/app").rglob("*.py"))
        for path in files:
            with self.subTest(path=str(path.relative_to(REPO))):
                ast.parse(path.read_text(encoding="utf-8-sig"))

    def test_catalog_contains_real_identifiers(self):
        catalog = ecommerce_catalog_by_title()
        self.assertEqual(len(catalog), 16)
        self.assertEqual(catalog["snow veil"]["id"], "CP-0001")
        self.assertEqual(catalog["snow veil"]["price"], 59.5)

    def test_known_card_maps_to_catalog_identifier(self):
        cards = extract_recommended_products("1. **Snow Veil**\n**Price:** $59.50\n**Rating:** 4.5")
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["id"], "CP-0001")

    def test_unknown_card_not_fabricated(self):
        cards = extract_recommended_products(
            "1. **PTU-NONEXISTENT-SKU-999**\n**Price:** $999.00\n**Rating:** 4.5"
        )
        self.assertEqual(cards, [], "Unknown titles must not become purchasable in-stock product cards")

    def test_mixed_cards_keep_only_catalog_products(self):
        cards = extract_recommended_products(
            "1. **Snow Veil**\n**Price:** $59.50\n**Rating:** 4.5\n"
            "2. **PTU-NONEXISTENT-SKU-999**\n**Price:** $999.00\n**Rating:** 4.5"
        )
        self.assertEqual([card["id"] for card in cards], ["CP-0001"])

    def test_policy_plain_text_not_product_card(self):
        self.assertEqual(extract_recommended_products("Returns are accepted within 30 days."), [])

    def test_policy_seed_expectations(self):
        root = policies_dir("ecommerce")
        returns = (root / "ReturnPolicy.txt").read_text(encoding="utf-8")
        warranty = (root / "Warranty.txt").read_text(encoding="utf-8")
        for expected in ("30 days", "original containers", "Custom-tinted paints are final sale"):
            self.assertIn(expected, returns)
        self.assertIn("2-year performance warranty", warranty)

    def test_native_specialist_configuration(self):
        self.assertEqual(catalog_tool_name(), "product_agent")
        self.assertEqual(policy_tool_name(), "policy_agent")
        instructions = load_agent_instructions("ecommerce", "chat_agent")
        self.assertIn("product_agent", instructions)
        self.assertIn("policy_agent", instructions)
        self.assertIn("returns", welcome_config()["subtitle"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
