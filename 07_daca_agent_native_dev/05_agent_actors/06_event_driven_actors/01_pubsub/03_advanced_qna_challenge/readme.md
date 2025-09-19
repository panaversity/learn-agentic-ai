# Advanced Challenge Guide: Q&A Personalized Learning System

This guide provides the detailed step-by-step instructions for implementing the advanced challenge described in the main `readme.md` for the Pub/Sub module.

**Goal**: Build a multi-service DACA application simulating a personalized learning system where student Q&A interactions trigger analysis and potential teacher support, all orchestrated via Dapr pub/sub and actors.

**Scenario Overview**:

1.  `StudentInteractionService`: Presents questions, receives answers, publishes results.
2.  `MemoryService`: Subscribes to answers, stores history in `StudentMemoryActor` state.
3.  `LearningAnalyticsService`: Subscribes to answers, analyzes performance in `StudentAnalyticsActor`, publishes alerts if student struggles.
4.  `TeacherSupportService`: Subscribes to alerts, simulates teacher action in `TeacherSupportAgentActor`.

**System Overview**: This challenge involves creating four distinct microservices, each running in its own Kubernetes Pod (with a Dapr sidecar), and each hosting at least one primary Dapr Actor representing an AI agent function:

1.  **`StudentInteractionService`** (`student-interaction-app`):
    - **Pods**: 1 (+ Dapr sidecar)
    - **Primary Agent Actor**: `InteractionHandlerActor` (Handles incoming answers, publishes events).
    - **Role**: User-facing API and initial event publisher.
2.  **`MemoryService`** (`memory-app`):
    - **Pods**: 1 (+ Dapr sidecar)
    - **Primary Agent Actor**: `StudentMemoryActor` (Subscribes to answers, stores history in state).
    - **Role**: Persistent storage of student interaction history.
3.  **`LearningAnalyticsService`** (`learning-analytics-app`):
    - **Pods**: 1 (+ Dapr sidecar)
    - **Primary Agent Actor**: `StudentAnalyticsActor` (Subscribes to answers, analyzes for patterns, publishes alerts).
    - **Role**: Real-time analysis and identification of students needing assistance.
4.  **`TeacherSupportService`** (`teacher-support-app`):
    - **Pods**: 1 (+ Dapr sidecar)
    - **Primary Agent Actor**: `TeacherSupportAgentActor` (Subscribes to assistance alerts, simulates teacher response).
    - **Role**: Responding to alerts and simulating intervention.

**Total**: 4 AI Apps / 4 Application Pods / 4 Primary Agent Actor types.

**Mermaid Diagram:**

```mermaid
%%{init: {'theme': 'dark', 'themeVariables': { 'darkMode': true, 'primaryColor': '#333', 'primaryTextColor': '#fff', 'primaryBorderColor': '#555', 'lineColor': '#d3d3d3', 'textColor': '#111' }}}%%
graph TD
    subgraph StudentInteractionService["StudentInteractionService (student-interaction-app)"]
        A[User/Student] --> B(FastAPI: Get Question)
        B --> A
        A --> C(FastAPI: Submit Answer)
        C --> D[InteractionHandlerActor]
        D -- Evaluate Answer & Publish student_answer_processed_event --> E[(student-activity-topic)]
    end

    subgraph MemoryService["MemoryService (memory-app)"]
        E --> F[StudentMemoryActor]
        F -- Stores Answer using Actor State (Memory) --> F
    end

    subgraph LearningAnalyticsService["LearningAnalyticsService (learning-analytics-app)"]
        E --> G[StudentAnalyticsActor]
        G -- Analyzes Performance (using event + internal state/summary) --> G
        G -- If struggling, publishes student_assistance_required_event --> H[(teacher-notifications-topic)]
    end

    subgraph TeacherSupportService["TeacherSupportService (teacher-support-app)"]
        H --> I[TeacherSupportAgentActor]
        I -->|1. Logs Alert| I
        I -->|2. Simulates Resource Curation & Email| J[Log Output]
    end

    classDef user fill:#f9f,stroke:#fff,stroke-width:2px,color:#111,font-weight:bold;
    classDef api fill:#ccf,stroke:#fff,stroke-width:2px,color:#111,font-weight:bold;
    classDef actor fill:#bfb,stroke:#fff,stroke-width:2px,color:#111,font-weight:bold;
    classDef topic fill:#fa0,stroke:#fff,stroke-width:2px,color:#111,font-weight:bold;
    classDef default fill:#eee,stroke:#fff,stroke-width:1px,color:#111;

    class A user;
    class B,C api;
    class D,F,G,I actor;
    class E,H topic;
    class J default;
```

Good luck with the challenge!
