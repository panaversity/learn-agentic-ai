# Tutorial: Working with Azure Container Apps (ACA) and Jobs

Azure Container Apps (ACA) is a fully managed serverless platform that enables you to run containerized applications and jobs without managing underlying infrastructure. Jobs in ACA allow you to execute containerized tasks that run for a finite duration and then exit, making them ideal for tasks like data processing, batch workloads, or event-driven operations. In this tutorial, you’ll learn how to:

1. Set up an Azure Container Apps environment.
2. Create and run a manual job.
3. Create and schedule a recurring job.
4. Create an event-driven job triggered by an Azure Storage Queue.
5. Monitor job executions using Azure Log Analytics.

Let’s get started!

---

## Prerequisites

- **Azure Account**: An active Azure subscription. If you don’t have one, create a free account at [azure.microsoft.com](https://azure.microsoft.com).
- **Azure CLI**: Installed and updated to the latest version. Install it from [here](https://learn.microsoft.com/cli/azure/install-azure-cli) if needed.
- **Docker**: Optional, for building custom container images locally (not required for this tutorial as we’ll use a public image).
- **Basic Command-Line Knowledge**: Familiarity with running commands in a terminal.

---

## Step 1: Set Up Your Environment

### 1.1 Install the Azure Container Apps CLI Extension
Ensure you have the latest Azure CLI and the Container Apps extension installed. Run these commands to update and install:

```bash
az upgrade
az extension add --name containerapp --upgrade
```

### 1.2 Sign In to Azure
Log in to your Azure account:

```bash
az login
```

Follow the prompts to authenticate.

### 1.3 Register Required Resource Providers
Register the necessary namespaces for Container Apps and Log Analytics:

```bash
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
```

### 1.4 Set Up Environment Variables
Define variables to simplify commands throughout the tutorial. Replace `<your-unique-name>` with a unique string (e.g., your initials and a number):

```bash
RESOURCE_GROUP="aca-jobs-tutorial"
LOCATION="eastus"
ENVIRONMENT="aca-env"
JOB_NAME_MANUAL="manual-job"
JOB_NAME_SCHEDULED="scheduled-job"
JOB_NAME_EVENT="event-job"
STORAGE_ACCOUNT="acastorage<your-unique-name>"
QUEUE_NAME="job-queue"
```

### 1.5 Create a Resource Group
Create a resource group to hold all resources:

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### 1.6 Create a Container Apps Environment
The environment is a secure boundary for your apps and jobs. It includes a Log Analytics workspace for logging by default:

```bash
az containerapp env create \
  --name $ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

Wait a few minutes for the environment to be provisioned.

---

## Step 2: Create and Run a Manual Job

A manual job is triggered on-demand. We’ll use a public sample image that prints a message and exits.

### 2.1 Create the Manual Job
Run this command to create a manual job:

```bash
az containerapp job create \
  --name $JOB_NAME_MANUAL \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --trigger-type Manual \
  --replica-timeout 300 \
  --replica-retry-limit 1 \
  --replica-completion-count 1 \
  --parallelism 1 \
  --image "mcr.microsoft.com/k8se/quickstart-jobs:latest"
```

- **`trigger-type Manual`**: Specifies this is a manual job.
- **`replica-timeout`**: Maximum runtime (in seconds) before termination (300 seconds = 5 minutes).
- **`replica-retry-limit`**: Number of retries if the job fails (1 in this case).
- **`replica-completion-count`**: Number of replicas that must complete successfully (1).
- **`parallelism`**: Number of replicas to run in parallel (1).
- **`image`**: A sample image that waits, prints a message, and exits.

### 2.2 Start the Manual Job
Trigger an execution of the job:

```bash
az containerapp job start \
  --name $JOB_NAME_MANUAL \
  --resource-group $RESOURCE_GROUP
```

This command initiates a single job execution. Note the execution name returned in the output (e.g., `manual-job--abc123`).

### 2.3 Check Execution Status
List recent executions to verify the job ran:

```bash
az containerapp job execution list \
  --name $JOB_NAME_MANUAL \
  --resource-group $RESOURCE_GROUP \
  --output table
```

Look for a `Succeeded` status.

---

## Step 3: Create and Schedule a Recurring Job

A scheduled job runs on a defined cron schedule. We’ll set it to run every 5 minutes.

### 3.1 Create the Scheduled Job
Use this command to create a scheduled job:

```bash
az containerapp job create \
  --name $JOB_NAME_SCHEDULED \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --trigger-type Schedule \
  --cron-expression "*/5 * * * *" \
  --replica-timeout 300 \
  --replica-retry-limit 1 \
  --replica-completion-count 1 \
  --parallelism 1 \
  --image "mcr.microsoft.com/k8se/quickstart-jobs:latest"
```

- **`trigger-type Schedule`**: Specifies a scheduled job.
- **`cron-expression "*/5 * * * *"`**: Runs every 5 minutes (UTC).

### 3.2 Verify Scheduled Executions
Wait a few minutes, then check the execution history:

```bash
az containerapp job execution list \
  --name $JOB_NAME_SCHEDULED \
  --resource-group $RESOURCE_GROUP \
  --output table
```

You should see executions starting every 5 minutes with a `Succeeded` status.

---

## Step 4: Create an Event-Driven Job

An event-driven job triggers based on events, such as a message arriving in an Azure Storage Queue. We’ll set up a queue and configure a job to process messages.

### 4.1 Create a Storage Account and Queue
Create a storage account:

```bash
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS
```

Get the storage account key:

```bash
STORAGE_KEY=$(az storage account keys list \
  --account-name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query "[0].value" --output tsv)
```

Create a queue:

```bash
az storage queue create \
  --name $QUEUE_NAME \
  --account-name $STORAGE_ACCOUNT \
  --account-key $STORAGE_KEY
```

### 4.2 Create the Event-Driven Job
For simplicity, we’ll use the same sample image, but in practice, you’d use a custom image to process queue messages. Create the job:

```bash
az containerapp job create \
  --name $JOB_NAME_EVENT \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --trigger-type Event \
  --replica-timeout 300 \
  --replica-retry-limit 1 \
  --replica-completion-count 1 \
  --parallelism 1 \
  --min-executions 0 \
  --max-executions 10 \
  --polling-interval 30 \
  --scale-rule-name "queue-rule" \
  --scale-rule-type "azure-queue" \
  --scale-rule-metadata "queueName=$QUEUE_NAME" "queueLength=1" "accountName=$STORAGE_ACCOUNT" \
  --scale-rule-auth "connection=conn-string" \
  --secrets "conn-string=DefaultEndpointsProtocol=https;AccountName=$STORAGE_ACCOUNT;AccountKey=$STORAGE_KEY;EndpointSuffix=core.windows.net" \
  --image "mcr.microsoft.com/k8se/quickstart-jobs:latest"
```

- **`trigger-type Event`**: Specifies an event-driven job.
- **`min-executions`/`max-executions`**: Controls scaling (0 to 10 executions).
- **`polling-interval`**: Checks the queue every 30 seconds.
- **`scale-rule-type "azure-queue"`**: Scales based on queue length.
- **`scale-rule-metadata`**: Specifies the queue and trigger condition (1 message).
- **`secrets`**: Stores the connection string securely.

### 4.3 Add a Message to the Queue
Trigger the job by adding a message:

```bash
az storage message put \
  --queue-name $QUEUE_NAME \
  --content "Trigger job execution" \
  --account-name $STORAGE_ACCOUNT \
  --account-key $STORAGE_KEY
```

### 4.4 Verify Event-Driven Execution
Check the execution history:

```bash
az containerapp job execution list \
  --name $JOB_NAME_EVENT \
  --resource-group $RESOURCE_GROUP \
  --output table
```

You should see an execution triggered by the queue message.

---

## Step 5: Monitor Job Executions

Jobs log output to Azure Log Analytics by default. Let’s retrieve logs for the manual job.

### 5.1 Get Log Analytics Workspace ID
Retrieve the workspace ID:

```bash
LOG_ANALYTICS_WORKSPACE_ID=$(az containerapp env show \
  --name $ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --query "properties.appLogsConfiguration.logAnalyticsConfiguration.customerId" \
  --output tsv)
```

### 5.2 Get the Latest Execution Name
Find the most recent execution of the manual job:

```bash
JOB_EXECUTION_NAME=$(az containerapp job execution list \
  --name $JOB_NAME_MANUAL \
  --resource-group $RESOURCE_GROUP \
  --query "[0].name" \
  --output tsv)
```

### 5.3 Query Logs
Run a query to view logs:

```bash
az monitor log-analytics query \
  --workspace $LOG_ANALYTICS_WORKSPACE_ID \
  --analytics-query "ContainerAppConsoleLogs_CL | where ContainerGroupName_s startswith '$JOB_EXECUTION_NAME' | order by _timestamp_d asc" \
  --query "[].Log_s" \
  --output table
```

You should see output like:
```
"This is a sample application that demonstrates how to use Azure Container Apps jobs"
"Starting processing..."
"Finished processing. Shutting down!"
```

Repeat this process for the scheduled and event-driven jobs by replacing `$JOB_NAME_MANUAL` with the respective job name.

---

## Step 6: Clean Up Resources

When you’re done, delete the resource group to avoid incurring charges:

```bash
az group delete --name $RESOURCE_GROUP --yes
```

---

## Conclusion

In this tutorial, you’ve learned how to:
- Set up an Azure Container Apps environment.
- Create and trigger a manual job.
- Schedule a recurring job using a cron expression.
- Build an event-driven job triggered by an Azure Storage Queue.
- Monitor job executions using Log Analytics.

Azure Container Apps Jobs are powerful for running finite tasks in a serverless environment. You can extend this further by using custom container images tailored to your specific workloads, integrating with other Azure services, or exploring advanced configurations like Dapr or KEDA scaling rules.

Happy coding! Let me know if you’d like to dive deeper into any specific aspect.