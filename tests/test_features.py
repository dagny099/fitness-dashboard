import pandas as pd
from classification.features import build_features

def test_build_features_basic():
    df = pd.read_csv('tests/fixtures/workouts_tiny.csv')
    feats = build_features(df)
    assert {'steps_per_min','speed_mph','is_valid'} <= set(feats.columns)
    assert (feats['is_valid'].isin([True, False])).all()
