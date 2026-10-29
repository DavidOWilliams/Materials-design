"""Real browser acceptance for reviewer findings WP7-IR01 and WP7-IR04.

Runs against localhost:8509 and a fresh WP7_IR_BROWSER_WORKSPACE.
Captures actual rendered browser screenshots and preserves original dossiers.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from material_core.wp7_handoff import verify_handoff
from material_core.wp5_service import replay


def main():
    root = Path(os.environ["WP7_IR_BROWSER_WORKSPACE"])
    root.mkdir(parents=True, exist_ok=False)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width":1600,"height":1000})
        page.goto(os.environ.get("D1_BROWSER_BASE_URL", "http://127.0.0.1:8509"), wait_until="networkidle", timeout=120000)
        expect(page.get_by_text("D1 — guided material-system design")).to_be_visible()
        workspace = page.get_by_label("D1 workspace")
        workspace.fill(str(root))
        workspace.press("Enter")
        page.wait_for_timeout(1500)
        page.get_by_role("tab").nth(1).click()
        page.get_by_role("button", name="Generate three architecture classes and persist WP3 campaign").click()
        expect(page.get_by_text("Saved", exact=False)).to_be_visible(timeout=120000)
        page.get_by_role("button", name="Inspect WP3 search and numerical Pareto").click()
        expect(page.get_by_label("Inspect candidate ID")).to_be_visible(timeout=120000)
        candidate = page.get_by_label("Select WP3 candidate")
        candidate.click()
        page.keyboard.press("Home")
        for _ in range(3):
            page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        page.get_by_role("button", name="Select WP3 candidate for WP4 handoff").click()
        expect(page.get_by_text("Compatible completed A/B gradient selected", exact=False)).to_be_visible(timeout=60000)
        page.get_by_role("tab").nth(2).click()
        expect(page.get_by_text("Selected WP3 candidate → fresh WP4 manufacturing feedback")).to_be_visible()
        page.get_by_role("button", name="Evaluate selected design through WP4 and save").click()
        expect(page.get_by_text("WP3 lineage verified", exact=False)).to_be_visible(timeout=120000)
        dossier = root / "selected-wp4.json"
        assert dossier.exists()
        assert verify_handoff(dossier)["verified"]
        assert replay(dossier)["status"] == "passed"
        page.screenshot(path=str(root / "wp7-ir01-browser.png"), full_page=True)
        page.get_by_role("button", name="Start checkpointed selected-design campaign and cancel").click()
        # Nonbinding 31 kg/m² cases may stop naturally before an explicit
        # cancellation, but the journal must remain inspectable and recoverable.
        expect(page.get_by_text("selected-wp4-journal.jsonl", exact=False)).to_be_visible(timeout=120000)
        page.get_by_role("button", name="Inspect cancellation checkpoints").click()
        page.get_by_role("button", name="Recover selected-design journal into immutable dossier").click()
        expect(page.get_by_text("Recovered original selected design", exact=False)).to_be_visible(timeout=120000)
        recovered = root / "selected-wp4-recovered.json"
        assert recovered.exists()
        assert verify_handoff(recovered)["verified"]
        assert replay(recovered)["status"] == "passed"
        page.screenshot(path=str(root / "wp7-ir04-browser.png"), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
