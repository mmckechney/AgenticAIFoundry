# AI Maturity Assessment Tool - Quick Reference Guide

## 🚀 Quick Start

### Prerequisites Checklist
- [ ] Azure AI Foundry project configured
- [ ] Azure OpenAI deployment ready
- [ ] Environment variables set
- [ ] Python dependencies installed

### 5-Minute Setup
```bash
# 1. Clone and navigate
cd /path/to/AgenticAIFoundry

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Azure credentials

# 4. Run the application
streamlit run stasses.py
```

## 📊 Component Overview

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Streamlit UI** | Web interface | Interactive forms, real-time visualization |
| **Assessment Engine** | Core logic | Score calculation, quadrant classification |
| **Azure OpenAI** | AI recommendations | Strategic guidance, implementation plans |
| **Telemetry Service** | Monitoring | Performance tracking, error logging |
| **Config Manager** | Configuration | JSON-based assessment structure |

## ⚙️ Environment Variables

### Required Configuration
```bash
# Azure OpenAI Service
AZURE_OPENAI_ENDPOINT=https://<account>.openai.azure.com/
AZURE_OPENAI_KEY=<your_openai_key>
AZURE_OPENAI_DEPLOYMENT=<deployment_name>
MODEL_DEPLOYMENT_NAME=<model_name>

# Azure AI Foundry
PROJECT_ENDPOINT=<foundry_project_endpoint>

# Telemetry (Optional)
AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED=true
```

### Quick Configuration Check
```python
import os
required_vars = [
    'AZURE_OPENAI_ENDPOINT',
    'AZURE_OPENAI_KEY', 
    'PROJECT_ENDPOINT',
    'MODEL_DEPLOYMENT_NAME'
]

for var in required_vars:
    if not os.getenv(var):
        print(f"❌ Missing: {var}")
    else:
        print(f"✅ Found: {var}")
```

## 📋 Assessment Dimensions Reference

### 1. Strategy & Governance (Weight: 20%)
**Key Questions:**
- AI strategy documentation
- Business alignment
- Governance framework
- Use case prioritization

**Scoring Guide:**
- **1**: No strategy/governance
- **3**: Basic framework in place  
- **5**: Comprehensive, well-established

### 2. Data & Infrastructure (Weight: 15%)
**Key Questions:**
- Data quality for AI
- Pipeline readiness
- Governance policies
- Tool evaluation processes

### 3. Technology & Tools (Weight: 15%)
**Key Questions:**
- AI/ML platform usage
- Model deployment
- Cloud service integration

### 4. Skills & Culture (Weight: 15%)
**Key Questions:**
- Team AI expertise
- Innovation culture
- Stakeholder awareness
- Executive literacy
- Upskilling programs

### 5. Results & Impact (Weight: 20%)
**Key Questions:**
- Business outcomes
- ROI generation
- KPI tracking

### 6. Responsible AI & Trustworthiness (Weight: 15%)
**Key Questions:**
- Bias monitoring
- Regulatory compliance
- Fairness policies

## 📍 Quadrant Classification

### Quadrant Determination Logic
```python
# Based on two primary dimensions:
x = scores["Results & Impact"]      # X-axis
y = scores["Strategy & Governance"] # Y-axis

# Quadrant assignment:
if x < 3 and y >= 3: quadrant = 2    # Strategy & Vision
elif x >= 3 and y < 3: quadrant = 3  # Execution & Scaling  
elif x < 3 and y < 3: quadrant = 1   # Enablement & Foundation
else: quadrant = 4                   # Results & Optimization
```

### Quadrant Recommendations

| Quadrant | Name | Focus Area | Key Actions |
|----------|------|------------|-------------|
| **1** | Enablement & Foundation | Build capabilities | Invest in data, tools, talent |
| **2** | Strategy & Vision | Strategic planning | Define/refine AI strategy |
| **3** | Execution & Scaling | Operational excellence | Scale initiatives, improve execution |
| **4** | Results & Optimization | Performance optimization | Focus on ROI, responsible AI |

## 🔧 Core Functions Reference

### Main Assessment Function
```python
def assesmentmain():
    """Main Streamlit application entry point"""
    # 1. UI setup and configuration
    # 2. Assessment form generation
    # 3. Score calculation and processing
    # 4. Visualization and results display
```

### AI Recommendation Function
```python
def aoai_callback(query: str) -> str:
    """Generate AI recommendations via Azure OpenAI"""
    # System prompt: AI Assessment Assistant
    # Temperature: 0.7
    # Max tokens: 4000
    # Returns: Strategic guidance and implementation steps
```

### Key Data Structures
```python
# Assessment dimensions loaded from JSON
DIMENSIONS = [
    {
        "name": "Strategy & Governance",
        "weight": 0.2,
        "questions": [...]
    }
]

# Quadrant definitions
QUADRANTS = [
    ("Strategy & Vision", "Focus description"),
    ("Enablement & Foundation", "Focus description"),
    ("Execution & Scaling", "Focus description"), 
    ("Results & Optimization", "Focus description")
]
```

## 📊 Scoring Calculations

### Dimension Score Calculation
```python
# For each dimension:
dimension_score = np.mean([q1_value, q2_value, ...])

# Weighted score:
weighted_score = dimension_score * dimension_weight

# Total assessment score:
total_score = sum(all_weighted_scores)
```

### Visualization Parameters
```python
# Quadrant chart coordinates
x = scores["Results & Impact"]           # X-axis
y = scores["Strategy & Governance"]      # Y-axis

# Bubble visualization
bubble_size = 30 + 20 * np.mean([
    scores["Data & Infrastructure"],
    scores["Technology & Tools"], 
    scores["Skills & Culture"]
])

# Color intensity
color_score = scores["Responsible AI & Trustworthiness"]
```

## 🎨 Visualization Components

### Plotly Chart Configuration
```python
fig = px.scatter(
    x=[x], y=[y],
    size=[bubble_size],
    color=[color_score],
    color_continuous_scale=['red', 'yellow', 'green'],
    range_x=[1, 5], 
    range_y=[1, 5],
    title="AI Maturity Quadrant"
)
```

### Results Data Table
```python
df = pd.DataFrame({
    "Dimension": [dim["name"] for dim in DIMENSIONS],
    "Score (1-5)": [round(scores[dim["name"]], 2) for dim in DIMENSIONS],
    "Weighted": [round(weighted_scores[dim["name"]], 2) for dim in DIMENSIONS]
})
```

## 📡 Telemetry Integration

### OpenTelemetry Setup
```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Configure Azure Monitor
connection_string = project_client.telemetry.get_connection_string()
configure_azure_monitor(connection_string=connection_string)

# Create tracer
tracer = trace.get_tracer(__name__)
```

### Performance Metrics

| Metric | Expected Range | Description |
|--------|----------------|-------------|
| **Form Load Time** | < 2 seconds | Initial UI rendering |
| **Assessment Processing** | 2-5 seconds | Score calculation |
| **AI Recommendation** | 3-8 seconds | OpenAI API response |
| **Visualization Render** | < 1 second | Chart generation |
| **Total Workflow** | 5-15 seconds | Complete assessment |

## 🔍 Common Usage Patterns

### Basic Assessment Flow
```python
# 1. User completes assessment form
user_responses = collect_slider_values()

# 2. Calculate scores
scores = calculate_dimension_scores(user_responses)
weighted_scores = apply_weights(scores)

# 3. Determine quadrant
quadrant = classify_quadrant(scores)

# 4. Generate recommendations  
recommendations = aoai_callback(format_assessment_data(scores))

# 5. Display results
render_results(scores, quadrant, recommendations)
```

### Configuration Modification
```python
# Modify assessment questions
with open('aiassessment.json', 'r') as f:
    config = json.load(f)

# Add new question
new_question = {
    "text": "New assessment question?",
    "desc": "1 = Poor, 5 = Excellent"
}
config[0]["questions"].append(new_question)

# Save updated configuration
with open('aiassessment.json', 'w') as f:
    json.dump(config, f, indent=2)
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### Issue: Azure OpenAI Connection Error
```bash
# Check environment variables
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_KEY

# Verify deployment name
echo $MODEL_DEPLOYMENT_NAME
```

**Solution**: Ensure correct endpoint URL and valid API key

#### Issue: Telemetry Collection Fails
```python
# Check Application Insights configuration
connection_string = project_client.telemetry.get_connection_string()
if not connection_string:
    print("Enable Application Insights in Azure AI Foundry project")
```

**Solution**: Enable tracing in Azure AI Foundry project settings

#### Issue: Form Submission Not Working
```python
# Debug session state
import streamlit as st
st.write("Session state:", st.session_state)

# Check form validation
if st.form_submit_button("Process Assessment"):
    st.write("Form submitted successfully")
```

**Solution**: Ensure all sliders have values and form is properly submitted

#### Issue: Visualization Not Displaying
```python
# Debug plot data
st.write("X coordinate:", x)
st.write("Y coordinate:", y) 
st.write("Bubble size:", bubble_size)

# Check Plotly configuration
import plotly.express as px
if px.__version__ < "5.0.0":
    print("Update Plotly: pip install plotly>=5.0.0")
```

### Performance Optimization

#### Streamlit Caching
```python
@st.cache_data
def load_assessment_config():
    """Cache configuration loading"""
    with open("aiassessment.json", "r") as f:
        return json.load(f)

@st.cache_resource  
def initialize_azure_clients():
    """Cache Azure client initialization"""
    return AzureOpenAI(...), AIProjectClient(...)
```

#### Session State Management
```python
# Initialize session state efficiently
if 'assessment_scores' not in st.session_state:
    st.session_state.assessment_scores = {}

# Clear session state for new assessment
if st.button("Reset Assessment"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()
```

## 🔒 Security Best Practices

### Credential Management
- Use Azure Key Vault for production secrets
- Never commit API keys to version control
- Implement credential rotation policies
- Use managed identities when possible

### Data Privacy
- No persistent user data storage
- Session-only data retention
- Secure Azure API communication
- Audit trail via telemetry

### Access Control
```python
# Example: Role-based access control
def check_user_permissions():
    # Implement your authorization logic
    if not user_has_assessment_access():
        st.error("Access denied")
        st.stop()
```

## 📈 Performance Benchmarks

### Expected Performance Characteristics

| Operation | Local Development | Azure App Service | Azure Container |
|-----------|------------------|-------------------|-----------------|
| **App Startup** | 2-3 seconds | 5-10 seconds | 3-5 seconds |
| **Form Rendering** | < 1 second | 1-2 seconds | < 1 second |
| **Score Calculation** | < 0.5 seconds | < 1 second | < 0.5 seconds |
| **AI Recommendation** | 3-8 seconds | 4-10 seconds | 3-8 seconds |
| **Concurrent Users** | 1 | 10-50 | 5-20 |

### Scaling Considerations
- **Memory Usage**: ~200MB baseline + 50MB per concurrent user
- **CPU Usage**: Low except during AI recommendation calls
- **Network**: Dependent on Azure OpenAI API latency
- **Storage**: Minimal (configuration files only)

---

*This quick reference provides essential information for developers working with the AI Maturity Assessment Tool, covering setup, configuration, core functions, and troubleshooting guidance.*