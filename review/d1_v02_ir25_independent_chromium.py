"""Independently authored Chromium review of D1 v0.2 recovery, persistence, and stale success."""
import os,json,hashlib,subprocess,sys,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from material_core.wp7_handoff import verify_handoff,recover_checkpointed_handoff
from material_core.wp5_service import replay

ROOT=Path("/tmp/d1-ir-browser")
PORT=8536
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def reject(fn,kind):
 try:fn()
 except (ValueError,FileNotFoundError,KeyError,OSError,TypeError) as err:
  print("REVIEW_REJECTED",kind,type(err).__name__,str(err),flush=True)
  return
 raise AssertionError(kind+" accepted unexpectedly")
def server(log):
 p=subprocess.Popen([sys.executable,"-m","streamlit","run","foundation/wp7_app.py",f"--server.port={PORT}",
  "--server.headless=true","--browser.gatherUsageStats=false"],stdout=log,stderr=subprocess.STDOUT,
  env={**os.environ,"PYTHONPATH":str(Path("foundation").resolve())})
 for i in range(120):
  try:
   with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/_stcore/health",timeout=2) as response:
    if response.status==200:return p
  except Exception:pass
  if p.poll() is not None:raise RuntimeError("server exited "+str(p.returncode))
  time.sleep(.5)
 raise TimeoutError("no server health")
def stop(p):
 p.terminate()
 try:p.wait(timeout=10)
 except subprocess.TimeoutExpired:p.kill();p.wait()
def main():
 ROOT.mkdir(parents=True,exist_ok=False)
 log=open(ROOT/"server.log","w");proc=server(log)
 try:
  with sync_playwright() as pl:
   browser=pl.chromium.launch(headless=True)
   page=browser.new_page(viewport={"width":1500,"height":950})
   page.goto(f"http://127.0.0.1:{PORT}",wait_until="networkidle",timeout=120000)
   page.get_by_label("D1 workspace").fill(str(ROOT))
   page.get_by_label("D1 workspace").press("Enter")
   page.get_by_role("tab").nth(1).click()
   page.get_by_role("button",name="Generate three architecture classes and persist WP3 campaign").click()
   expect(page.get_by_text("Saved",exact=False)).to_be_visible(timeout=120000)
   page.get_by_role("button",name="Inspect WP3 search and numerical Pareto").click()
   sel=page.get_by_label("Inspect candidate ID")
   expect(sel).to_be_visible(timeout=120000)
   sel.click();page.keyboard.press("Home")
   for _ in range(3):page.keyboard.press("ArrowDown")
   page.keyboard.press("Enter")
   page.get_by_role("button",name="Select WP3 candidate for WP4 handoff").click()
   expect(page.get_by_text("Compatible completed A/B gradient selected",exact=False)).to_be_visible(timeout=60000)
   page.get_by_role("tab").nth(2).click()
   page.get_by_role("button",name="Evaluate selected design through WP4 and save").click()
   expect(page.get_by_text("WP3 lineage verified",exact=False)).to_be_visible(timeout=120000)
   dossier=ROOT/"selected-wp4.json"
   journal=ROOT/"selected-wp4-journal.jsonl"
   recovered=ROOT/"selected-wp4-recovered.json"
   assert dossier.exists() and verify_handoff(dossier)["verified"]
   page.get_by_role("button",name="Start checkpointed selected-design campaign and cancel").click()
   for _ in range(240):
    if journal.exists():break
    page.wait_for_timeout(500)
   assert journal.exists()
   page.get_by_role("button",name="Inspect cancellation checkpoints").click()
   originals={k:digest(k) for k in [dossier,journal,ROOT/"mixed-architecture"/"campaign.json"]}
   page.get_by_role("button",name="Recover selected-design journal into immutable dossier").click()
   success=page.get_by_text("Recovered original selected design and verified source lineage",exact=False)
   expect(success.first).to_be_visible(timeout=120000)
   assert recovered.exists()
   assert verify_handoff(recovered)["verified"] and replay(recovered)["status"]=="passed"
   assert all(digest(p)==h for p,h in originals.items())
   page.screenshot(path=str(ROOT/"01-confirmed-recovery.png"),full_page=True)
   page.get_by_role("button",name="Inspect cancellation checkpoints").click()
   expect(success.first).to_be_visible(timeout=60000)
   page.screenshot(path=str(ROOT/"02-after-rerender.png"),full_page=True)
   cmd="import sys;from material_core.wp7_handoff import verify_handoff;from material_core.wp5_service import replay;assert verify_handoff(sys.argv[1])['verified'];assert replay(sys.argv[1])['status']=='passed';print('separate-process-pass')"
   result=subprocess.run([sys.executable,"-c",cmd,str(recovered)],capture_output=True,text=True,check=True,env={**os.environ,"PYTHONPATH":str(Path("foundation").resolve())})
   assert "separate-process-pass" in result.stdout
   fresh=browser.new_context()
   new=fresh.new_page()
   new.goto(f"http://127.0.0.1:{PORT}",wait_until="networkidle",timeout=120000)
   new.get_by_role("tab").nth(2).click()
   new.get_by_label("Verified dossier to inspect").fill(str(recovered))
   new.get_by_label("Verified dossier to inspect").press("Enter")
   new.get_by_role("button",name="Inspect dossier and Pareto").click()
   expect(new.get_by_text("WP4 synthetic estimated-achieved state",exact=False)).to_be_visible(timeout=120000)
   new.screenshot(path=str(ROOT/"03-fresh-context.png"),full_page=True)
   fresh.close()
   print("REVIEW_PASS R2 R3 normal_browser_restore_rerender_fresh_session",json.dumps({"recovered":str(recovered),"dossier_sha256":digest(recovered),"handoff_sha256":digest(str(recovered)+".handoff.json"),"journal_sha256":digest(journal),"source_ledger_sha256":digest(ROOT/"mixed-architecture"/"campaign.json")}),flush=True)
   reject(lambda:recover_checkpointed_handoff(ROOT/"missing.journal.jsonl",ROOT/"new.json"),"missing_journal")
   reject(lambda:recover_checkpointed_handoff(journal,recovered),"existing_target")
   # Deliberately corrupt the companion AFTER successful browser verification.
   companion=Path(str(recovered)+".handoff.json")
   original=companion.read_bytes()
   data=json.loads(original);data["sha256"]="0"*64;companion.write_text(json.dumps(data))
   reject(lambda:verify_handoff(recovered),"tampered_companion")
   page.get_by_role("button",name="Inspect cancellation checkpoints").click()
   stale_visible=success.count()>0 and success.first.is_visible()
   page.screenshot(path=str(ROOT/"04-tampered-companion-rerender.png"),full_page=True)
   warning=page.get_by_text("Previously recovered dossier can no longer be verified",exact=False)
   expect(warning).to_be_visible(timeout=120000)
   expect(success).to_have_count(0,timeout=120000)
   stale_visible=success.count()>0
   assert not stale_visible,"Green verified-success improperly persisted after corrupted companion"
   print("REVIEW_PASS R2_T03 corrupted_companion_green_absent_warning_visible",json.dumps({"success_visible":stale_visible,"warning_visible":warning.is_visible(),"verify_handoff":"rejected"}),flush=True)
   companion.write_bytes(original)
   page.get_by_role("button",name="Inspect cancellation checkpoints").focus()
   page.get_by_role("button",name="Inspect cancellation checkpoints").press("Enter")
   assert not (success.count()>0 and success.first.is_visible()),"Old green success returned after restored companion without fresh confirmation"
   print("REVIEW_PASS R2_T04_T05 stale_status_does_not_return_after_repair",flush=True)
   assert verify_handoff(recovered)["verified"]
   browser.close()
 finally:
  stop(proc);log.close()
if __name__=="__main__":main()
