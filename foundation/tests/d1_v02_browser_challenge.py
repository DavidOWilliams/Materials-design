"""D1 v0.2 first-user Playwright smoke and immutable-collision verification.

Requires live Streamlit localhost:8512 and D1_V02_BROWSER_WORKSPACE.
Saves real Chromium screenshots and a machine-readable result.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from material_core.wp5_service import replay, inspect

def main():
    root=Path(os.environ["D1_V02_BROWSER_WORKSPACE"])
    root.mkdir(parents=True,exist_ok=False)
    findings=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={"width":1500,"height":950})
        page.goto("http://127.0.0.1:8512",wait_until="networkidle",timeout=120000)
        expect(page.get_by_text("D1 — guided material-system design")).to_be_visible()
        page.get_by_label("D1 workspace").fill(str(root))
        page.get_by_label("D1 workspace").press("Enter")
        expect(page.get_by_text("Engineering duty:", exact=False)).to_be_visible()
        page.screenshot(path=str(root/"01-challenge.png"),full_page=True)
        # Existing dossier: immutability protected before execution.
        (root/"d1-example.json").write_text("preserved-existing-evidence")
        page.reload(wait_until="networkidle")
        page.get_by_label("D1 workspace").fill(str(root))
        page.get_by_label("D1 workspace").press("Enter")
        expect(page.get_by_text("This dossier already exists",exact=False)).to_be_visible()
        expect(page.get_by_role("button",name="Generate, evaluate and save dossier")).to_be_disabled()
        page.screenshot(path=str(root/"02-collision.png"),full_page=True)
        page.get_by_role("button",name="Use suggested unused filename").click()
        expect(page.get_by_label("New D1 dossier filename")).to_have_value("d1-example-run-001.json")
        page.get_by_role("button",name="Create new run and save immutable dossier").click()
        expect(page.get_by_text("Saved",exact=False)).to_be_visible(timeout=120000)
        assert (root/"d1-example.json").read_text()=="preserved-existing-evidence"
        assert replay(root/"d1-example-run-001.json")["status"]=="passed"
        findings.append("immutable collision protected, unused name executed, replay passed")
        page.screenshot(path=str(root/"03-new-dossier.png"),full_page=True)
        page.get_by_role("tab").nth(2).click()
        page.get_by_role("button",name="Inspect dossier and Pareto").click()
        expect(page.get_by_text("WP4 synthetic estimated-achieved state",exact=False)).to_be_visible(timeout=30000)
        page.screenshot(path=str(root/"04-wp4-analysis.png"),full_page=True)
        page.get_by_role("tab").nth(1).click()
        # Lower mesh for browser smoke; scientific 4096 demo is run separately in CI.
        page.get_by_role("button",name="Generate three architecture classes and persist WP3 campaign").click()
        expect(page.get_by_text("Saved",exact=False)).to_be_visible(timeout=120000)
        page.get_by_role("button",name="Inspect WP3 search and numerical Pareto").click()
        expect(page.get_by_text("WP3 intended-state only",exact=False)).to_be_visible(timeout=60000)
        page.screenshot(path=str(root/"05-wp3-analysis.png"),full_page=True)
        # Repeated run shows an actionable collision, never overwrites.
        expect(page.get_by_text("campaign directory already exists",exact=False)).to_be_visible()
        assert (root/"mixed-architecture"/"campaign.json").exists()
        findings.append("WP3 immutable campaign and separate intended-state chart")
        page.get_by_role("tab").nth(3).click()
        page.get_by_label("Source dossier").fill(str(root/"d1-example-run-001.json"))
        page.get_by_label("Source dossier").press("Enter")
        page.get_by_role("button",name="Verify integrity and recompute").click()
        expect(page.get_by_text("Existing dossier independently recomputed",exact=False)).to_be_visible(timeout=120000)
        page.get_by_label("Immutable import destination").fill(str(root/"restored.json"))
        page.get_by_label("Immutable import destination").press("Enter")
        page.get_by_role("button",name="Restore copied dossier").click()
        expect(page.get_by_text("Imported",exact=False)).to_be_visible(timeout=120000)
        assert replay(root/"restored.json")["status"]=="passed"
        page.get_by_role("button",name="Replay restored dossier").click()
        expect(page.get_by_text("passed",exact=False).first).to_be_visible(timeout=120000)
        page.screenshot(path=str(root/"06-replay-controls.png"),full_page=True)
        findings.append("Tab 4 immutable import, replay and separate source preserved")
        narrow=browser.new_page(viewport={"width":790,"height":900})
        narrow.goto("http://127.0.0.1:8512",wait_until="networkidle",timeout=120000)
        expect(narrow.get_by_text("D1 — guided material-system design")).to_be_visible()
        narrow.screenshot(path=str(root/"07-narrow-screen.png"),full_page=True)
        browser.close()
    (root/"browser-verification.json").write_text(json.dumps({"status":"passed","checks":findings},indent=2))
    print(json.dumps({"status":"passed","checks":findings}))

if __name__=="__main__":
    main()
