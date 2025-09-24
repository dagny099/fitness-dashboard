# Quick Start Guide

Get your **Fitness Intelligence Platform** running in minutes and discover intelligent insights from your workout data!

## What You'll Experience

This quick start transforms your fitness data into actionable insights:

- 🧠 **Intelligence Dashboard** as your primary interface
- 🤖 **Automatic workout categorization** with smart classification
- 📈 **Trend analysis** with confidence scoring
- 🔍 **Complete transparency** - understand how insights are generated
- 📊 **Personalized recommendations** based on your patterns

## Prerequisites

- ✅ Python 3.10+ installed
- ✅ Dependencies installed (see [Installation](installation.md))
- ✅ MySQL server running locally

## Step 1: Database Setup

Initialize your database with the required schema:

```bash
python scripts/init.py
```

This script prepares your system for intelligent analysis:

- **Creates the `sweat` database** with optimized schema
- **Sets up the `workout_summary` table** for smart classification
- **Configures intelligence services** connection
- **Initializes transparency features** for algorithm explainability

!!! success "System Ready"
    You should see output confirming:
    ```
    Database 'sweat' created successfully
    Table 'workout_summary' created successfully  
    Intelligence services initialized
    Current row count: 0
    ```

## Step 2: Load Your Fitness Data

### Option A: Use Your Own Data (Recommended)

1. **Export from MapMyRun**: Get your workout history as CSV from [MapMyRun](https://www.mapmyfitness.com/workout/export/csv)
2. **Replace sample file**: `src/user2632022_workout_history.csv`
3. **Import with AI processing**:

```bash
python src/update_db.py
```

The AI system will automatically:
- **Classify workouts** using K-means clustering
- **Detect patterns** in your activity history
- **Generate intelligence insights** for immediate analysis
- **Calculate confidence scores** for all classifications

### Option B: Explore with Demo Mode

Launch without data to see AI features:
- Sample intelligence dashboard with demo insights
- Algorithm transparency system fully operational
- AI classification demo with example workouts

## Step 3: Launch the AI Intelligence Platform

Start your AI-powered fitness dashboard:

```bash
streamlit run src/streamlit_app.py
```

Visit: **http://localhost:8501**

You'll land directly on the **Intelligence Dashboard** - your AI command center!

## Step 4: Discover Your AI Intelligence

### 🧠 Intelligence Dashboard (Your Landing Page)

![Your Intelligence Dashboard](../assets/screenshots/pages/intelligence-dashboard-full.png)

**First thing you'll see:**
```
🧠 Your AI analyzed 2,409 workouts and discovered 4 key insights
Last updated: 2 minutes ago | 87% classification confidence
```

### 📊 Daily Intelligence Brief Cards

Three AI-powered insight cards immediately visible:

#### **🎯 Focus Area Today**
AI determines your current priority:
```
🎯 FOCUS AREA: Building Consistency
📊 Current score: 42/100
🤖 AI recommends: Establish regular workout schedule
   Algorithm: Multi-dimensional Consistency Analysis
   Confidence: 85%
```

#### **📈 Trending This Week**
Statistical analysis with confidence:
```
📈 TRENDING: Calorie Burn Improving  
📊 +12.5% increase over 30 days
📈 Linear Regression Analysis
   Confidence: 91% (p-value: 0.09)
```

#### **⚠️ Performance Alerts**
AI-powered monitoring:
```
⚠️ All systems normal
Consistent performance patterns detected
🔍 Statistical Outlier Detection
```

### 🔬 Algorithm Transparency Sidebar

Complete AI explainability system:

**Active AI Systems:**
- 🤖 K-means Classification
- 📈 Linear Regression Trends
- 🔍 Statistical Anomaly Detection  
- 📊 Multi-dimensional Consistency
- 🔮 Performance Forecasting

**Interactive Features:**
- **Algorithm dropdown** - explore any AI system
- **Expandable explanation cards** - understand methodology
- **Source code references** - complete transparency
- **Confidence visualization** - trust through clarity

## Step 5: Explore AI Classification in Action

### 🤖 AI Classification Demo

Watch machine learning categorize your workouts:

- **real_run**: Focused running sessions (8-12 min/mile)
- **choco_adventure**: Walking activities (20-28 min/mile)  
- **mixed**: Combined running/walking sessions
- **outlier**: Unusual patterns requiring attention

### Algorithm Transparency Features

Click any **🤖 algorithm badge** to see:
- **📖 Plain English explanation** of how it works
- **📁 Source code reference** (e.g., `intelligence_service.py:75-186`)
- **⚙️ Parameter details** and configuration
- **📊 Performance metrics** and accuracy rates

## Step 6: Navigate the AI-Enhanced Interface

### **Primary Navigation (Intelligence First)**

#### **🧠 AI Intelligence** (Default)
Your AI command center with:
- Daily intelligence brief
- Algorithm transparency system
- AI classification demonstration
- Personalized recommendations

#### **Traditional Views (AI-Enhanced)**
- **📊 Monthly View**: Statistical summaries with AI annotations
- **🐕 The Choco Effect**: Behavioral transformation insights
- **📅 Calendar Stats**: Workout calendar with AI classification
- **📈 Trends**: Statistical analysis with machine learning
- **📋 History**: Workout table with AI categorization

## Quick AI Demo Walkthrough

Try these AI features immediately:

### **1. Algorithm Exploration** (2 minutes)
- **Click any algorithm badge** (🤖, 📈, 🔍)
- **Read the explanation card** in plain English
- **See source code reference** for complete transparency
- **Check confidence score** to understand AI certainty

### **2. Intelligence Brief Analysis** (3 minutes)
- **Review your focus area** and AI recommendation
- **Explore trending analysis** with statistical confidence
- **Check performance alerts** for pattern recognition
- **Click "How was this calculated?"** for detailed explanations

### **3. AI Classification Demo** (5 minutes)
- **Watch AI categorize workouts** in real-time
- **See step-by-step reasoning** for each classification
- **Understand confidence scoring** for AI decisions
- **Provide feedback** to improve accuracy

## AI System Configuration

### **Automatic Environment Detection**
- **Development** (macOS): Local MySQL with full AI features
- **Production** (Linux): AWS RDS with scalable AI processing

### **AI Performance Standards**
- **<5 seconds**: Classification for 1,000+ workouts  
- **87% accuracy**: Workout classification confidence
- **Real-time**: Intelligence brief generation
- **<3 seconds**: Algorithm transparency loading

## Understanding Your AI Data

### **Workout Classification Results**

| AI Category | Description | Typical Features |
|-------------|-------------|------------------|
| **real_run** 🏃 | Focused running | 8-12 min/mile pace, consistent effort |
| **choco_adventure** 🚶 | Walking activities | 20-28 min/mile, leisurely pace |
| **mixed** 🔄 | Combined activities | Variable pace, intervals |
| **outlier** ⚠️ | Unusual patterns | Extreme values requiring attention |

### **AI Confidence Indicators**

- **🟢 Green (85-100%)**: High confidence, reliable classification
- **🟡 Yellow (70-84%)**: Medium confidence, review recommended  
- **🔴 Red (0-69%)**: Low confidence, manual verification suggested

## Next Steps: Mastering AI Features

Now that you've experienced AI intelligence:

### **Immediate Actions**
1. **[Get Your First AI Insights](first-ai-insights.md)**: Complete your AI onboarding
2. **[Explore User Journeys](../user-guide/user-journeys.md)**: Discover all AI capabilities
3. **[Understanding AI Systems](../ai/overview.md)**: Deep dive into AI architecture

### **Advanced AI Usage**
1. **Provide feedback** on AI classifications to improve accuracy
2. **Explore algorithm transparency** for technical understanding  
3. **Use AI recommendations** for training optimization
4. **Monitor AI performance** metrics and improvements

### **Integration & Development**
1. **[Developer AI Guide](../developer/ai-services.md)**: Build with AI services
2. **[API References](../developer/api-reference.md)**: Integrate AI endpoints
3. **[Testing Infrastructure](../developer/testing.md)**: Validate AI functionality

## Troubleshooting AI Features

### **AI Dashboard Issues**

!!! warning "Intelligence Dashboard Not Loading"
    **Symptoms**: AI header missing or blank intelligence brief
    
    **Solutions**:
    - Verify database connection with workout data
    - Check AI services initialization in logs
    - Ensure Python ML dependencies installed (`scikit-learn`, `scipy`)

!!! warning "Algorithm Transparency Not Working"
    **Symptoms**: Algorithm badges not clickable, explanation cards empty
    
    **Solutions**:
    - Check algorithm registry initialization
    - Verify source code file paths in configuration
    - Review browser console for JavaScript errors

!!! warning "AI Classifications Seem Wrong"
    **Symptoms**: Workouts misclassified, low confidence scores
    
    **Solutions**:
    - Provide feedback through UI correction system
    - Check data quality (pace, distance, duration values)
    - Review classification criteria in AI documentation

### **Performance Issues**

!!! tip "Slow AI Response Times"
    **For large datasets (1000+ workouts)**:
    - AI classification should complete in <5 seconds
    - Intelligence brief generation in <3 seconds
    - Algorithm transparency loading in <3 seconds
    
    **If slower**: Check database indexing and memory allocation

## Support & Community

### **Getting Help**
- **AI Algorithm Questions**: Review [Algorithm Transparency Guide](../ai/algorithm-transparency.md)
- **Technical Issues**: Check [Troubleshooting Reference](../reference/troubleshooting.md)
- **Feature Requests**: Submit feedback through AI interface or [GitHub Issues](https://github.com/dagny/fitness-dashboard/issues)

### **Contributing to AI Improvement**
- **User feedback** through classification corrections
- **Algorithm transparency** suggestions for better explanations
- **Performance reporting** for AI system optimization
- **Documentation improvements** for better user understanding

Welcome to the future of fitness analytics - where AI transforms your workout data into actionable intelligence! 🚀