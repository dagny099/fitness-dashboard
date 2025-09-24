from __future__ import annotations
import numpy as np, pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from .utils import CLASSES

FEATURES = ["avg_pace","steps_per_min","speed_mph"]

def _cluster_label_map(X: pd.DataFrame, cluster_ids: np.ndarray) -> dict:
    tmp = pd.DataFrame({"cluster": cluster_ids, "avg_pace": X["avg_pace"].values})
    order = tmp.groupby("cluster")["avg_pace"].median().sort_values().index.tolist()
    return {order[0]: "Run", order[1]: "Hybrid", order[2]: "Walk"}

def predict_proba(df: pd.DataFrame, n_components: int=3, random_state: int=42) -> pd.DataFrame:
    X = df.copy()
    for c in FEATURES:
        if c not in X.columns: X[c] = X[c] if c in X.columns else X["avg_pace"]
    X[FEATURES] = X[FEATURES].fillna(X[FEATURES].median(numeric_only=True))
    Z = StandardScaler().fit_transform(X[FEATURES].values)
    gmm = GaussianMixture(n_components=n_components, random_state=random_state)
    gmm.fit(Z)
    post = gmm.predict_proba(Z)
    clusters = gmm.predict(Z)
    mapping = _cluster_label_map(X, clusters)
    out = np.zeros((len(df), len(CLASSES)))
    for i, cls in enumerate(CLASSES):
        idxs = [k for k,v in mapping.items() if v==cls]
        if idxs: out[:,i] = post[:, idxs].sum(axis=1)
    return pd.DataFrame(out, index=df.index, columns=CLASSES)
