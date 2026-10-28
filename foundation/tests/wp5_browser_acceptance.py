"""Real Chromium browser acceptance against a live Streamlit process.

The test clicks the deployed UI and inspects the actual persisted WP4 dossier.
No numerical service is mocked.
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright, expect
from material_core.wp5_service import inspect, replay


def main():
    workspace = Path(os.environ["WP5_BROWSER_WORKSPACE"])
    workspace.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8501", wait_until="networkidle", timeout=120000)
        expect(page.get_by_text("Materials design — bounded WP5 demonstration")).to_be_visible()
        page.get_by_label("Workspace directory").fill(str(workspace))
        page.get_by_role("tab", name="Campaign").click()
        page.get_by_label("Maximum evaluations").fill("1")
        page.get_by_label("Process scenario version").fill("2")
        page.get_by_role("button", name="Execute and persist campaign").click()
        dossier = workspace / "campaign.json"
        expect(page.get_by_text("Saved:", exact=False)).to_be_visible(timeout=120000)
        assert dossier.exists()
        assert inspect(dossier)["records"]
        from material_core.wp4_feedback import reopen
        assert reopen(dossier)["process"]["version"] == 2
        page.get_by_role("tab", name="Inspect / compare").click()
        page.get_by_role("button", name="Inspect verified dossier").click()
        page.get_by_role("tab", name="Replay / export").click()
        page.get_by_role("button", name="Recompute numerical evidence").click()
        assert replay(dossier)["status"] == "passed"
        page.screenshot(path=str(workspace / "wp5-browser-acceptance.png"), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
