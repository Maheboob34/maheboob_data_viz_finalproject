# Hospital Quality & Readmission Dashboard

Streamlit companion to the *Hospital Quality and Readmission Analysis* notebook (CMS Care
Compare data: Hospital General Information, HCAHPS, Hospital Readmissions Reduction Program).

## Files
- `app.py` — the dashboard
- `data.json` — curated data extracted directly from the notebook's own published figures (every value matches the notebook's research-question findings)
- `requirements.txt` — dependencies

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud (required for submission)
1. Create a **new public GitHub repository** for this project (not your classwork repo).
2. Add `app.py`, `data.json`, `requirements.txt` (and your notebook + PDF export) to the repo and push.
3. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, click **New app**.
4. Pick your repo/branch, set the main file path to `app.py`, and click **Deploy**.
5. Copy the live app URL — you'll need it for the presentation and the submission checklist.

## What's inside
A single curated, filterable page (not all 10 research questions — a thoughtful subset per the
assignment brief):
1. CMS rating vs. excess readmission ratio (state + rating filters)
2. State-level patient experience vs. readmission performance (highlightable)
3. Readmission ratio by hospital ownership
4. Patient experience by emergency-service availability
5. Top 10 hospitals by composite quality score
6. Regression drivers of excess readmission ratio

Palette is CVD-safe (muted grey for context, blue/orange for focus, RdBu/Blues for
diverging/sequential encodings) and consistent with the notebook's chart styling.
