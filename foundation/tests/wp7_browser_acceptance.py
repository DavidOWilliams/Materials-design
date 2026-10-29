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
        expect(page.get_by_text("D1 — guided material-system design")).to_be_visible()
        page.get_by_label("D1 workspace").fill(str(workspace))
        page.get_by_label("D1 workspace").press("Enter")
        expect(page.get_by_label("D1 workspace")).to_have_value(str(workspace))
        page.wait_for_timeout(2000)  # Streamlit text-input commit triggers a full app rerender
        print("Browser tab labels:", page.get_by_role("tab").all_text_contents(), flush=True)
        page.screenshot(path=str(workspace / "wp7-initial-browser.png"), full_page=True)
        # The first tab is selected by default; do not depend on a brittle label lookup.
        page.get_by_role("button", name="Generate, evaluate and save dossier").click()
        path = workspace / "d1-example.json"
        page.wait_for_timeout(3000)
        print("After execution, actual file exists:", path.exists(), flush=True)
        print("Visible page content after execution:", page.locator("body").inner_text()[-6500:], flush=True)
        page.screenshot(path=str(workspace / "wp7-after-execution.png"), full_page=True)
        expect(page.get_by_text("Saved", exact=False)).to_be_visible(timeout=15000)
        assert path.exists()
        assert inspect(path)["measured_evidence"] is None
        page.get_by_role("tab").nth(2).click()
        page.get_by_role("button", name="Inspect dossier and Pareto").click()
        expect(page.get_by_text("Inspect candidate ID")).to_be_visible(timeout=120000)
        page.get_by_role("tab").nth(3).click()
        page.get_by_role("button", name="Verify integrity and recompute").click()
        assert replay(path)["status"] == "passed"
        page.screenshot(path=str(workspace / "wp7-browser.png"), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
