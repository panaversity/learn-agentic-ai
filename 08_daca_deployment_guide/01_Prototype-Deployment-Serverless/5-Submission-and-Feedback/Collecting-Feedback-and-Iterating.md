# Collecting Feedback and Iterating Guide

## Objective
This guide provides a structured approach to collecting, analyzing, and acting on feedback for prototype deployments, ensuring continuous improvement and alignment with user needs.

## Prerequisites
- Deployed prototype application
- Feedback collection system
- Access to application metrics
- Basic understanding of user research methods

## Step-by-Step Instructions

### 1. Set Up Feedback Collection System

#### 1.1 Create Feedback Database Schema
```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    rating INTEGER,
    comments TEXT,
    feature VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'new'
);

CREATE TABLE feedback_actions (
    id SERIAL PRIMARY KEY,
    feedback_id INTEGER REFERENCES feedback(id),
    action_taken TEXT,
    status VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 1.2 Implement Feedback API
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI()

class Feedback(BaseModel):
    user_id: str
    rating: int
    comments: str
    feature: str

class FeedbackAction(BaseModel):
    feedback_id: int
    action_taken: str
    status: str

@app.post("/api/v1/feedback")
async def submit_feedback(feedback: Feedback):
    try:
        # Store feedback in database
        # ...
        return {"status": "success", "message": "Feedback received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/feedback/action")
async def log_action(action: FeedbackAction):
    try:
        # Log action taken
        # ...
        return {"status": "success", "message": "Action logged"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Create Feedback Analysis Dashboard

#### 2.1 Set Up Analytics
```python
from fastapi import FastAPI
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/api/v1/feedback/analytics")
async def get_analytics():
    # Get feedback data
    feedback_data = pd.DataFrame([
        {"rating": 4, "feature": "UI", "timestamp": datetime.now()},
        {"rating": 5, "feature": "Performance", "timestamp": datetime.now()}
    ])
    
    # Calculate metrics
    metrics = {
        "average_rating": feedback_data["rating"].mean(),
        "total_feedback": len(feedback_data),
        "feature_ratings": feedback_data.groupby("feature")["rating"].mean().to_dict()
    }
    
    return metrics

@app.get("/api/v1/feedback/trends")
async def get_trends():
    # Get time-series data
    # ...
    return {"trends": "data"}
```

#### 2.2 Create Visualization
```python
def create_feedback_visualization(feedback_data):
    # Create rating distribution
    fig1 = px.histogram(feedback_data, x="rating", title="Rating Distribution")
    
    # Create feature ratings
    fig2 = px.bar(
        feedback_data.groupby("feature")["rating"].mean().reset_index(),
        x="feature",
        y="rating",
        title="Feature Ratings"
    )
    
    return fig1.to_json(), fig2.to_json()
```

### 3. Implement Feedback Processing Workflow

#### 3.1 Create Feedback Processing Script
```python
from typing import List, Dict
import pandas as pd
from datetime import datetime

class FeedbackProcessor:
    def __init__(self):
        self.feedback_data = pd.DataFrame()
    
    def load_feedback(self, data: List[Dict]):
        self.feedback_data = pd.DataFrame(data)
    
    def analyze_feedback(self):
        analysis = {
            "total_feedback": len(self.feedback_data),
            "average_rating": self.feedback_data["rating"].mean(),
            "feature_analysis": self.feedback_data.groupby("feature").agg({
                "rating": ["mean", "count"],
                "comments": "count"
            }).to_dict()
        }
        return analysis
    
    def identify_trends(self):
        # Implement trend analysis
        pass
    
    def generate_report(self):
        analysis = self.analyze_feedback()
        return {
            "summary": analysis,
            "recommendations": self.generate_recommendations(analysis)
        }
    
    def generate_recommendations(self, analysis: Dict):
        # Implement recommendation logic
        pass
```

### 4. Create Iteration Planning Template

Create `iteration-plan.md`:

```markdown
# Iteration Plan

## Feedback Summary
- Total feedback received: [number]
- Average rating: [rating]
- Key themes: [list]

## Priority Areas
1. [High priority item]
   - Feedback count: [number]
   - Impact: [description]
   - Proposed solution: [description]

2. [Medium priority item]
   - Feedback count: [number]
   - Impact: [description]
   - Proposed solution: [description]

## Action Items
- [ ] Implement [feature]
- [ ] Fix [issue]
- [ ] Improve [aspect]

## Timeline
- Start date: [date]
- End date: [date]
- Milestones: [list]

## Success Metrics
- [Metric 1]: [target]
- [Metric 2]: [target]
```

## Validation

### 1. Test Feedback Collection
```bash
# Submit test feedback
curl -X POST https://your-app.azurecontainerapps.io/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "rating": 5, "comments": "Great!", "feature": "UI"}'

# Check feedback storage
curl -X GET https://your-app.azurecontainerapps.io/api/v1/feedback/analytics
```

### 2. Monitor Feedback Processing
```bash
# Check processing status
curl -X GET https://your-app.azurecontainerapps.io/api/v1/feedback/status

# View analytics
curl -X GET https://your-app.azurecontainerapps.io/api/v1/feedback/trends
```

## Common Issues and Solutions

### Issue 1: Low Feedback Response
- **Solution**: Implement incentives and reminders
- **Prevention**: Make feedback collection easy and visible

### Issue 2: Unclear Feedback
- **Solution**: Provide structured feedback forms
- **Prevention**: Guide users with specific questions

### Issue 3: Slow Iteration Cycle
- **Solution**: Automate feedback processing
- **Prevention**: Set clear iteration timelines

## Best Practices

### 1. Feedback Collection
- Make it easy to provide feedback
- Use multiple collection methods
- Provide incentives
- Regular reminders
- Clear instructions

### 2. Analysis
- Regular review cycles
- Quantitative and qualitative analysis
- Trend identification
- Priority setting
- Action planning

### 3. Implementation
- Clear iteration goals
- Measurable outcomes
- Regular updates
- User communication
- Progress tracking

## Next Steps
- Implement feedback collection (see Prototype-URL-Sharing.md)
- Set up monitoring
- Plan next iteration 