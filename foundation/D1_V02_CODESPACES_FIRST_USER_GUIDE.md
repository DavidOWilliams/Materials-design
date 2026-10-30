# D1 v0.2 — Codespaces launch and first-time demonstration

**Scope:** Synthetic demonstration, not a real material qualification tool. This guide applies to the **development** branch `d1-v0.2-guided-ui`. Do not use it for certified engineering designs.

## Open Codespaces on Windows with Microsoft Edge

1. Open [DavidOWilliams/Materials-design](https://github.com/DavidOWilliams/Materials-design) in Edge.
2. Choose **Code → Codespaces**, open your existing Codespace (or create one).
3. In the Codespaces terminal, copy each command as shown:

```bash
git status --short
git fetch origin
git switch d1-v0.2-guided-ui
git pull --ff-only origin d1-v0.2-guided-ui
python3 --version
command -v python3.12 || true
```

The final two commands show which Python is selected and whether Python **3.12** is available. D1 requires Python 3.12. Do **not** replace system `python3` or change the default Python interpreter.

If the terminal only shows Python 3.11, first check whether `python3.12` is available. If missing and the Codespace uses Ubuntu with `apt` packages, try:

```bash
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv
python3.12 --version
```

If `apt` cannot find Python 3.12, use the Codespaces **Change dev container configuration** option to select a Microsoft Python 3.12 image or recreate a Codespace based on a Python 3.12 devcontainer. Do not force system-wide Python replacements. The installed runtime and its package availability depend on the Codespace image.

## First-time environment setup

From the repository root:

```bash
PYTHON=python3.12 bash foundation/setup.sh
.venv-foundation/bin/python -m pip install streamlit==1.40.2
.venv-foundation/bin/python -m pip check
.venv-foundation/bin/python --version
```

`foundation/setup.sh` intentionally refuses to overwrite an existing virtual environment. If `.venv-foundation` already exists and reports Python 3.12, **reuse** it:

```bash
.venv-foundation/bin/python --version
.venv-foundation/bin/python -m pip install streamlit==1.40.2
.venv-foundation/bin/python -m pip check
```

If the existing virtual environment uses a different Python version, preserve it by renaming it before creating a new one: `mv .venv-foundation .venv-foundation-old`. Do not delete an environment containing evidence you need.

## Launch and reach the browser

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m streamlit run foundation/wp7_app.py --server.address 0.0.0.0 --server.port 8501
```

In the **Ports** panel, find port **8501**, choose **Open in Browser**, or click its forwarded link. The app can also be opened in a Microsoft Edge browser tab. If 8501 is in use, stop the old Streamlit process with **Ctrl+C** in its terminal, or explicitly start on another unused port (`--server.port 8502`) and open that port instead.

To stop D1, select its running terminal and press **Ctrl+C**. Existing dossiers are unchanged. To restart, run the same Streamlit launch command. You do not need to reinstall dependencies for each session.

## First user journey

1. **Tab 1: Run demonstration.** Read the synthetic evidence limitation and inspect objective/constraint data. Select **Representative mass-constrained coupon**. Change the filename if needed; this is an immutable evidence name, not an overwrite target.
2. If `d1-example.json` already exists, the app shows a warning and disables the new-run button. Select **Inspect existing dossier** to verify it, or **Use suggested unused filename**, then **Generate, evaluate and save dossier**.
3. **Tab 2: Explore architectures.** Choose a new WP3 campaign directory and generate homogeneous, layered and gradient alternatives. If `mixed-architecture` exists, open its saved `campaign.json` or use the unused-directory suggestion. The WP3 scatter comparison is **intended state** only. Select a candidate to inspect structure, exact constituent fractions and numerical qualification.
4. If the chosen WP3 candidate is a **numerically qualified, supported A/B gradient**, choose it for WP4 handoff. Unsupported architectures and unqualified candidates must be rejected.
5. **Tab 3: Manufacturing and trade-offs.** Create a separate WP4 dossier at an unused destination; inspect synthetic estimated-achieved results, potential feedback and **WP4-only** Pareto. C1 profile overlays and C3 deviations appear only for source-supported compatible representations. The graph is not measured evidence.
6. To inspect cancellation/recovery, choose unused checkpoint journal and recovery output paths. Keep all original files and handoff companions. A naturally terminated campaign must never be described as forcibly cancelled.
7. **Tab 4: Restore and replay.** Recompute numerical evidence from the original dossier, export its verified JSON, import to a **new** filename and replay the restored file. To preserve WP3 evidence, export its complete verified ZIP and restore into a new directory.
8. After restarting Streamlit, reopen an existing WP3 ledger and WP4 dossier by their paths. The application's session selection may reset after a new browser session; files remain intact.

## Evidence and scientific boundary

All D1 materials are hypothetical; synthesis of real-world ceramic recipes or experimentally achieved states is not established. WP3 intended-state numerical qualification does **not** establish manufacturability. WP4's mapped geometry is a **synthetic estimate**. Where composition data is missing, the UI must indicate that no comparison is available rather than inventing profile points. Results remain traceable to exact candidate IDs, source tables and provenance in the expandable sections.

## Verifying the development branch

The dedicated GitHub Actions job `D1 v0.2 UI and scientific challenge verification` runs accepted tests, Python 3.12, real Chromium interactions, and uploads evidence hashes. Check the run's commit SHA and overall conclusion before using evidence. Earlier green runs against different SHAs are not sufficient. Do not merge or release without independent review.
