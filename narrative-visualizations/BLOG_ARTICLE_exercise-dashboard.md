---
title: "Exercise Dashboard"
description: "Fitness visualization dashboard integrating local and cloud-stored exercise metrics using Streamlit and AWS RDS."
permalink: /data-stories/exercise-dashboard/
layout: section
section: data-stories
tags: [trend analysis, data visualization]
---

# The Choco Effect: How a Dog Transformed My Running Data
<img src="{{ '/assets/images/choco_puppy_with-stick.png' | relative_url }}" alt="Button hover demo" style="float:right; margin: 0em 0em 1em 1em; max-width:250px; height:auto;">

*A decade of fitness tracking reveals an unexpected truth about consistency, companionship, and the stories hiding in our data*

---

## The Perfect Tracker's Paradox

I was the model quantified-self runner: 2,593 workouts logged over 14 years. Every run tracked, every mile recorded, every pace calculated. MapMyRun dutifully collected it all while I... never actually looked at what it was telling me.

That changed when I finally exported my data and discovered something remarkable: I could pinpoint the exact month my life changed. Not through memory or photos, but through the dramatic shift in my running patterns:  **June 2018. The month I became a different kind of runner.**
<!-- **VISUALIZATION: The Timeline Split**-->
<figure class="chart">
  <iframe src="/assets/visualizations/choco-effect/fig_1_timeline.html" 
          width="100%" 
          height="475px" 
          frameborder="0"
          class="desktop-chart"
          style="border: 1px solid #ddd; border-radius: 8px;">
  </iframe>
  <figcaption><strong>My pace from 2011-2025</strong>: Each workout is colored by average pace - <span style="color: #3498db;">JOGS</span>, <span style="color: #e74c3c;">WALKS</span>, and <span style="color: #9b59b6;">Bit of both? </span> Notice how the density of workouts increases post-Choco arrival 🐾</figcaption>
</figure>
The numbers were so dramatic I initially thought I'd made a data processing error:
- **Before June 2018**: 505 workouts over 7 years (6 workouts/month)
- **After June 2018**: 2,088 workouts over 6.5 years (27 workouts/month)

That's not improvement. That's transformation. A 4.5x increase in consistency that happened virtually overnight and never reverted.

But the frequency change was just the beginning. The *nature* of my workouts had fundamentally shifted:

<!-- **VISUALIZATION: The Pace Transformation]** -->
<figure class="chart">
  <figcaption><strong>Bimodal Distribution Emerges</strong>: The violin plot shows pace distribution before/after June 2018. Before, tightly distributed around 9.3 min/mi. After, workouts are bimodally distributed with peaks at 10 min/mi (runs) and 24 min/mi (walks). (similar for duration and distance)🐾</figcaption>
  <iframe src="/assets/visualizations/choco-effect/visualization_2_compare_histograms_3_metrics.html" 
          width="100%" 
          height="500" 
          frameborder="0"
          class="desktop-chart"
          style="border: 1px solid #ddd; border-radius: 8px;">
  </iframe>
</figure>


**Before Choco**:
- Average pace: 9.3 min/mile
- Average distance: 5.2 miles
- Activity type: Running. Just running.

**After Choco**:
- Average pace: 19.5 min/mile (10+ minutes slower!)
- Average distance: 2.7 miles  
- Activity type: Complete chaos

Something had fundamentally changed about how I exercised. And that something had four legs and a tail.

---

## Meet Choco: The Data Scientist I Didn't Know I Needed

<details markdown="1" open>
<summary>🐕 The Technical Details of Dog-Driven Data</summary>

Choco, my Labrador Retriever, didn't just join my workouts—he restructured them entirely. The data reveals two distinct activity profiles post-June 2018:

**Profile 1: "Real Runs" (14% of workouts)**
- Pace: 8-12 min/mile
- Distance: 3-8 miles
- Pattern: Early morning, while Choco sleeps

**Profile 2: "Choco Adventures" (76% of workouts)**
- Pace: 20-28 min/mile
- Distance: 1-3 miles
- Pattern: Any time, because every walk counts

The remaining 10%? That's where it gets interesting—transition zones where I clearly couldn't decide if we were running or walking.

</details>

Here's what actually happened: In June 2018, I adopted a rescue dog who had her own ideas about exercise. Suddenly, my rigid "training runs" exploded into a spectrum of activities:

- Morning runs (that turned into sniff-walks)
- Evening walks (that sometimes became runs)  
- "Quick bathroom breaks" (that MapMyRun auto-tracked)
- Weekend adventures (part hike, part sprint, part social hour)

My carefully curated workout data became beautifully chaotic—and unexpectedly revealing.

> **[VISUALIZATION: The Consistency Revolution]**
> *Calendar heatmap showing workout frequency by day, 2015-2025. Sparse dots before June 2018 transform into an almost-daily pattern after. The "Choco line" is clearly visible.*

<div class="chart-container">
  <iframe src="/assets/visualizations/choco-effect/visualization_3_consistency_rolling_avg.html" 
          width="100%" 
          height="600" 
          frameborder="0"
          class="desktop-chart"
          style="border: 1px solid #ddd; border-radius: 8px;">
  </iframe>
  
  <!-- <img src="/assets/visualizations/choco-effect/XXX.png" 
       alt="Vision API analysis pipeline diagram" 
       class="mobile-chart"
       style="width: 100%; border-radius: 8px;">
  -->
</div>

---

## The Paradox of Imperfect Data

The traditional data quality expert in me initially saw problems:
- Pace metrics were now "contaminated" by walks
- Distance averages were "ruined" by short outings  
- Activity categorization was inconsistent

But the human in me saw the real story: **Choco didn't mess up my data—he revealed what actually drives exercise consistency.**

<details markdown="1" open>
<summary>📊 The Numbers Behind the Transformation</summary>

**Consistency Metrics**:  
- Longest streak pre-Choco: 14 days  
- Longest streak post-Choco: 247 days  
- Monthly variance pre-Choco: ±8.7 workouts  
- Monthly variance post-Choco: ±3.2 workouts  
 
**Behavioral Changes**:  
- Morning workouts: 85% → 62% (dogs don't care about your schedule)  
- Weekend activity: 2x increase (every day is workout day with a dog)  
- Seasonal consistency: Winter dropoff eliminated (dogs need walks year-round)  

</details>

The insights hiding in this "messy" data were profound:

1. **Consistency beats intensity**: My average pace slowed by 10 minutes/mile, but my fitness improved because I was moving every single day.

2. **Perfect is the enemy of good**: When every walk "counted," I stopped skipping workouts because they wouldn't be "real runs."

3. **External motivation works**: Choco's needs created a consistency no training plan ever achieved.

---

## The Technical Challenge: Can Machines Learn the Difference?

This discovery led to an intriguing question: If the difference between my runs and dog walks is so clear in the data, can machine learning identify them without labels?

> **[INTERACTIVE ELEMENT: Predict the Activity Type]**
> *Quiz showing 5 workout metrics. Reader guesses "Run" or "Dog Walk" before revealing the answer and ML prediction.*

The bimodal distribution in my pace data suggests clear clusters:
- **Cluster 1**: 8-12 min/mile, 3-8 miles, 30-70 minutes
- **Cluster 2**: 20-28 min/mile, 1-3 miles, 20-90 minutes

But here's where it gets interesting: there's a fuzzy middle ground where runs became walks, or walks became runs. These edge cases might reveal the most about how life happens in the margins of our planned activities.

**Coming in Episode 2**: Building a classifier to automatically identify workout types, and discovering what the "unclassifiable" workouts reveal about the beautiful messiness of real life.

---

## Your Data Has Stories Too

The Choco Effect taught me that the most interesting insights often hide in what we consider "data quality issues." Those inconsistencies, outliers, and sudden changes? They're life happening.

<details markdown="1">
<summary>🛠️ Try This With Your Own Data</summary>  

**Quick Analysis Checklist**:  
1. Export your fitness data (Strava, Garmin, Apple Health, etc.)  
2. Look for sudden changes in:  
   - Frequency patterns  
   - Average metrics (pace, distance, duration)  
   - Workout time distributions  
3. Ask yourself: What life change might explain this?  
4. Check if categories or labels changed around the same time  

**SQL Starter Query**:
```sql
-- Find your "Choco moment"
WITH monthly_stats AS (
  SELECT 
    DATE_TRUNC('month', workout_date) as month,
    COUNT(*) as workout_count,
    AVG(distance) as avg_distance,
    AVG(pace) as avg_pace
  FROM workouts
  GROUP BY 1
)
SELECT 
  month,
  workout_count,
  workout_count - LAG(workout_count) OVER (ORDER BY month) as change
FROM monthly_stats
ORDER BY ABS(change) DESC
LIMIT 10;
```

</details>

**The real lesson isn't about dogs or running**. It's that our data tells stories we don't expect. My "failed" attempt at maintaining pristine running data became a beautiful record of life change. The metrics got messy, but my habits got better.

What stories are hiding in your perfectly tracked imperfect life?

---

## What's Next

**Episode 2: "Teaching Machines to Spot Dog Walks"** - Can unsupervised learning identify workout types based purely on pace, distance, and duration patterns? More importantly, what do the edge cases teach us about the fuzzy boundaries in our categorized lives?

**Episode 3: "The Weather Excuse Myth"** - Combining workout data with historical weather reveals surprising patterns about what actually affects exercise consistency (spoiler: it's not rain).

---

**[Links Section]**
- 🔗 **[Interactive Dashboard](your-dashboard-url)** - Explore the full workout dataset
- 🐙 **[GitHub Repository](your-repo-url)** - Code, data, and notebooks
- 📊 **[SQL Playground](your-playground-url)** - Query the workout database yourself
- 📈 **[Dataset](sample-data-url)** - Download a sample for your own analysis

---

*Barbara is a data scientist who discovered that the best insights come from imperfect data. Her dog Choco is a better personal trainer than any app, though he refuses to wear a fitness tracker. Follow their data adventures at [barbhs.com].*