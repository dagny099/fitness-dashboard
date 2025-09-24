# Interactive Algorithm Explorer

*Interactive documentation component for exploring AI algorithms with live examples and explanations*

## Component Overview

The Interactive Algorithm Explorer provides hands-on exploration of AI algorithms with real-time examples, parameter adjustment, and transparent explanations of how each algorithm works.

## Interactive Elements

### 1. K-means Classification Demo

```markdown
!!! interactive "K-means Workout Classification"
    
    **Try the Algorithm**: Adjust parameters and see how classifications change
    
    === "Input Data"
        | Workout ID | Pace (min/mile) | Distance (miles) | Duration (min) |
        |------------|-----------------|------------------|----------------|
        | 1 | 8.5 | 5.0 | 42.5 |
        | 2 | 24.2 | 2.1 | 50.8 |
        | 3 | 12.1 | 3.2 | 38.7 |
        
        **Interactive Controls:**
        - **Number of Clusters**: `[2] [3] [4] [5]` (Click to change)
        - **Random State**: `[42] [123] [456]` (For reproducibility)
        
    === "Algorithm Process"
        **Step 1: Feature Scaling**
        ```
        StandardScaler().fit_transform(features)
        Mean: [0, 0, 0]
        Std:  [1, 1, 1]
        ```
        
        **Step 2: K-means Clustering**
        ```python
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(scaled_features)
        ```
        
        **Step 3: Classification Mapping**
        - **Cluster 0** (Fast): → `real_run`
        - **Cluster 1** (Medium): → `mixed`  
        - **Cluster 2** (Slow): → `choco_adventure`
        
    === "Results & Confidence"
        **Classifications:**
        | Workout ID | Classification | Confidence | Distance to Center |
        |------------|----------------|------------|-------------------|
        | 1 | real_run | 92% | 0.12 |
        | 2 | choco_adventure | 88% | 0.18 |
        | 3 | mixed | 76% | 0.31 |
        
        **Confidence Calculation:**
        ```python
        confidence = 100 * (1 - distance_to_center / max_distance)
        ```
        
    === "Source Code"
        **Implementation Reference**:
        ```python
        # File: src/services/intelligence_service.py
        # Lines: 75-186
        # Method: classify_workout_types()
        
        def classify_workout_types(self, workouts_df):
            features = workouts_df[['pace_min_per_mile', 'distance_mi', 'duration_sec']]
            
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            kmeans = KMeans(n_clusters=3, random_state=42)
            clusters = kmeans.fit_predict(features_scaled)
            
            return self._map_clusters_to_classifications(clusters, workouts_df)
        ```
```

### 2. Statistical Trend Analysis Interactive

```markdown
!!! interactive "Linear Regression Trend Analysis"
    
    **Explore Trend Detection**: See how statistical confidence changes with different data patterns
    
    === "Sample Data"
        **Performance Metrics Over Time:**
        
        *Click data points to modify values and see trend changes*
        
        ```
        Week 1: 450 calories  ←→ [Adjustable: 300-600]
        Week 2: 480 calories  ←→ [Adjustable: 300-600]  
        Week 3: 510 calories  ←→ [Adjustable: 300-600]
        Week 4: 530 calories  ←→ [Adjustable: 300-600]
        ```
        
        **Current Trend**: 📈 Ascending (26.7 cal/week)
        **Statistical Confidence**: 94% (p-value: 0.06)
        
    === "Algorithm Details"
        **Linear Regression Analysis:**
        ```python
        from scipy.stats import linregress
        
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        
        trend_direction = 'ascending' if slope > 0 else 'descending'
        confidence = (1 - p_value) * 100
        trend_strength = 'strong' if abs(r_value) > 0.7 else 'moderate'
        ```
        
        **Current Calculation:**
        - **Slope**: +26.7 calories/week
        - **R-squared**: 0.89 (strong correlation)
        - **P-value**: 0.06 (significant at α=0.1)
        
    === "Confidence Visualization"
        **Confidence Score Breakdown:**
        
        ```
        🟢 High Confidence (85-100%): Take action on this trend
        🟡 Medium Confidence (70-84%): Monitor closely  
        🔴 Low Confidence (0-69%): Need more data
        ```
        
        **Your Current Score: 94%** 🟢
        
        **Interpretation**: This is a statistically significant upward trend in calorie burn. The high confidence score indicates this pattern is likely to continue.
        
    === "Interactive Parameters"
        **Adjust Analysis Settings:**
        
        - **Significance Level**: `[0.05] [0.1] [0.2]`
        - **Minimum Data Points**: `[3] [5] [7]` 
        - **Trend Window**: `[7 days] [30 days] [90 days]`
        
        *Changes update results in real-time*
```

### 3. Algorithm Transparency Widget

```markdown
!!! widget "Algorithm Transparency Explorer"
    
    **Explore Any AI Algorithm**: Click algorithm badges to see complete transparency information
    
    <div class="algorithm-grid">
        <div class="algo-card" onclick="showAlgorithm('kmeans')">
            <div class="algo-icon">🤖</div>
            <div class="algo-name">K-means Classification</div>
            <div class="algo-confidence">87% accuracy</div>
        </div>
        
        <div class="algo-card" onclick="showAlgorithm('regression')">
            <div class="algo-icon">📈</div>
            <div class="algo-name">Linear Regression</div>
            <div class="algo-confidence">R² = 0.89</div>
        </div>
        
        <div class="algo-card" onclick="showAlgorithm('anomaly')">
            <div class="algo-icon">🔍</div>
            <div class="algo-name">Anomaly Detection</div>
            <div class="algo-confidence">3 methods</div>
        </div>
        
        <div class="algo-card" onclick="showAlgorithm('consistency')">
            <div class="algo-icon">📊</div>
            <div class="algo-name">Consistency Analysis</div>
            <div class="algo-confidence">4 dimensions</div>
        </div>
    </div>
    
    <div id="algorithm-details" class="algo-details">
        <h4>Select an algorithm above to see detailed information</h4>
        <p>Interactive transparency information will appear here including:</p>
        <ul>
            <li>Complete source code references</li>
            <li>Parameter explanations</li>
            <li>Performance metrics</li>
            <li>Real-time confidence scoring</li>
        </ul>
    </div>
```

### 4. User Journey Simulator

```markdown
!!! simulator "AI Discovery Journey Simulator"
    
    **Experience the AI Platform**: Step through different user personas discovering AI features
    
    === "New User Journey"
        **Persona**: First-time visitor with no AI experience
        
        **Step 1: Landing Page** *(Current Step)*
        ```
        🧠 Your AI analyzed 2,409 workouts and discovered 4 key insights
        Last updated: 2 minutes ago | 87% classification confidence
        ```
        
        **User Reaction**: *"This mentions AI insights - what does that mean?"*
        
        **Next Action Options:**
        - **[Click AI Intelligence]** → Go to intelligence dashboard
        - **[Scroll down]** → See intelligence brief cards
        - **[Click algorithm badge]** → Learn about transparency
        
        **Progress**: Step 1 of 8 | Trust Level: 20%
        
    === "Technical User Journey"  
        **Persona**: Developer wanting to understand AI implementation
        
        **Current Step**: Algorithm transparency exploration
        
        **Available Actions:**
        - **Examine source code** (`intelligence_service.py:75-186`)
        - **Review algorithm parameters** (n_clusters=3, random_state=42)
        - **Check performance metrics** (87% accuracy, <5s processing)
        - **Explore test suite** (200+ test methods)
        
        **Developer Satisfaction**: 85% (High transparency score)
        
    === "Casual User Journey"
        **Persona**: Fitness enthusiast wanting insights
        
        **Current Focus**: Understanding AI recommendations
        
        **AI Recommendation**: "Focus on building consistency"
        **User Question**: "Why this recommendation?"
        
        **Transparency Available:**
        - **Algorithm**: Multi-dimensional Consistency Analysis
        - **Your Score**: 42/100 (needs improvement)
        - **Confidence**: 85% (highly confident recommendation)
        - **Next Steps**: Establish regular workout schedule
```

## Interactive Code Examples

### Real-time Algorithm Testing

```markdown
!!! code-example "Try the AI Classification Algorithm"
    
    **Paste Your Workout Data** (CSV format):
    ```
    workout_id,pace_min_per_mile,distance_mi,duration_sec
    1,8.5,5.0,2550
    2,24.2,2.1,3048  
    3,12.1,3.2,2322
    ```
    
    **Results** (Updated in real-time):
    ```json
    {
        "classifications": {
            "1": "real_run",
            "2": "choco_adventure", 
            "3": "mixed"
        },
        "confidence_scores": {
            "1": 92.3,
            "2": 88.7,
            "3": 76.1
        },
        "algorithm_metadata": {
            "algorithm": "K-means ML Classification",
            "file_reference": "intelligence_service.py:75-186",
            "processing_time": 0.023
        }
    }
    ```
    
    **Try Different Data**: Modify the values above and see classifications change instantly!
```

## Documentation Enhancement Features

### 1. Contextual Help System

```markdown
!!! help "Smart Help System"
    
    Hover over any AI term for instant explanation:
    
    - **[K-means clustering]** *(hover for definition)*
    - **[Confidence score]** *(hover for explanation)*  
    - **[Algorithm transparency]** *(hover for details)*
    - **[Statistical significance]** *(hover for meaning)*
    
    **Dynamic Context**: Help content changes based on user's current page and technical level.
```

### 2. Progressive Disclosure Interface

```markdown
!!! progressive "Multi-Level Algorithm Explanation"
    
    **Level 1: Simple** *(Click to expand)*
    > The AI looks at your workout pace and distance to automatically categorize activities.
    
    **Level 2: Detailed** *(Click to expand)*
    > K-means clustering algorithm analyzes three features (pace, distance, duration) using standardized values to group similar workouts into categories like running, walking, or mixed activities.
    
    **Level 3: Technical** *(Click to expand)*
    > ```python
    > features = StandardScaler().fit_transform(workouts[['pace', 'distance', 'duration']])
    > kmeans = KMeans(n_clusters=3, random_state=42)
    > classifications = kmeans.fit_predict(features)
    > ```
    
    **Level 4: Expert** *(Click to expand)*
    > Complete source code, parameter tuning options, performance benchmarks, and extension points for custom classification algorithms.
```

### 3. Real-time Performance Dashboard

```markdown
!!! dashboard "Live AI Performance Metrics"
    
    **Current System Status**: 🟢 All AI systems operational
    
    **Real-time Metrics**:
    - **Classification Speed**: 2.3s (Target: <5s) ✅
    - **Accuracy Rate**: 87.2% (Target: >85%) ✅  
    - **Confidence Average**: 81.4% (Target: >75%) ✅
    - **Active Users**: 23 (Capacity: 50) ✅
    
    **Last Updated**: 15 seconds ago | **Auto-refresh**: ON
    
    *Metrics update automatically every 30 seconds*
```

## Implementation Notes

### MkDocs Integration

The interactive elements can be implemented using:

1. **Custom CSS/JavaScript** for interactive widgets
2. **Pymdownx extensions** for enhanced markdown features  
3. **External widgets** embedded via iframes
4. **React/Vue components** for complex interactions

### Browser Compatibility

All interactive elements designed to work with:
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile devices with touch interface
- Progressive enhancement for older browsers
- Keyboard navigation support

### Performance Considerations

- **Lazy loading** for complex interactive elements
- **Caching** for algorithm explanations and examples
- **Responsive design** for mobile optimization
- **Accessibility compliance** with WCAG guidelines

These interactive documentation elements transform static documentation into an engaging, educational experience that helps users understand and trust the AI systems powering their fitness intelligence platform.