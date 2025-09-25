# Quick Reference

Essential commands, tasks, and troubleshooting for daily use of your Fitness Dashboard.

## 🚀 Getting Started (First Time)

### Setup Commands
```bash
# 1. Initialize database
python scripts/init.py

# 2. Import your data
python src/update_db.py

# 3. Start dashboard
streamlit run src/streamlit_app.py
```

### First Steps
1. **Visit**: http://localhost:8501
2. **Import data**: Replace `src/user2632022_workout_history.csv` with your export
3. **Check insights**: Look for focus area suggestions and trends

## 📊 Common Tasks

### Data Management
| Task | How To |
|------|--------|
| **Import new workouts** | Replace CSV file → Run `python src/update_db.py` |
| **Fix wrong categories** | Model Management page → Find workout → Correct → Retrain |
| **Check data quality** | Custom Queries → Look for outliers (pace >60 or <4 min/mile) |
| **Export results** | Copy query results → Paste into spreadsheet |

### Analysis Tasks
| Task | Where To Go |
|------|-------------|
| **See recent trends** | Main dashboard → Trending card |
| **Compare time periods** | Trends page → Date range picker |
| **Find best workouts** | Custom Queries → ORDER BY avg_pace_min_mi LIMIT 10 |
| **View monthly stats** | Monthly View tab |
| **Get recommendations** | Main dashboard → Focus Area card |

### Troubleshooting
| Problem | Quick Fix |
|---------|-----------|
| **No data showing** | Check if you ran `python src/update_db.py` |
| **Classifications wrong** | Model Management → Correct examples → Retrain |
| **Dashboard won't start** | Check MySQL is running → Verify `poetry install` worked |
| **Import errors** | Check CSV file path → Look for missing columns |

## 🔧 Useful SQL Queries

Copy these into the Custom Queries page:

### Find Your Best Runs
```sql
SELECT workout_date, distance_mi, avg_pace_min_mi, kcal_burned
FROM workout_summary
WHERE activity_type = 'real_run'
ORDER BY avg_pace_min_mi
LIMIT 10;
```

### Monthly Activity Summary
```sql
SELECT
    DATE_FORMAT(workout_date, '%Y-%m') as month,
    COUNT(*) as total_workouts,
    SUM(distance_mi) as total_miles,
    AVG(avg_pace_min_mi) as avg_pace
FROM workout_summary
GROUP BY DATE_FORMAT(workout_date, '%Y-%m')
ORDER BY month DESC;
```

### Data Quality Check
```sql
SELECT * FROM workout_summary
WHERE avg_pace_min_mi > 60 OR avg_pace_min_mi < 4
   OR distance_mi > 50 OR distance_mi < 0.1
ORDER BY workout_date DESC;
```

### Activity Type Breakdown
```sql
SELECT
    activity_type,
    COUNT(*) as count,
    AVG(distance_mi) as avg_distance,
    AVG(kcal_burned) as avg_calories
FROM workout_summary
GROUP BY activity_type
ORDER BY count DESC;
```

## 🎯 Understanding Your Results

### Focus Area Meanings
- **Building Consistency**: Workout irregularly → Establish routine
- **Adding Frequency**: Consistent but infrequent → Work out more often
- **Optimizing Performance**: Already consistent → Focus on improvement

### Workout Categories
- **Real Runs**: 8-12 min/mile pace, focused running
- **Walking**: 20-28 min/mile pace, leisure activity
- **Mixed**: Variable pace, intervals or run/walk combo
- **Outlier**: Unusual data, check for errors

### Confidence Scores
- **85-100%**: High confidence, trust the result
- **70-84%**: Medium confidence, review if seems wrong
- **Below 70%**: Low confidence, likely needs correction

## ⚡ Quick Fixes

### Dashboard Issues
```bash
# Dashboard won't start
lsof -ti:8501 | xargs kill  # Kill existing process
streamlit run src/streamlit_app.py

# Database connection errors
brew services restart mysql  # macOS
sudo systemctl restart mysql  # Linux

# Import not working
ls -la src/user2632022_workout_history.csv  # Check file exists
head src/user2632022_workout_history.csv    # Check format
```

### Model Issues
1. **Go to Model Management page**
2. **Check accuracy** - if <70%, needs retraining
3. **Review recent classifications** - correct obvious mistakes
4. **Click "Retrain Model"** after corrections

### Data Issues
1. **Run data quality SQL** (see above)
2. **Fix obvious errors** in your CSV file
3. **Re-import**: `python src/update_db.py`
4. **Refresh dashboard** to see changes

## 📝 Regular Maintenance

### Weekly
- [ ] Export new data from fitness app
- [ ] Run `python src/update_db.py`
- [ ] Check Model Management accuracy

### Monthly
- [ ] Review and correct any wrong classifications
- [ ] Retrain model if accuracy drops
- [ ] Export analysis for personal records

### As Needed
- [ ] Clean up obvious data errors
- [ ] Update date ranges for seasonal analysis
- [ ] Backup your database

## 🆘 When to Get Help

**Check Documentation First:**
- [Common Tasks](user-journeys.md) - Step-by-step guides
- [Dashboard Overview](dashboard-overview.md) - Interface explanations
- [Troubleshooting](../reference/troubleshooting.md) - Detailed problem-solving

**Still Stuck?**
- Submit issue on [GitHub](https://github.com/dagny/fitness-dashboard/issues)
- Include error messages and what you were trying to do
- Mention your operating system and Python version

---

💡 **Bookmark this page** - it has everything you need for daily dashboard use!