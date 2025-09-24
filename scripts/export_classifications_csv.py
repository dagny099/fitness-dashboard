#!/usr/bin/env python3
import argparse, pandas as pd
from classification.features import build_features
from classification.rules import predict_proba as rules_proba
from classification.gmm import predict_proba as gmm_proba
from classification.ensemble import blend
from classification.utils import to_label

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--algo", default="gmm", choices=["rules","gmm","ensemble"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--hybrid-low", type=float, default=0.45)
    ap.add_argument("--hybrid-high", type=float, default=0.55)
    args = ap.parse_args()

    raw = pd.read_csv(args.input)
    feats = build_features(raw)
    valid = feats[feats["is_valid"]].copy()
    if args.algo=="rules":
        P = rules_proba(valid)
    elif args.algo=="gmm":
        P = gmm_proba(valid)
    else:
        P = blend(rules_proba(valid), gmm_proba(valid), weights=[0.25,0.75])

    rows = []
    for idx, row in P.iterrows():
        label, conf = to_label(row.values, args.hybrid_low, args.hybrid_high)
        rows.append({"workout_id": idx, "predicted_type": label, "confidence": conf})
    out = pd.concat([valid, P, pd.DataFrame(rows).set_index("workout_id")], axis=1)
    out.to_csv(args.out, index=True)
    print(f"Wrote {len(out)} rows to {args.out}")

if __name__ == "__main__": 
    main()
