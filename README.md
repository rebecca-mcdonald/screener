# Hammer & Nails Echo Park – Candidate Fit Screener

A lightweight **Streamlit** app that screens candidates for the **Sales Associate / Member Concierge** role at **Hammer & Nails – Echo Park**.

It asks targeted questions across hospitality, sales drive, membership mindset, reliability, operations, attention to detail, tech comfort, communication, and availability; then produces a transparent scorecard and exportable JSON.

## Quickstart

```bash
# 1) Create & activate a virtual env (optional but recommended)
python3 -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run
streamlit run streamlit_app.py
```

The app runs on http://localhost:8501

## Deploy to Streamlit Cloud

1. Push this repo to GitHub.
2. On https://streamlit.io/cloud, click **New app** → select your repo/branch → app file `streamlit_app.py`.
3. Set **Python version** to 3.9+ and hit **Deploy**.

## Files

- `streamlit_app.py` — the Streamlit app
- `requirements.txt` — Python dependencies
- `questions.json` — the question bank (edit here to tune the screener)
- `LICENSE` — MIT
- `.gitignore`

## Notes

- **Knockouts:** Evenings, weekends, and baseline sales comfort are required. If unmet, the result is flagged for review.
- **Scoring:** Likert and SJT answers are normalized to a 0–100 scale and averaged with light dimensional weights.
- **Export:** You can download a JSON scorecard per candidate.
