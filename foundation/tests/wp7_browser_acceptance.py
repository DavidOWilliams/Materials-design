"""WP7 real Chromium acceptance against running Streamlit; no mocked services.

Run with WP7_BROWSER_WORKSPACE set to a new directory and server on 8509.
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright, expect
from material_core.wp5_service import inspect, replay


def main():
    workspace = Path(os.environ["WP7_BROWSER_WORKSPACE"])
    workspace.mkdir(parents=True, exist_ok=False)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1500, "height": 950})
        page.goto("http://127.0.0.1:8509", wait_until="networkidle", timeout=120000)
        expect(page.get_by_text("D1 — synthetic ceramic gradient design")).to_be_visible()
        page.get_by_label("D1 workspace").fill(str(workspace))
        page.get_by_role("tab", name="1. Run demonstration").click()
        page.get_by_role("button", name="Generate, evaluate and save dossier").click()
        path = workspace / "d1-example.json"
        expect(page.get_by_text("Persisted", exact=False)).to_be_visible(timeout=120000)
        assert path.exists()
        assert inspect(path)["measured_evidence"] is None
        page.get_by_role("tab", name="3. Inspect feedback and trade-offs").click()
        page.get_by_role("button", name="Inspect dossier and Pareto").click()
        expect(page.get_by_text("Select saved candidate")).to_be_visible(timeout=120000)
        page.get_by_role("tab", name="4. Restore and replay").click()
        page.get_by_role("button", name="Verify integrity and recompute").click()
        assert replay(path)["status"] == "passed"
        page.screenshot(path=str(workspace / "wp7-browser.png"), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
