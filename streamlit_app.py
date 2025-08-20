
import json
import time
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="H&N Echo Park – Candidate Fit Screener", page_icon="💈", layout="centered")

@st.cache_data
def load_questions():
    with open("questions.json", "r") as f:
        return json.load(f)

def normalize(val, min_v=1, max_v=5):
    v = min(max_v, max(min_v, val))
    return ((v - min_v) / (max_v - min_v)) * 100.0

def score_question(q, a):
    w = q.get("weight", 1)
    if w == 0:
        return 0.0
    kind = q["kind"]
    if kind == "likert":
        try:
            return normalize(float(a or 3)) * w
        except Exception:
            return normalize(3) * w
    if kind == "boolean":
        good = True
        val = 5 if a is True else 1 if a is False else 3
        return normalize(val) * w
    if kind == "select":
        opt = None
        for o in q.get("options", []):
            if o["value"] == a:
                opt = o
                break
        return normalize(opt.get("score", 3) if opt else 3) * w
    if kind == "sjt":
        sel = None
        for c in q.get("choices", []):
            if c["key"] == a:
                sel = c
                break
        return normalize(sel.get("score", 3) if sel else 3) * w
    if kind == "text":
        min_chars = q.get("minChars", 0)
        txt = (a or "").strip()
        if not txt:
            return 50.0 * w
        ratio = min(1.0, len(txt) / max(40, min_chars))
        return (60 + ratio * 40) * w
    return 0.0

def pretty_label(id_):
    return {
        "availability_evenings":"Can work evenings",
        "availability_weekends":"Can work weekends",
        "sales_comfort":"Comfort with initiating sales conversations"
    }.get(id_, id_)

data = load_questions()
DIM_WEIGHTS = data["dimensions"]
QUESTIONS = data["questions"]
KNOCKOUTS = data["knockouts"]

st.markdown(\"\"\"\n# Hammer & Nails – Echo Park\n**Sales Associate / Member Concierge** – Candidate Fit Screener\n\n> Quality is in the details. This screener highlights hospitality, membership sales, and reliability — the core of the role.\n\"\"\")


with st.form("screener"):
    answers = {}
    for q in QUESTIONS:
        st.markdown(f\"### {q['label']}\")
        if q.get("help"):
            st.caption(q["help"])

        kind = q["kind"]
        ans = None

        if kind == "text":
            if q.get("minChars", 0) > 60 or q["id"] in ["best_day"]:
                ans = st.text_area(" ", key=q["id"])
            else:
                ans = st.text_input(" ", key=q["id"])
            if q.get("minChars"):
                st.caption(f\"Aim for at least {q['minChars']} characters.\")
        elif kind == "likert":
            left, right = (q.get("labels") or ["Low", "High"])
            st.write(f\"{left} ← → {right}\")
            ans = st.slider(" ", 1, 5, 3, key=q["id"])
        elif kind == "select":
            options = [o["label"] for o in q.get("options", [])]
            values = [o["value"] for o in q.get("options", [])]
            label = st.selectbox(" ", options, index=None, placeholder="Select an option", key=q["id"])
            ans = None
            if label is not None:
                idx = options.index(label)
                ans = values[idx]
        elif kind == "boolean":
            ans = st.toggle(q["label"], value=False, key=q["id"])
        elif kind == "sjt":
            st.write(q["scenario"])
            choices = [f\"{c['key']}: {c['label']}\" for c in q.get("choices", [])]
            keys = [c["key"] for c in q.get("choices", [])]
            picked = st.radio("Choose one", choices, index=None, key=q["id"])
            ans = keys[choices.index(picked)] if picked is not None else None

        answers[q["id"]] = ans
        st.divider()

    submitted = st.form_submit_button("Review scorecard")

if submitted:
    # Knockout check
    failed = []
    # evenings/weekends
    if not answers.get("availability_evenings", False):
        failed.append("availability_evenings")
    if not answers.get("availability_weekends", False):
        failed.append("availability_weekends")
    # sales comfort
    sc = answers.get("sales_comfort", 3) or 3
    try:
        sc = int(sc)
    except Exception:
        sc = 3
    if sc < 3:
        failed.append("sales_comfort")

    # Scoring per dimension
    dim_totals = {}
    dim_weights = {}
    for q in QUESTIONS:
        dim = q["dimension"]
        dim_w = (q.get("weight", 1)) * DIM_WEIGHTS.get(dim, 1.0)
        s = score_question(q, answers.get(q["id"]))
        dim_totals[dim] = dim_totals.get(dim, 0.0) + s * DIM_WEIGHTS.get(dim, 1.0)
        dim_weights[dim] = dim_weights.get(dim, 0.0) + dim_w

    dim_scores = {d: round((dim_totals[d] / dim_weights[d]) if dim_weights[d] else 0.0) for d in dim_totals}
    overall = 0
    if dim_scores:
        ssum = sum(dim_scores[d] * DIM_WEIGHTS.get(d, 1.0) for d in dim_scores)
        wsum = sum(DIM_WEIGHTS.get(d, 1.0) for d in dim_scores)
        overall = round(ssum / wsum)

    # Tier
    if failed:
        tier = ("Review (Knockout unmet)", "yellow")
    elif overall >= 85:
        tier = ("Strong Match", "green")
    elif overall >= 70:
        tier = ("Promising", "blue")
    elif overall >= 55:
        tier = ("Trainable", "gray")
    else:
        tier = ("Low Match", "red")

    st.success(f"Overall score: **{overall} / 100**  •  Tier: **{tier[0]}**")

    with st.expander("Strengths by dimension"):
        for d, v in sorted(dim_scores.items(), key=lambda kv: kv[1], reverse=True):
            st.write(f\"**{d}** — {v}\") 
            st.progress(v/100)

    with st.expander("Knockouts"):
        if not failed:
            st.write(":white_check_mark: All must‑have requirements met.")
        else:
            for k in failed:
                st.write(f":warning: {pretty_label(k)}")

    with st.expander("Candidate Details"):
        st.write(f\"**Name:** {answers.get('name') or '—'}\") 
        st.write(f\"**Email:** {answers.get('email') or '—'}\") 

    st.markdown(\"### Suggested Interview Probes\") 
    st.markdown(\"- Walk me through how you’d convert a happy first‑time guest into a member.\\n- Tell me about a time you balanced phone, walk‑in, and stylist support simultaneously.\\n- How do you keep the lobby immaculate during peak times?\\n- Describe a time you received coaching that changed your approach at the front desk.\")

    payload = {
        "answers": answers,
        "scoreByDimension": dim_scores,
        "overallScore": overall,
        "knockoutFailed": failed,
        "timestamp": datetime.utcnow().isoformat(),
        "location": "Hammer & Nails – Echo Park"
    }
    st.download_button("Download JSON", data=json.dumps(payload, indent=2), file_name=f"H&N-EP-candidate-{answers.get('email','anonymous')}.json", mime="application/json")

