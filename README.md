# DeadlockGuard — OS IA Activity 2

## Run
1. Install Python 3.10 or later.
2. Open Terminal in this folder.
3. Run: `python -m venv .venv`
4. Activate it:
   - macOS/Linux: `source .venv/bin/activate`
   - Windows: `.venv\\Scripts\\activate`
5. Run: `pip install -r requirements.txt`
6. Run: `streamlit run app.py`

## Test algorithms
Run `pytest -q` from this folder. The included tests validate the default safe sequence,
a waiting request, an unsafe request denial, and a single-instance cycle detector.

## Important submission checklist
- Add all group members' names, roll numbers and contributions.
- Run the dashboard on your own machine.
- Capture screenshots of TC1–TC6 from actual dashboard execution.
- Confirm the results and replace any illustrative/expected wording with observed results.
- Every member must understand Need = Maximum - Allocation, Work updates, safe sequence,
  request validation, and why unsafe does not mean deadlocked.
- Mention the actual tools and verification performed. Do not claim tests/screenshots you did not perform.

## Default safe-state dataset
Allocation = [[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
Maximum    = [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
Available  = [3,3,2]
Expected safe sequence = P1 -> P3 -> P0 -> P2 -> P4

## Required demo order (six minutes)
1. 0:00–0:40 — dashboard and system assumptions
2. 0:40–2:00 — Need matrix, Work trace and safe sequence
3. 2:00–2:50 — valid request exceeding Available: WAITING
4. 2:50–3:40 — request that creates unsafe state: DENIED and restored
5. 3:40–4:40 — single-instance deadlock cycle and recovery
6. 4:40–5:30 — prevention by resource ordering
7. 5:30–6:00 — boundary handling and conclusion
