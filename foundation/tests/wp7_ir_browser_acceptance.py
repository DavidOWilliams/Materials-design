"""Real browser acceptance for reviewer findings WP7-IR01 and WP7-IR04.

Runs against localhost:8509 and a fresh WP7_IR_BROWSER_WORKSPACE.
Captures actual rendered browser screenshots and preserves original dossiers.
"""
import json
import hashlib
import os
import subprocess
import sys
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
        candidate = page.get_by_label("Inspect candidate ID")
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
        journal = root / "selected-wp4-journal.jsonl"
        for _ in range(240):
            if journal.exists():
                break
            page.wait_for_timeout(500)
        assert journal.exists(), "Checkpoint journal not persisted after browser wait"
        page.get_by_role("button", name="Inspect cancellation checkpoints").click()
        original_sha = hashlib.sha256(dossier.read_bytes()).hexdigest()
        journal_sha = hashlib.sha256(journal.read_bytes()).hexdigest()
        ledger_sha = hashlib.sha256((root/"mixed-architecture"/"campaign.json").read_bytes()).hexdigest()
        page.get_by_role("button", name="Recover selected-design journal into immutable dossier").click()
        recovery_notice = page.get_by_text("Recovered original selected design and verified source lineage", exact=False)
        try:
            expect(recovery_notice).to_be_visible(timeout=120000)
        except AssertionError:
            page.screenshot(path=str(root/"wp7-ir04-recovery-visible-failure.png"), full_page=True)
            print("Recovery UI DOM after failed confirmation:\\n" + page.locator("body").inner_text()[-8000:], flush=True)
            raise
        recovered = root / "selected-wp4-recovered.json"
        assert recovered.exists()
        assert verify_handoff(recovered)["verified"]
        assert (root / "selected-wp4-recovered.json.handoff.json").exists()
        assert replay(recovered)["status"] == "passed"
        # Reopen and numerically replay in a new Python process, not shared memory.
        proc = subprocess.run([sys.executable, "-c",
            "import sys; from material_core.wp7_handoff import verify_handoff; from material_core.wp5_service import replay; "
            "assert verify_handoff(sys.argv[1])['verified']; assert replay(sys.argv[1])['status']=='passed'; print('separate-process verified')",
            str(recovered)], check=True, text=True, capture_output=True)
        assert "separate-process verified" in proc.stdout
        assert hashlib.sha256(dossier.read_bytes()).hexdigest() == original_sha
        assert hashlib.sha256(journal.read_bytes()).hexdigest() == journal_sha
        assert hashlib.sha256((root/"mixed-architecture"/"campaign.json").read_bytes()).hexdigest() == ledger_sha
        # An unrelated Streamlit rerun must not erase the successful recovery feedback.
        page.get_by_role("button", name="Inspect cancellation checkpoints").click()
        expect(recovery_notice).to_be_visible(timeout=120000)
        page.screenshot(path=str(root / "wp7-ir04-browser.png"), full_page=True)
        # A new browser context has no WP3 selection: reopen the saved dossier directly.
        fresh = browser.new_context(viewport={"width":1400,"height":850})
        reopened = fresh.new_page()
        reopened.goto(os.environ.get("D1_BROWSER_BASE_URL", "http://127.0.0.1:8509"),
                      wait_until="networkidle", timeout=120000)
        reopened.get_by_label("D1 workspace").fill(str(root))
        reopened.get_by_label("D1 workspace").press("Enter")
        reopened.get_by_role("tab").nth(2).click()
        reopened.get_by_label("Verified dossier to inspect").fill(str(recovered))
        reopened.get_by_label("Verified dossier to inspect").press("Enter")
        reopened.get_by_role("button", name="Inspect dossier and Pareto").click()
        expect(reopened.get_by_text("WP4 synthetic estimated-achieved state", exact=False)).to_be_visible(timeout=120000)
        reopened.screenshot(path=str(root/"wp7-ir04-reopened-new-session.png"), full_page=True)
        fresh.close()
        browser.close()


if __name__ == "__main__":
    main()
