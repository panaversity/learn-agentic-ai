# Prototype URL Sharing Guide

## Objective
This guide provides instructions for securely sharing and managing access to prototype deployments in Azure Container Apps, including best practices for access control and feedback collection.

## Prerequisites
- Azure Container Apps deployment
- Application URL
- Azure AD tenant
- Basic understanding of Azure security concepts

## Step-by-Step Instructions

### 1. Configure Access Control

#### 1.1 Set Up Azure AD Authentication
```bash
# Enable Azure AD authentication
az containerapp update \
  --name your-app \
  --resource-group your-resource-group \
  --enable-ingress true \
  --target-port 80 \
  --ingress external \
  --auth-enabled true \
  --auth-provider azure-active-directory
```

#### 1.2 Configure Access Restrictions
```bash
# Add IP restrictions
az containerapp update \
  --name your-app \
  --resource-group your-resource-group \
  --ingress-configuration '{
    "external": true,
    "targetPort": 80,
    "allowInsecure": false,
    "ipSecurityRestrictions": [
      {
        "name": "Allow specific IP",
        "ipAddress": "1.2.3.4/32",
        "action": "Allow"
      }
    ]
  }'
```

### 2. Create Access Management Script

Create `manage-access.sh`:

```bash
#!/bin/bash

# Set variables
APP_NAME="your-app"
RESOURCE_GROUP="your-resource-group"
USER_EMAIL="user@example.com"

# Function to add user access
add_user_access() {
  local email=$1
  local role=$2
  
  # Get user object ID
  USER_ID=$(az ad user show --id $email --query id -o tsv)
  
  # Assign role
  az role assignment create \
    --assignee $USER_ID \
    --role $role \
    --scope "/subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$APP_NAME"
}

# Function to remove user access
remove_user_access() {
  local email=$1
  
  # Get user object ID
  USER_ID=$(az ad user show --id $email --query id -o tsv)
  
  # Remove role assignment
  az role assignment delete \
    --assignee $USER_ID \
    --scope "/subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$APP_NAME"
}

# Example usage
# add_user_access $USER_EMAIL "Reader"
# remove_user_access $USER_EMAIL
```

### 3. Create Feedback Collection System

#### 3.1 Set Up Feedback Endpoint
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

app = FastAPI()

class Feedback(BaseModel):
    user_id: str
    rating: int
    comments: str
    feature: str

@app.post("/api/v1/feedback")
async def submit_feedback(feedback: Feedback):
    try:
        # Log feedback
        logging.info(f"Feedback received: {feedback.dict()}")
        
        # Store feedback (implement your storage solution)
        # ...
        
        return {"status": "success", "message": "Feedback received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 3.2 Create Feedback Dashboard
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import pandas as pd
import plotly.express as px

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/v1/feedback/stats")
async def get_feedback_stats():
    # Get feedback data (implement your data retrieval)
    feedback_data = pd.DataFrame([
        {"rating": 4, "feature": "UI"},
        {"rating": 5, "feature": "Performance"}
    ])
    
    # Create visualization
    fig = px.bar(feedback_data, x="feature", y="rating")
    return fig.to_json()
```

### 4. Share Application URL

Create `share-url.md`:

```markdown
# Prototype Access Instructions

## Application URL
https://your-app.azurecontainerapps.io

## Access Instructions
1. Click the application URL
2. Sign in with your Azure AD account
3. Accept the terms of service
4. Start using the application

## Feedback
Please provide feedback through:
- In-app feedback form
- Email: feedback@example.com
- Slack channel: #prototype-feedback

## Support
For technical issues:
- Email: support@example.com
- Documentation: [link to docs]
```

## Validation

### 1. Test Access Control
```bash
# Verify Azure AD authentication
curl -I https://your-app.azurecontainerapps.io

# Check IP restrictions
az containerapp show \
  --name your-app \
  --resource-group your-resource-group \
  --query "properties.configuration.ingress.ipSecurityRestrictions"
```

### 2. Test Feedback System
```bash
# Submit test feedback
curl -X POST https://your-app.azurecontainerapps.io/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "rating": 5, "comments": "Great!", "feature": "UI"}'
```

### 3. Monitor Access
```bash
# Check access logs
az monitor activity-log list \
  --resource-group your-resource-group \
  --resource-type Microsoft.App/containerApps \
  --resource your-app
```

## Common Issues and Solutions

### Issue 1: Access Denied
- **Solution**: Verify user permissions and IP restrictions
- **Prevention**: Regular access reviews

### Issue 2: Authentication Problems
- **Solution**: Check Azure AD configuration
- **Prevention**: Test authentication flow

### Issue 3: Feedback Collection Issues
- **Solution**: Monitor feedback endpoint
- **Prevention**: Implement proper error handling

## Best Practices

### 1. Security
- Use Azure AD authentication
- Implement IP restrictions
- Regular access reviews
- Monitor access patterns
- Use least privilege principle

### 2. Access Management
- Document access procedures
- Regular access audits
- Clear access revocation
- Role-based access control
- Temporary access for testing

### 3. Feedback Collection
- Easy feedback submission
- Structured feedback format
- Regular feedback review
- Action on feedback
- Feedback tracking

## Next Steps
- Collect feedback (see Collecting-Feedback-and-Iterating.md)
- Implement monitoring
- Plan next iteration 