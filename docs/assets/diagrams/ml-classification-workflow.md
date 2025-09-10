# ML Classification Workflow Diagram

This diagram shows the complete machine learning workflow for workout classification with algorithm transparency.

```mermaid
flowchart TD
    Start([Workout Data Input]) --> Validate{Data Validation}
    
    Validate -->|Valid| Extract[Extract Features<br/>• Pace (min/mile)<br/>• Distance (miles)<br/>• Duration (seconds)]
    Validate -->|Invalid| Error[Error: Invalid Data<br/>Log & Return]
    
    Extract --> Preprocess[Preprocessing<br/>• Handle missing values<br/>• Outlier detection<br/>• Data type conversion]
    
    Preprocess --> Scale[Feature Scaling<br/>StandardScaler()<br/>• Mean = 0<br/>• Std Dev = 1]
    
    Scale --> Cluster[K-means Clustering<br/>• n_clusters = 3<br/>• random_state = 42<br/>• max_iter = 300]
    
    Cluster --> Assign[Cluster Assignment<br/>• Cluster 0: Fast pace<br/>• Cluster 1: Medium pace<br/>• Cluster 2: Slow pace]
    
    Assign --> Distance[Calculate Distance<br/>to Cluster Centers<br/>• Euclidean distance<br/>• Confidence scoring]
    
    Distance --> Classify{Classification Logic}
    
    Classify -->|Fast Cluster<br/>Pace < 15 min/mile| RunClass[Classification: real_run<br/>Confidence: Distance-based<br/>Color: Green]
    
    Classify -->|Slow Cluster<br/>Pace > 18 min/mile| WalkClass[Classification: choco_adventure<br/>Confidence: Distance-based<br/>Color: Orange]
    
    Classify -->|Medium Cluster<br/>Or Mixed Patterns| MixedClass[Classification: mixed<br/>Confidence: Lower<br/>Color: Blue]
    
    Classify -->|Extreme Values<br/>Pace > 60 or Distance > 50| OutlierClass[Classification: outlier<br/>Confidence: High<br/>Color: Red]
    
    RunClass --> Meta[Generate Metadata<br/>• Algorithm: K-means ML<br/>• File: intelligence_service.py<br/>• Method: classify_workout_types<br/>• Lines: 75-186]
    
    WalkClass --> Meta
    MixedClass --> Meta
    OutlierClass --> Meta
    
    Meta --> Transparency[Algorithm Transparency<br/>• Confidence score (0-100%)<br/>• Parameter values<br/>• Source code references<br/>• Performance metrics]
    
    Transparency --> UI[User Interface Display<br/>• Classification badge<br/>• Confidence visualization<br/>• Expandable explanations<br/>• Feedback collection]
    
    UI --> Feedback{User Feedback?}
    Feedback -->|Yes| Update[Update Algorithm Registry<br/>• Log user corrections<br/>• Track accuracy metrics<br/>• Improve future models]
    
    Feedback -->|No| Store[Store Results<br/>• Classification result<br/>• Confidence score<br/>• Timestamp<br/>• Metadata]
    
    Update --> Store
    Store --> End([Complete])
    Error --> End
    
    %% Styling
    classDef startEnd fill:#e8f5e8,stroke:#4caf50,stroke-width:3px
    classDef process fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    classDef classification fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    classDef error fill:#ffebee,stroke:#f44336,stroke-width:2px
    classDef transparency fill:#f1f8e9,stroke:#8bc34a,stroke-width:2px
    
    class Start,End startEnd
    class Extract,Preprocess,Scale,Cluster,Assign,Distance,Meta,UI,Update,Store process
    class Validate,Classify,Feedback decision
    class RunClass,WalkClass,MixedClass,OutlierClass classification
    class Error error
    class Transparency transparency
```

## Classification Categories Explained

### 🏃 **real_run**
- **Criteria**: Fast cluster, typically 6-12 min/mile pace
- **Features**: Consistent pace, moderate to long distance
- **Confidence**: High when clearly in fast cluster center
- **UI Display**: Green badge, running icon

### 🚶 **choco_adventure** 
- **Criteria**: Slow cluster, typically 20-28 min/mile pace
- **Features**: Leisurely pace, often shorter distances
- **Confidence**: High when clearly in slow cluster center  
- **UI Display**: Orange badge, walking icon

### 🔄 **mixed**
- **Criteria**: Medium cluster or ambiguous patterns
- **Features**: Variable pace, interval training, or walk/run combinations
- **Confidence**: Lower due to cluster boundary proximity
- **UI Display**: Blue badge, mixed activity icon

### ⚠️ **outlier**
- **Criteria**: Extreme values outside normal ranges
- **Features**: Pace >60 min/mile or distance >50 miles
- **Confidence**: High for clear data quality issues
- **UI Display**: Red badge, warning icon

## Transparency Features

### **Confidence Scoring**
- Based on Euclidean distance to cluster center
- Normalized to 0-100% scale
- Visual indicators: Green (high), Yellow (medium), Red (low)

### **Algorithm Traceability**  
- Every classification links to source code
- Parameter values displayed interactively
- Performance metrics updated in real-time

### **User Feedback Integration**
- Correction mechanism for misclassifications
- Accuracy tracking and improvement metrics
- Future model training data collection