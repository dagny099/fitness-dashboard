import pandas as pd
from classification.features import build_features
from classification.rules import predict_proba

def test_rules_predicts():
    df = pd.read_csv('tests/fixtures/workouts_tiny.csv')
    feats = build_features(df)
    P = predict_proba(feats)
    assert set(P.columns) == {'Run','Walk','Hybrid'}
    assert len(P) == len(feats)
