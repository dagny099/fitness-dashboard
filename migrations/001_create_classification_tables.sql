-- Sprint 2 (not required to run now)
CREATE TABLE IF NOT EXISTS classification_runs (
  run_id CHAR(36) PRIMARY KEY,
  algorithm VARCHAR(64) NOT NULL,
  version VARCHAR(32) NOT NULL,
  params JSON NOT NULL,
  data_snapshot VARCHAR(64),
  code_sha CHAR(40),
  ran_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS workout_classifications (
  workout_id VARCHAR(20) NOT NULL,
  run_id CHAR(36) NOT NULL,
  predicted_type VARCHAR(20) NOT NULL,
  confidence DECIMAL(4,3) NOT NULL,
  features_used JSON,
  explanations JSON,
  classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (workout_id, run_id),
  FOREIGN KEY (workout_id) REFERENCES workout_summary(workout_id),
  FOREIGN KEY (run_id) REFERENCES classification_runs(run_id)
);
