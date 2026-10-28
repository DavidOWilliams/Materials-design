"""Independent Playwright WP7 mixed-architecture ZIP download/restore and application restart."""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from material_core.wp7_search_dossier import mixed_summary
from material_core.wp3_search import recompute_search

PORT=8519
def start_server(log):
    proc=subprocess.Popen([sys.executable,"-m","streamlit","run","foundation/wp7_app.py",
       f"--server.port={PORT}","--server.headless=true","--browser.gatherUsageStats=false"],
       stdout=log,stderr=subprocess.STDOUT,env={**os.environ,"PYTHONPATH":str(Path("foundation").resolve())})
    for i in range(100):
        if proc.poll() is not None:raise RuntimeError("Streamlit exited "+str(proc.returncode))
        try:
            with urllib.request.urlopen(f"http://localhost:{PORT}/_stcore/health",timeout=2) as h:
                if h.status==200:return proc
        except Exception:pass
        time.sleep(.3)
    raise TimeoutError("Streamlit failed health check")
def stop_server(p):
    if p is None:return
    p.terminate()
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        p.kill();p.wait(timeout=5)
def main():
    root=Path(os.environ.get("WP7_REVIEW_BROWSER_ROOT","/tmp/wp7-review-browser"))
    root.mkdir(parents=True,exist_ok=False)
    workspace=root/"workspace";workspace.mkdir()
    restore=root/"restored"
    log=open(root/"streamlit-server.log","w")
    proc=None
    try:
        proc=start_server(log)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={"width":1400,"height":900},accept_downloads=True)
            page.goto(f"http://localhost:{PORT}",wait_until="networkidle",timeout=120000)
            expect(page.get_by_text("D1 — synthetic ceramic gradient design")).to_be_visible()
            page.get_by_label("D1 workspace").fill(str(workspace))
            page.get_by_label("D1 workspace").press("Enter")
            page.get_by_role("tab").nth(1).click()
            page.get_by_role("button",name="Generate three architecture classes and persist WP3 campaign").click()
            expect(page.get_by_text("Saved",exact=False)).to_be_visible(timeout=120000)
            ledger=workspace/"mixed-architecture"/"campaign.json"
            assert ledger.exists(),"WP3 browser generated no persistent ledger"
            page.get_by_role("button",name="Inspect WP3 search and numerical Pareto").click()
            expect(page.get_by_text("Select WP3 candidate")).to_be_visible(timeout=120000)
            assert len(mixed_summary(ledger)["rows"])>=4
            page.screenshot(path=str(root/"mixed-browser.png"),full_page=True)
            with page.expect_download(timeout=120000) as request:
                page.get_by_role("button",name="Download full verified WP3 dossier ZIP").click()
            download=request.value
            saved=root/"browser-export.zip"
            download.save_as(str(saved))
            assert saved.stat().st_size>10000
            upload=page.locator("input[type=file]")
            assert upload.count()>=1
            upload.first.set_input_files(str(saved))
            page.get_by_label("New WP3 destination directory").fill(str(restore))
            page.get_by_label("New WP3 destination directory").press("Enter")
            page.get_by_role("button",name="Verify and restore WP3 ZIP").click()
            expect(page.get_by_text("passed",exact=False)).to_be_visible(timeout=120000)
            assert (restore/"campaign.json").exists(),"ZIP UI did not restore WP3 ledger"
            assert recompute_search(restore/"campaign.json")["replay"]=="passed"
            page.screenshot(path=str(root/"restored-browser.png"),full_page=True)
            browser.close()
        stop_server(proc);proc=None
        proc=start_server(log)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={"width":1400,"height":900})
            page.goto(f"http://localhost:{PORT}",wait_until="networkidle",timeout=120000)
            page.get_by_role("tab").nth(1).click()
            page.get_by_label("WP3 ledger path").fill(str(restore/"campaign.json"))
            page.get_by_label("WP3 ledger path").press("Enter")
            page.get_by_role("button",name="Inspect WP3 search and numerical Pareto").click()
            expect(page.get_by_text("Select WP3 candidate")).to_be_visible(timeout=120000)
            assert len(mixed_summary(restore/"campaign.json")["rows"])>=4
            page.screenshot(path=str(root/"restart-browser.png"),full_page=True)
            browser.close()
        output={"status":"passed","browser_download_bytes":saved.stat().st_size,
               "architectures":sorted({v["architecture"] for v in mixed_summary(restore/"campaign.json")["rows"]}),
               "restore_replay":"passed","restart_verified":True}
        (root/"result.json").write_text(json.dumps(output,indent=2)+"\n")
        print("REVIEW_BROWSER_PASS",json.dumps(output),flush=True)
    finally:
        stop_server(proc);log.close()
if __name__=="__main__":main()
