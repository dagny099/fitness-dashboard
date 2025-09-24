import streamlit as st, pandas as pd
from classification.features import build_features
from classification.rules import predict_proba as rules_proba
from classification.gmm import predict_proba as gmm_proba
from classification.ensemble import blend
from classification.utils import to_label, CLASSES

st.set_page_config(page_title="Run/Walk/Hybrid — Demo", layout="wide")
st.title("Run/Walk/Hybrid — Exploration Demo (Sprint 1)")
st.caption("Upload a workouts CSV; switch algorithms; inspect uncertainty; export results.")

uploaded = st.file_uploader("Upload CSV of workouts", type=["csv"])
algo = st.selectbox("Algorithm", ["rules","gmm","ensemble"], index=1)
hyb_low = st.slider("Hybrid band — low", 0.0, 1.0, 0.45, 0.01)
hyb_high = st.slider("Hybrid band — high", 0.0, 1.0, 0.55, 0.01)

if uploaded is not None:
    raw = pd.read_csv(uploaded)
    feats = build_features(raw)
    valid = feats[feats["is_valid"]].copy()
    if valid.empty:
        st.warning("No valid rows after quality filters."); st.stop()
    if algo=="rules": P = rules_proba(valid)
    elif algo=="gmm": P = gmm_proba(valid)
    else: P = blend(rules_proba(valid), gmm_proba(valid), weights=[0.25,0.75])
    rows = []
    for idx, row in P.iterrows():
        label, conf = to_label(row.values, hybrid_low=hyb_low, hybrid_high=hyb_high)
        rows.append({"workout_id": idx, "predicted_type": label, "confidence": conf})
    L = pd.DataFrame(rows).set_index("workout_id")
    out = pd.concat([valid, P, L], axis=1)

    st.subheader("Summary")
    c1,c2,c3 = st.columns(3)
    c1.metric("Rows (valid)", len(valid))
    c2.metric("Mean confidence", round(out["confidence"].mean(),3))
    c3.metric("Hybrid fraction", round((out["predicted_type"]=="Hybrid").mean(),3))

    st.subheader("Class distribution")
    st.bar_chart(out["predicted_type"].value_counts())

    st.subheader("Most uncertain")
    st.dataframe(out.sort_values("confidence").head(20))

    st.subheader("Predictions table")
    st.dataframe(out.reset_index())

    csv = out.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="predictions.csv", mime="text/csv")
else:
    st.info("Upload a CSV to begin — expected columns: workout_id, avg_pace, distance_mi, duration_sec, steps.")
