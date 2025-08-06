# Dapr Jobs Lab: Scheduling Future Agent Actions

<br>

> **⚠️ Important Advisory: Dapr Jobs API is in Alpha**
>
> The Dapr Jobs API (`v1.0-alpha1`) demonstrated in this lab is currently in **Alpha**. This means:
>
> - **Subject to Change**: The API, its behavior, and its features may change significantly in future Dapr releases.
> - **Not Recommended for Production**: Due to its alpha status, it is **not recommended to use the Dapr Jobs API in production environments** until it graduates to a stable version.
> - **Observed Behavior**: As seen in this lab, the alpha version may have behaviors (like the specific endpoint it calls when a job triggers - `/job/<job_name>`) that might differ from final documentation or intuitive expectations.
>
> **Production Alternatives for Scheduled Tasks**:
> For production needs requiring scheduled or cron-like execution, consider these more mature alternatives:
>
> - **Kubernetes CronJobs**: If deploying in Kubernetes, `CronJob` is a robust, battle-tested way to schedule batch tasks. Your job container could be a Dapr-enabled application that performs the required action.
> - **System Cron (e.g., Linux `cron`)**: For simpler, single-instance schedulers, system-level cron can trigger scripts or application endpoints.
> - **In-Application Scheduling Libraries**: For applications that manage their own scheduling (and don't require the distributed nature or Dapr integration for scheduling itself), libraries like `APScheduler` (Python), Quartz.NET (.NET), etc., can be used. However, ensure your application is designed for resilience if it becomes a single point of failure for scheduling.
> - **Cloud Provider Scheduled Functions/Tasks**: Services like AWS Lambda Scheduled Events, Azure Functions Timer Trigger, or Google Cloud Scheduler offer managed serverless scheduling.

<br>

**Goal**: This lab demonstrates how to use Dapr\'s Jobs building block (currently in Alpha) to schedule and trigger future actions programmatically. We will focus on how this capability can be leveraged by AI agents or Dapr Actors within an agentic system (like DACA) to manage tasks that need to occur at specific future times or intervals, similar to a calendar or reminder system.

-> The jobs API is currently in alpha and subject to change.

---

## 1. Introduction to Dapr Jobs

Many applications, especially complex agentic systems, require tasks to be performed at a later time or on a recurring basis. Dapr Jobs provide a robust solution for this by offering a way to schedule work without implementing and managing a complex scheduler yourself.

**Key Components & Features**:

- **Jobs API Building Block**: An API (currently `v1.0-alpha1`) provided by the Dapr sidecar to manage (create, get, delete) jobs programmatically via HTTP.
- **Scheduler Control Plane Service**: A Dapr system service responsible for storing job definitions, tracking schedules, and ensuring jobs are triggered at their due times. In self-hosted mode, this service is typically run automatically when Dapr is initialized.
- **At-Least-Once Execution**: Dapr Jobs guarantee that a job will be invoked at least once _after_ its scheduled time is due.
- **Persistent Storage**: Job details are stored by the Scheduler service.
- **Primary Use Cases**:
  - **Scheduled Service Invocation**: Triggering an HTTP/gRPC endpoint on a Dapr-enabled application at a specific time or interval. This is the focus of our lab.
  - **Delayed Pub/Sub Messaging**: Publishing a message to a topic at a future time.
- **Idempotent Creation/Updates**: When a job is created via the API (`POST /v1.0-alpha1/jobs/<job-name>`), if a job with the same name already exists, its definition is updated.

**Dapr Jobs vs. Dapr Actor Reminders**:

- **Actor Reminders**: Simpler, for Dapr Actors to schedule callbacks _to themselves_. Good for actor-specific state-based timers.
- **Dapr Jobs**: More general. Can target _any_ Dapr app/method, support CRON schedules, and are managed via a distinct API. Excellent for broader, inter-service scheduled tasks or when an agent needs to ensure an action happens irrespective of its own immediate activation state.

For agentic systems, while actors might use reminders for internal state-based timers, Dapr Jobs are excellent for scheduling broader, inter-service tasks, or when an agent needs to ensure an action happens irrespective of its own activation state at that exact future moment.

---

## 2. Dapr Jobs in Agentic Systems (DACA Context)

In the Dapr Agentic Cloud Ascent (DACA) paradigm, where we envision scalable and resilient AI agents, the ability to schedule future work is crucial. Agents often operate on timelines, needing to:

- **Perform follow-up actions**: An agent might interact with a user or another system and determine a follow-up is needed in X hours or on a specific date.
- **Execute periodic tasks**: An agent could be responsible for daily data aggregation, weekly report generation, or hourly checks on external systems.
- **Manage long-running processes with delays**: A complex workflow orchestrated by an agent might involve steps separated by defined waiting periods.
- **Simulate calendar-like events**: An agent could be tasked with triggering notifications or actions based on a scheduled event, like reminding a user before a meeting.

Dapr Jobs provide a Dapr-native, resilient, and scalable solution for these needs:

- **Offloading Complexity**: Agents don\'t need to implement their own robust scheduling logic, manage timers across activations, or deal with scheduler persistence. They can delegate this to Dapr.
- **Resilience**: Dapr\'s Scheduler ensures that if an agent (or the service hosting it) is temporarily down when a job is due, the job can still be picked up and executed once the target is available (depending on retry configurations at the service invocation level).
- **Decoupling**: The agent logic for _deciding_ a task needs to be scheduled is separate from the Dapr mechanism that _executes_ the scheduling.
- **Interoperability**: A job scheduled by one agent (or service) can target another agent or service, facilitating complex, time-based orchestrations.

**Example Scenario in DACA**:
Imagine a "Project Management Agent" built using Dapr Actors. When a user assigns a task with a future due date, the agent actor could:

1.  Store the task details.
2.  Create a Dapr Job scheduled to run shortly before the due date.
3.  The job\'s target could be a method on the Project Management Agent itself (e.g., `triggerTaskDueNotification`) or a separate notification service.
    This way, the agent ensures timely reminders or escalations without maintaining active timers over potentially long periods.

---

## 3. Lab: Programmatically Scheduling Service Calls with Dapr Jobs

This lab demonstrates how an application can use Dapr\'s HTTP API to create, monitor, and delete jobs that trigger its own endpoints.

**Lab Scenario Overview**:

1.  **`TaskExecutorService` (`main.py`)**: A FastAPI application with:
    - An HTTP POST endpoint (`/executeScheduledTask`) that logs when called by a Dapr Job.
    - Endpoints to programmatically manage Dapr Jobs:
      - `POST /programmatic/schedule-task`: Creates/updates a Dapr job targeting `/executeScheduledTask`.
      - `GET /programmatic/task-status/{job_name}`: Retrieves a job\'s status.
      - `DELETE /programmatic/delete-task/{job_name}`: Deletes a job.
2.  **Execution**: We will run `main.py` with its Dapr sidecar. Then, using `curl` or a browser, we will call the `/programmatic/schedule-task` endpoint to create a job. We\'ll observe the service logs to see the `/executeScheduledTask` endpoint being called by Dapr based on the schedule, and then use the other programmatic endpoints to manage the job.

**Prerequisites**:

- Python 3.8+ and `uv`.
- Dapr CLI installed and initialized (`dapr init`).
- Docker installed and running.

---

### Implementation Steps

#### Step 1: Review the Code

Familiarize yourself with `03_jobs/jobs_lab/main.py`. It contains:

- The `TaskExecutorService` FastAPI application.
- The `/executeScheduledTask` endpoint (the target for our jobs).
- The `/programmatic/*` endpoints that use `httpx` to call the Dapr Jobs API (`/v1.0-alpha1/jobs/...`) on the application\'s own Dapr sidecar.

Key aspects of programmatic job creation in `main.py` (`/programmatic/schedule-task`):

- It constructs a JSON payload for the job (specifying `schedule`, `target.appId`, `target.method`, `data`, etc.).
- It POSTs this payload to `http://localhost:<DAPR_HTTP_PORT>/v1.0-alpha1/jobs/<job_name>`.
- The `target.appId` is set to `APP_ID` (this application\'s own Dapr ID), so the job calls back into itself.

#### Step 2: Running the `TaskExecutorService` with Dapr

Navigate to the `03_jobs/jobs_lab` directory.
Run the `main.py` service with Dapr:

```bash
tilt up
```

You should see logs from Dapr and your FastAPI app starting up.

#### Step 3: Programmatically Scheduling and Managing a Job

Open a new terminal. You can use `curl` to interact with the `/programmatic/*` endpoints of your running service (which listens on port `8002`).

1.  **Schedule a Task (Create a Dapr Job)**:
    Let\'s create a job named `myFirstProgrammaticJob` that runs every 20 seconds and sends custom data.

    ```bash
    curl -X POST \
      -H \"Content-Type: application/json\" \
      -d '{}' \
      \"http://localhost:8002/programmatic/schedule-task?job_name=myFirstProgrammaticJob&schedule=@every 20s\"
    ```

    (For POST with query parameters and empty body, or include `task_data` in the URL if GET, or send as JSON body for POST if you modify the endpoint to accept it.)

    _Simplified for GET request if `schedule_new_task` accepted GET, or using default task_data for POST:_
    Let\'s refine the call to explicitly send JSON data for `task_data` as the endpoint expects it for the POST request if not using defaults.

    Since `schedule_new_task` expects `task_data: dict` in its signature, let\'s assume we want to POST that data. If `task_data` is a query parameter in FastAPI, it needs to be a Pydantic model or passed in the body for POST.
    The current signature `async def schedule_new_task(job_name: str, schedule: str = \"@every 1m\", repeats: int = 0, task_data: dict = None)` means FastAPI will look for `job_name`, `schedule`, `repeats` as query parameters for a POST if not in body, and `task_data` would ideally be in the POST body.

    Let\'s make the `curl` call cleaner for POSTing `task_data` (assuming `main.py` handles `task_data` from POST body, which it will if we type hint it as a Pydantic model or `Body(...)`):

    _Assuming `main.py` is updated to take `task_data` from POST body, or we rely on its default if not provided._
    If `task_data` in `schedule_new_task` is meant to be part of the Dapr job\'s payload (which it is), and we want to specify this `task_data` when calling `/programmatic/schedule-task`, we should ideally POST a JSON body to `/programmatic/schedule-task` itself.

    Let\'s adjust the `schedule_new_task` in `main.py` to accept `task_data` from the request body. (This change will be done in the next step if needed, for now, let\'s use query params for simplicity for `job_name` and `schedule` and rely on default internal `task_data`).

    **Corrected `curl` for current `main.py` (using query params for job_name and schedule, default internal task_data):**

    ```bash
    curl -X POST \"http://localhost:8002/programmatic/schedule-task?job_name=myProgJob1&schedule=@every 20s\"
    ```

    You should get a JSON response like: `{"status":"Job scheduled/updated","job_name":"myProgJob1",...}`.

2.  **Observe Logs**:
    In the terminal where `dapr run ... python main.py` is executing, watch the logs. Every 20 seconds, you should see:

    ```
    INFO:jobs_lab.main:[YYYY-MM-DDTHH:MM:SS.mmmmmm] Received call to /executeScheduledTask by Dapr Job.
    INFO:jobs_lab.main:Received JSON data: {\'message\': \'Programmatically scheduled!\', \'source\': \'myProgJob1\'}
    ```

3.  **Get Job Status**:

    ```bash
    curl \"http://localhost:8002/programmatic/task-status/myProgJob1\"
    ```

    This will return a JSON object with details about the job, including its schedule, last execution, etc.

4.  **Delete the Job**:
    ```bash
    curl -X DELETE \"http://localhost:8002/programmatic/delete-task/myProgJob1\"
    ```
    You should get a success response. After this, the logs in the service terminal should stop showing new executions for `myProgJob1`.

---

## 4. Understanding Programmatic Job Creation by Agents

The `/programmatic/schedule-task` endpoint in `main.py` is a direct example of how an agent (or any Dapr-enabled service) would schedule a Dapr Job:

1.  **Construct Payload**: The agent logic determines the job details (target app, method, schedule, data).
2.  **HTTP POST to Sidecar**: It makes an HTTP POST request to its _own_ Dapr sidecar\'s endpoint: `http://localhost:<DAPR_HTTP_PORT>/v1.0-alpha1/jobs/<job-name>`. The body of this POST is the JSON job specification (as seen in the `job_payload` in `main.py`).

**Key Considerations for Agents**:

- **Dynamic Schedules**: Agents can compute exact future timestamps (ISO 8601 format, e.g., `YYYY-MM-DDTHH:MM:SSZ`) for the `schedule` field for one-time execution (also provide `repeats: 1` in the job payload sent to Dapr).
- **Targeting Self or Others**: The `target.appId` in the job payload can be the agent\'s own `app-id` (for self-reminders/tasks) or the `app-id` of another service.
- **Job Naming & Idempotency**: Use unique, meaningful job names. If an agent POSTs to the same job name, Dapr updates the existing job.
- **Error Handling**: Agent logic must handle potential errors from the Dapr API call (e.g., network issues, malformed requests).

---

## 5. Key Dapr Concepts Covered

- **Dapr Jobs API (v1.0-alpha1)**: Programmatic interaction via HTTP to manage scheduled tasks.
- **Dapr Scheduler Service**: The Dapr component handling job storage and triggering.
- **Job Specification (JSON)**: Structure for `schedule`, `target`, `data`, `repeats`.
- **Service Invocation by Job**: How a job triggers an HTTP endpoint on a Dapr application.
- **Agent-driven Scheduling**: The core concept of an application dynamically creating and managing its own scheduled tasks via its Dapr sidecar.

---

## 6. Important Reading Resources

- **Dapr Jobs API Reference (v1.0-alpha1)**: (Refer to the specific alpha API docs if available, generally linked from the main Jobs overview) Look for `POST /v1.0-alpha1/jobs/{jobName}`.
- **Dapr Jobs Overview**: [https://docs.dapr.io/developing-applications/building-blocks/jobs/jobs-overview/](https://docs.dapr.io/developing-applications/building-blocks/jobs/jobs-overview/)
- **How-To: Schedule Jobs using Dapr**: [https://docs.dapr.io/developing-applications/building-blocks/jobs/howto-schedule-jobs/](https://docs.dapr.io/developing-applications/building-blocks/jobs/howto-schedule-jobs/) (This page might show CLI/YAML, adapt understanding for API calls).

This lab provides a practical way to understand Dapr Jobs, especially how they can be integrated into applications for dynamic, agent-driven task scheduling.
