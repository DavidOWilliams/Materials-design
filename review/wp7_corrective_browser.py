"""Independent reviewer real Chromium WP7 IR01/IR04 corrected UI journey."""
import json,os,subprocess,sys,time,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from material_core.wp7_handoff import verify_handoff
from material_core.wp5_service import replay
from material_core.wp3_search import open_search
PORT=8527
def start(f):
 p=subprocess.Popen([sys.executable,"-m","streamlit","run","foundation/wp7_app.py",
  f"--server.port={PORT}","--server.headless=true","--browser.gatherUsageStats=false"],
  stdout=f,stderr=subprocess.STDOUT,env={**os.environ,"PYTHONPATH":str(Path("foundation").resolve())})
 for _ in range(120):
  if p.poll() is not None:raise RuntimeError("server exited "+str(p.returncode))
  try:
   with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/_stcore/health",timeout=2) as r:
    if r.status==200:return p
  except Exception:pass
  time.sleep(.4)
 raise TimeoutError("Streamlit health never passed")
def stop(p):
 if p is None:return
 p.terminate()
 try:p.wait(timeout=8)
 except subprocess.TimeoutExpired:p.kill();p.wait()
def main():
 out=Path("/tmp/wp7-review/ui");out.mkdir(parents=True,exist_ok=False)
 workspace=out/"workspace"; workspace.mkdir()
 f=open(out/"streamlit.log","w");p=None
 try:
  p=start(f)
  with sync_playwright() as pl:
   browser=pl.chromium.launch(headless=True)
   page=browser.new_page(viewport={"width":1500,"height":950})
   page.goto(f"http://127.0.0.1:{PORT}",wait_until="networkidle",timeout=120000)
   expect(page.get_by_text("D1 — synthetic ceramic material-system design")).to_be_visible()
   page.get_by_label("D1 workspace").fill(str(workspace))
   page.get_by_label("D1 workspace").press("Enter")
   page.get_by_role("tab").nth(1).click()
   page.get_by_role("button",name="Generate three architecture classes and persist WP3 campaign").click()
   expect(page.get_by_text("Saved",exact=False)).to_be_visible(timeout=120000)
   page.get_by_role("button",name="Inspect WP3 search and numerical Pareto").click()
   select=page.get_by_label("Select WP3 candidate")
   expect(select).to_be_visible()
   select.click()
   page.keyboard.press("Home")
   for _ in range(3):page.keyboard.press("ArrowDown")
   page.keyboard.press("Enter")
   page.wait_for_timeout(500)
   page.get_by_role("button",name="Select WP3 candidate for WP4 handoff").click()
   expect(page.get_by_text("Compatible completed A/B gradient selected",exact=False)).to_be_visible(timeout=120000)
   page.get_by_role("tab").nth(2).click()
   page.get_by_role("button",name="Evaluate selected design through WP4 and save").click()
   expect(page.get_by_text("WP3 lineage verified",exact=False)).to_be_visible(timeout=120000)
   dossier=workspace/"selected-wp4.json"
   assert dossier.exists() and verify_handoff(dossier)["verified"]
   assert replay(dossier)["status"]=="passed"
   page.get_by_role("button",name="Start checkpointed selected-design campaign and cancel").click()
   expect(page.get_by_text("selected-wp4-journal.jsonl",exact=False)).to_be_visible(timeout=120000)
   page.get_by_role("button",name="Inspect cancellation checkpoints").click()
   page.get_by_role("button",name="Recover selected-design journal into immutable dossier").click()
   expect(page.get_by_text("Recovered original selected design",exact=False)).to_be_visible(timeout=120000)
   recovered=workspace/"selected-wp4-recovered.json"
   assert recovered.exists() and verify_handoff(recovered)["verified"]
   assert replay(recovered)["status"]=="passed"
   page.screenshot(path=str(out/"handoff-recovered.png"),full_page=True)
   browser.close()
  stop(p);p=None
  p=start(f)
  with sync_playwright() as pl:
   browser=pl.chromium.launch(headless=True)
   page=browser.new_page(viewport={"width":1500,"height":950})
   page.goto(f"http://127.0.0.1:{PORT}",wait_until="networkidle",timeout=120000)
   page.get_by_role("tab").nth(2).click()
   page.get_by_label("Verified dossier to inspect").fill(str(recovered))
   page.get_by_label("Verified dossier to inspect").press("Enter")
   page.get_by_role("button",name="Inspect dossier and Pareto").click()
   expect(page.get_by_text("Select saved candidate")).to_be_visible(timeout=120000)
   page.screenshot(path=str(out/"restarted-recovered.png"),full_page=True)
   browser.close()
  summary={"browser":"pass","handoff":"verified","recovered":"verified","restart":"pass","replay":"pass","source_architectures":sorted({p["proposal"]["architecture"] for p in open_search(workspace/"mixed-architecture"/"campaign.json")["proposals"]})}
  (out/"review-result.json").write_text(json.dumps(summary,indent=2))
  print("INDEPENDENT_BROWSER_PASS",json.dumps(summary),flush=True)
 finally:stop(p);f.close()
if __name__=="__main__":main()
