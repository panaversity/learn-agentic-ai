"""
02_base_agent_actor/daca-ambient-agent/ambient-actor/src/ambient_actor/actors/interface.py

This file defines the comprehensive external contract for the DACA Base Actor Runtime.
It provides a structured way for other actors, services, or external systems to interact
with the full spectrum of DACA agent capabilities, aligning with DACA principles
and 12-Factor Agents, and designed to support complex interactions and background handoffs.
"""

from dapr.actor import ActorInterface, actormethod
# Using modern Python type hints (e.g., dict, list, | None).
# For Python < 3.9, use from typing import Dict, List, Optional.


class BaseActorInterface(ActorInterface):
    """
    Defines the comprehensive external contract for the DACA Base Actor Runtime.

    These methods are callable by other actors, services, or external systems
    to interact with the full spectrum of DACA agent capabilities. The docstrings
    provide details on arguments, return values, and the purpose ("What, Why, How")
    of each method, including considerations for future milestones like M6 background handoffs.
    """

    # --- Core Interaction & Event Handling ---
    @actormethod(name="ProcessMessage")
    async def process_message(
        self, input: dict[str, str | list | dict]
    ) -> dict[str, object] | None:
        """
        What:
            Handles generic synchronous messages, commands, or queries sent to the actor.
            This is a versatile entry point for various synchronous interactions.
        Why:
            Fulfills the 'Reactive & Real-Time Processing' promise by enabling low-latency,
            versatile message handling. The actor can signal an outgoing stream via the response.
        How:
            The actor's internal logic processes the `message_data` (which should specify
            the intended action or query) in real-time, potentially updating state,
            triggering events, or initiating workflows. Supports 'Flexible Agent Engine
            Integration' by handling diverse payloads. In M6, may initiate background handoffs.
            Aligns with 12-Factor Agents (Factor 6: Expose control via APIs).

        Args:
            input (dict[str, str | list | dict]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "message_data": dict, the actual message from the user (e.g., {"role": "user", "content": "Hi"}).
                - "engine_config": dict, configuration for the agentic engine (e.g., {"run_method": "run", "model": "..."}).
                - "engine_type": str, specifying the type of engine (e.g., "openai").

        Returns:
            dict[str, object] | None: A dictionary containing the processing status and result.
                Example Success: `{"status": "success", "result": {"answer": "AI is..."}}`
                Example Streaming: `{"status": "accepted_for_streaming", "stream_id": "unique_session_id", "stream_info": {"output_topic": "actor_stream_topic"}}`
                Example Error: `{"status": "error", "error_message": "Failed to process."}`
                Returns `None` if the interface method is not implemented.
        """
        pass

    @actormethod(name="GetConversationHistory")
    async def get_conversation_history(self) -> list[dict] | None:
        """Retrieve conversation history."""
        pass
        
    @actormethod(name="ProcessEvent")
    async def process_event(
        self,
        input: dict[str, object]
    ) -> None:
        """
        What:
            Processes asynchronous events received via Dapr pub/sub or other sources
            (e.g., Dapr input bindings).
        Why:
            Meets the 'Comprehensive EDA' promise by enabling event-driven behavior,
            critical for decoupled communication. Idempotency, supported by `event_metadata`,
            ensures reliability ('Deep Resiliency & Idempotency').
        How:
            Handles events (e.g., task updates, external signals), updating state or
            triggering actions. `event_metadata` (e.g., event ID, source, timestamp)
            supports tracing and deduplication. In M6, facilitates event-driven handoffs.
            Aligns with A2A facilitation and 12-Factor Agents (Factor 11: Various triggers).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "event_payload": dict[str, object], the core data of the event.
                - "event_metadata": dict[str, object] | None, optional, details like event ID, source,
                    timestamp for tracing and idempotency. Defaults to None.
        """
        pass

    # --- Proactive Behavior & Task Management ---
    @actormethod(name="ScheduleReminder")
    async def schedule_reminder(
        self, input: dict[str, object]
    ) -> str | None:
        """
        What:
            Schedules a persistent Dapr reminder for proactive tasks (e.g., health checks,
            periodic data aggregation).
        Why:
            Fulfills the 'Proactive & Scheduled Execution' promise with reliable, persistent
            task scheduling. `ttl_seconds` allows for temporary yet persistent tasks.
        How:
            Registers a Dapr reminder that will trigger the actor's `receive_reminder` method,
            passing `task_data`. Supports one-time or recurring tasks based on `period_seconds`.
            In M6, can schedule follow-up tasks for handoffs (e.g., checking delegated task status).
            Aligns with 12-Factor Agents (Factor 11: Various trigger mechanisms).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "reminder_name": str, a unique name for this reminder instance (acts as its ID).
                - "task_data": dict[str, object] | None, optional, state to be passed to the actor
                when the reminder fires. Defaults to None.
                - "due_time_seconds": int, optional, delay in seconds before the first invocation. Defaults to 0.
                - "period_seconds": int, optional, interval in seconds for recurring reminders.
                    If 0, it's a one-time reminder. Defaults to 0.
                - "ttl_seconds": int | None, optional, time-to-live in seconds for the reminder registration.
                    Defaults to None (no TTL).

        Returns:
            str | None: The `reminder_name` as the identifier for the scheduled task, or `None` if scheduling fails or not implemented.
        """
        pass

    @actormethod(name="CancelReminder")
    async def cancel_reminder(self, reminder_name: str) -> None:
        """
        What:
            Cancels a previously scheduled Dapr reminder.
        Why:
            Provides control over persistent proactive tasks, ensuring flexibility as part of the
            'Proactive & Scheduled Execution' promise.
        How:
            Unregisters the Dapr reminder, stopping future executions. In M6, can cancel
            handoff-related reminders if a task is completed or re-routed.
            Aligns with 12-Factor Agents (Factor 11).

        Args:
            reminder_name (str): The unique name/ID of the Dapr reminder to cancel.
        """
        pass

    # --- State, Memory & Knowledge Management ---
    @actormethod(name="UpdateKnowledgeEntry")
    async def update_knowledge_entry(
        self, input: dict[str, object]
        ) -> None:
        """
        What:
            Updates or creates a specific entry in the actor's persistent knowledge base
            (e.g., using Dapr state store like Redis).
        Why:
            Meets 'Advanced State, Memory, and Knowledge Management' promise by enabling
            persistent state for short-term operational data and long-term knowledge.
            `metadata` can support advanced features like custom TTL, versioning, or embeddings info.
        How:
            Saves structured `data_payload` associated with `entry_id`, along with `metadata`.
            In M6, stores handoff state (e.g., task details, intermediate results).
            Aligns with 12-Factor Agents (Factor 5: Unify execution and business state).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "entry_id": str, a unique identifier for the knowledge entry.
                - "data_payload": dict[str, object], the content of the knowledge entry.
                - "metadata": dict[str, object] | None, optional, additional context like source,
                timestamp, vector embeddings info, TTL. Defaults to None.
        """
        pass

    @actormethod(name="QueryKnowledge")
    async def query_knowledge(
        self, input: dict[str, object]
    ) -> dict[str, object] | None:
        """
        What:
            Queries the actor’s knowledge base and various memory systems (e.g., Dapr state store,
            integrated vector databases via an MCP-like mechanism).
        Why:
            Fulfills state management and knowledge retrieval by enabling flexible querying,
            from simple key-value lookups (by `entry_id` in `query` dict) to potentially more
            complex semantic searches (depending on implementation). Supports 'Own your context window'.
        How:
            Executes queries based on `query` payload, potentially targeting specific `memory_types`
            with `query_config` (e.g., top_k results, filters, consistency levels).
            In M6, retrieves handoff state for task tracking or context resumption.
            Aligns with 12-Factor Agents (Factor 3: Manage context effectively).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "query": dict[str, object], the query itself (e.g., `{"entry_id": "some_id"}` or
                    `{"semantic_query": "search text", "vector_space": "docs"}`).
                - "memory_types": list[str] | None, optional, specifies which memory systems to target
                (e.g., ["dapr_state", "vector_db_main"]). Defaults to None (implementation-defined default).
                - "query_config": dict[str, object] | None, optional, parameters for the query
                    (e.g., `{"top_k": 5, "include_metadata": True}`). Defaults to None.

        Returns:
            dict[str, object] | None: Structured query results, or `None` if no results/error or not implemented.
        """
        pass

    @actormethod(name="DeleteKnowledgeEntry")
    async def delete_knowledge_entry(self, entry_id: str) -> None:
        """
        What:
            Deletes a specific knowledge entry from the actor's persistent state store.
        Why:
            Supports state management by enabling cleanup of outdated or irrelevant information,
            preventing state bloat, and potentially supporting versioning strategies. Essential for long-lived agents.
        How:
            Removes the state entry associated with `entry_id`. In M6, cleans up obsolete handoff state
            or temporary data after task completion.
            Aligns with 12-Factor Agents (Factor 5).

        Args:
            entry_id (str): The unique identifier of the knowledge entry to delete.
        """
        pass

    @actormethod(name="PrepareContext")
    async def prepare_context(
        self, input: dict[str, object]
    ) -> dict[str, object] | None:
        """
        What:
            Prepares context for LLM calls, agent decision-making, or user interactions
            by aggregating and processing information from the actor's state and knowledge.
        Why:
            Fulfills 'Advanced State, Memory, and Knowledge Management' by enabling
            sophisticated, dynamic context preparation (e.g., summarization of history,
            retrieval of relevant documents, vectorization hints). Addresses user-to-agent memory needs.
        How:
            Typically queries state/knowledge via `QueryKnowledge` or direct state access,
            applies `config`-driven processing (e.g., selecting top_k results, applying
            transformation functions, formatting for LLM), and returns a structured context payload.
            In M6, prepares comprehensive context for handoff tasks (e.g., passing conversation
            history, relevant data). Aligns with 12-Factor Agents (Factor 3).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "query": dict[str, object], specifies the information needed for context
                    (e.g., `{"user_id": "u123", "session_id": "s456", "context_type": "llm_prompt"}`).
                - "config": dict[str, object] | None, optional, configuration for context preparation
                (e.g., `{"max_tokens": 2000, "summary_level": "detailed"}`). Defaults to None.

        Returns:
            dict[str, object] | None: A dictionary representing the prepared context, or `None` if not implemented.
        """
        pass

    # --- Data Streaming ---
    @actormethod(name="IngestStreamChunk")
    async def ingest_stream_chunk(
        self, input: dict[str, object]
    ) -> None:
        """
        What:
            Processes incoming stream chunks for non-message-based workflows (e.g., large file uploads,
            continuous sensor data ingestion).
        Why:
            Supports 'Robust Streaming Capabilities' for data ingestion, complementing
            `ProcessMessage`’s ability to handle streaming outputs from the actor. Ensures
            full streaming support for diverse use cases.
        How:
            Handles individual `chunk_data` with `sequence_number` for ordering and `is_last_chunk`
            for finalization, potentially storing progress or aggregated data in state.
            `metadata` provides context about the stream or chunk. In M6, supports streaming
            handoffs for real-time data transfer between agents or services.
            Aligns with 12-Factor Agents (Factor 7: Treat tools as structured JSON outputs, extensible to streams).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "stream_id": str, identifier to correlate chunks belonging to the same stream.
                - "chunk_data": bytes, the actual data chunk.
                - "sequence_number": int, for ordering chunks.
                - "is_last_chunk": bool, flag indicating the end of the stream.
                - "metadata": dict[str, object] | None, optional, context about the stream or chunk.
                Defaults to None.
        """
        pass

    @actormethod(name="InitiateOutgoingStream")
    async def initiate_outgoing_stream(
        self, input: dict[str, object]
    ) -> dict[str, object] | None:
        """
        What:
            Initiates an outgoing stream from the actor (e.g., to stream LLM responses, processed data,
            or logs). The actual chunks are typically sent via an internally managed mechanism
            (e.g., publishing to a dedicated pub/sub topic per `stream_id`).
        Why:
            Completes 'Robust Streaming Capabilities' by enabling the actor to be a source of streams,
            allowing clients or other services to consume data chunk by chunk.
        How:
            Sets up resources or state for the outgoing stream (e.g., creates a unique pub/sub topic name based
            on `stream_id`). The actor then internally publishes chunks to this designated channel.
            The `recipient_details` might specify preferences for the stream.
            In M6, supports streaming handoff results or ongoing task updates.
            Aligns with 12-Factor Agents (Factor 7).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "stream_id": str, a unique identifier for this outgoing stream.
                - "recipient_details": dict[str, object], information about the intended recipient or
                the nature of the stream (e.g., `{"type": "llm_response", "client_id": "c789"}`).
                - "metadata": dict[str, object] | None, optional, additional context for the stream.
                    Defaults to None.

        Returns:
            dict[str, object] | None: Information needed by the recipient to connect to or identify
                the stream (e.g., `{"stream_id": stream_id, "output_topic": "actor_stream_topic_for_stream_id"}`).
                Returns `None` if not implemented.
        """
        pass

    # --- Planning & Goal-Oriented Execution ---
    @actormethod(name="InitiateGoalPlan")
    async def initiate_goal_plan(
        self, input: dict[str, object]
    ) -> str | None:
        """
        What:
            Instructs the actor to create and potentially start executing a plan to achieve a given goal.
        Why:
            Fulfills 'Integrated Planning & Task Management' by enabling complex, multi-step goal
            execution. Critical for agent autonomy and sophisticated behavior.
        How:
            Generates a unique `plan_id`. The actor internally decomposes the `goal_description` into
            tasks, potentially using an LLM or a predefined strategy, storing progress and state.
            May involve scheduling reminders/timers or starting Dapr Workflows.
            In M6, initiates handoff plans for tasks delegated to other actors or workflows.
            Aligns with 12-Factor Agents (Factor 8: Own your control flow).

        Args:
            goal_description (str): A clear, natural language or structured description of the desired outcome.
            plan_parameters (dict[str, object] | None, optional): Any specific constraints,
                inputs, or configuration for the planning process. Defaults to None.

        Returns:
            str | None: A unique `plan_id` to track this planning and execution instance, or `None` if not implemented.
        """
        pass

    @actormethod(name="GetPlanExecutionStatus")
    async def get_plan_execution_status(self, plan_id: str) -> dict[str, object] | None:
        """
        What:
            Queries the status, current progress, and any intermediate or final results of a plan.
        Why:
            Supports 'Integrated Planning & Task Management' by enabling plan monitoring and
            tracking of complex goals. Essential for observability and external coordination.
        How:
            Retrieves the plan's state (e.g., status like 'running', 'completed', 'failed';
            current_step; intermediate_results; errors) from the actor's state store.
            In M6, tracks the progress of handoff plans.
            Aligns with 12-Factor Agents (Factor 8).

        Args:
            plan_id (str): The ID of the plan to query.

        Returns:
            dict[str, object] | None: A structured status report for the plan, or `None` if not implemented.
        """
        pass

    @actormethod(name="ControlGoalPlan")
    async def control_goal_plan(
        self, input: dict[str, object]
    ) -> None:
        """
        What:
            Controls an ongoing plan’s execution (e.g., 'pause', 'resume', 'update_parameter', 'retry_step').
        Why:
            Provides flexibility and external control over 'Integrated Planning & Task Management',
            allowing dynamic adjustments to agent behavior.
        How:
            Updates the plan's state or triggers specific control logic based on the `action`
            and `parameters`. In M6, allows managing handoff plans during delegation or if issues arise.
            Aligns with 12-Factor Agents (Factor 8).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "plan_id": str, the ID of the plan to control.
                - "action": str, the control action to perform (e.g., "pause", "resume", "retry_failed_step").
                - "parameters": dict[str, object] | None, optional, additional parameters for the control action.
                    Defaults to None.
        """
        pass

    @actormethod(name="CancelGoalPlan")
    async def cancel_goal_plan(self, plan_id: str) -> None:
        """
        What:
            Cancels an ongoing or pending plan execution.
        Why:
            Ensures control over planning, supporting 'Integrated Planning & Task Management'.
            Allows for graceful termination of tasks that are no longer needed.
        How:
            Stops the plan's execution, cleans up associated resources (e.g., reminders, timers),
            and updates its state to 'cancelled'. In M6, cancels handoff plans if the primary goal changes.
            Aligns with 12-Factor Agents (Factor 8).

        Args:
            plan_id (str): The ID of the plan to cancel.
        """
        pass

    @actormethod(name="ListActiveGoalPlans")
    async def list_active_goal_plans(self) -> list[dict[str, object]] | None:
        """
        What:
            Retrieves a list of currently active or pending plans managed by this actor.
        Why:
            Supports 'Integrated Planning & Task Management' by providing visibility into the
            actor's ongoing goals and commitments.
        How:
            Queries the actor's state for metadata of plans that are not in a terminal state
            (e.g., completed, failed, cancelled). In M6, lists handoff plans for oversight.
            Aligns with 12-Factor Agents (Factor 8).

        Returns:
            list[dict[str, object]] | None: A list of plan metadata dictionaries (e.g.,
                `[{'plan_id': 'p1', 'status': 'running', 'goal': '...'}]`), or `None` if not implemented.
        """
        pass

    @actormethod(name="GetAgentProfile")
    async def get_agent_profile(self) -> dict[str, object] | None:
        """
        What:
            Retrieves the actor's profile, akin to an Agent Card, for A2A communication and discovery.
        Why:
            Meets 'A2A & MCP Facilitation' by enabling other agents or systems to discover
            this actor's capabilities, supported interaction methods (potentially beyond this
            interface for specialized agents), communication endpoints, and other metadata.
            Supports standardized agent ecosystems and "Agentia World" vision.
        How:
            Returns a structured profile dictionary containing information like actor type,
            version, supported DACA interface methods, custom methods, data schemas for interaction,
            MCP tool capabilities, and subscribed event topics. In M6, helps identify suitable
            actors for handoff delegation based on their profile.
            Aligns with 12-Factor Agents (Factor 10: Promote small, focused agents by clear capability definition).

        Returns:
            dict[str, object] | None: The actor's profile dictionary, or `None` if not implemented.
        """
        pass

    # --- Human-in-the-Loop (HITL) ---
    @actormethod(name="FlagForHumanReview")
    async def flag_for_human_review(
        self, input: dict[str, object]
    ) -> None:
        """
        What:
            The actor signals that a specific task, decision, or piece of data requires human review.
        Why:
            Meets 'HITL Integration' by enabling human intervention for complex, ambiguous,
            or low-confidence tasks, ensuring safer and more reliable agent operation.
        How:
            Typically publishes a review request event (containing `review_request_id`, `task_context`, etc.)
            to a dedicated HITL system or topic, or stores it for polling. `assigned_to` can route
            the review. In M6, flags handoff tasks or decisions for validation by a human supervisor.
            Aligns with 12-Factor Agents (Factor 4: Treat HITL as a tool call/structured interaction).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "review_request_id": str, a unique ID for this specific review request.
                - "task_context": dict[str, object], data and context relevant to what needs reviewing.
                - "review_instructions": str | None, optional, specific questions or guidance for the human reviewer.
                Defaults to None.
                - "confidence_score": float | None, optional, the actor's confidence in its current
                    state/decision, if applicable. Defaults to None.
                - "assigned_to": str | None, optional, optional identifier for a specific human, role, or group
                    for review. Defaults to None.
        """
        pass

    @actormethod(name="ProvideHumanFeedback")
    async def provide_human_feedback(
        self, input: dict[str, object]
    ) -> None:
        """
        What:
            An external system or human submits feedback (decision, correction, annotation) for a
            task previously flagged for review via `FlagForHumanReview`.
        Why:
            Completes the 'HITL Integration' loop by allowing the agent to receive and process
            human input, enabling it to adapt, learn (potentially), or proceed with human guidance.
        How:
            The actor receives the `feedback_payload` for the given `review_request_id`.
            It updates its state, modifies its plan, or takes corrective action based on the feedback
            and `resolution_status`. `reviewer_details` provides auditability. In M6, human feedback
            can refine handoff tasks or approve delegated actions.
            Aligns with 12-Factor Agents (Factor 4).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "review_request_id": str, the ID of the original review request being addressed.
                - "feedback_payload": dict[str, object], the human's decision, corrections, or annotations.
                - "reviewer_details": dict[str, object] | None, optional, information about the reviewer
                (e.g., `{"id": "user789", "role": "senior_analyst"}`). Defaults to None.
            resolution_status (str | None, optional): Status of the review outcome
                (e.g., "approved", "rejected_with_comments", "clarification_needed"). Defaults to None.
        """
        pass

    # --- Dapr Workflow Interaction (Retained for explicit orchestration if needed) ---
    @actormethod(name="StartExternalWorkflow")
    async def start_external_workflow(
        self, input: dict[str, object]
    ) -> str | None:
        """
        What:
            Initiates an external Dapr workflow instance, typically for long-running, multi-step,
            or complex blocking tasks that are better managed outside the actor's direct execution.
        Why:
            Meets 'Dapr Workflow Interaction' by enabling the actor to offload complex processes,
            keeping the actor itself responsive. Useful for addressing handoff scenarios like those
            seen in LangGraph/CrewAI, where an actor might delegate a sub-process to a workflow.
        How:
            The actor calls Dapr to start a workflow instance of type `workflow_name` (registered with Dapr),
            optionally specifying the `workflow_component_name` if not default. `workflow_input` is passed
            to the workflow, and `workflow_options` can include things like instance ID.
            In M6, provides a mechanism for delegating complex handoff tasks to Dapr Workflows.
            Aligns with 12-Factor Agents (Factor 8: Own your control flow, which can include offloading).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "workflow_name": str, the type of the Dapr workflow to start.
                - "workflow_component_name": str | None, optional, the name of the Dapr workflow component
                    if multiple are configured. Defaults to None (Dapr uses default).
                - "workflow_input": dict[str, object] | None, optional, input data for the workflow. Defaults to None.
            workflow_options (dict[str, object] | None, optional): Options for starting the workflow,
                like a custom instance ID. Defaults to None.

        Returns:
            str | None: The Dapr workflow instance ID if successfully started, or `None` if not implemented/failed.
        """
        pass

    @actormethod(name="SendEventToWorkflow")
    async def send_event_to_workflow(
        self,
        input: dict[str, object]
    ) -> None:
        """
        What:
            Sends an event to a running Dapr workflow instance, allowing for dynamic interaction
            and data passing during workflow execution.
        Why:
            Supports 'Dapr Workflow Interaction' by enabling actors to communicate with and influence
            ongoing Dapr workflows.
        How:
            The actor uses Dapr client to raise an event for the specified `workflow_instance_id`.
            The workflow must be designed to listen for `event_name`. In M6, can send handoff-related
            updates or results to a managing workflow.
            Aligns with 12-Factor Agents (Factor 8).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "workflow_instance_id": str, the ID of the target Dapr workflow instance.
                - "event_name": str, the name of the event to send to the workflow.
                - "event_payload": dict[str, object] | None, optional, data associated with the event.
                    Defaults to None.
                - "workflow_component_name": str | None, optional, the Dapr workflow component name.
                Defaults to None.
        """
        pass

    @actormethod(name="GetExternalWorkflowStatus")
    async def get_external_workflow_status(
        self, input: dict[str, object]
    ) -> dict[str, object] | None:
        """
        What:
            Queries the status and metadata of a specific Dapr workflow instance.
        Why:
            Supports 'Dapr Workflow Interaction' by enabling actors to monitor the progress and
            outcome of workflows they may have started or are otherwise interested in.
        How:
            The actor calls Dapr to get the status of the `workflow_instance_id`.
            In M6, tracks the progress of handoff workflows.
            Aligns with 12-Factor Agents (Factor 8).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "workflow_instance_id": str, the ID of the Dapr workflow instance to query.
                - "workflow_component_name": str | None, the Dapr workflow component name.
                    Defaults to None.

        Returns:
            dict[str, object] | None: A dictionary containing the workflow status and metadata, or `None` if not implemented/error.
        """
        pass

    @actormethod(name="TerminateExternalWorkflow")
    async def terminate_external_workflow(
        self, input: dict[str, object]
    ) -> None:
        """
        What:
            Terminates a running Dapr workflow instance.
        Why:
            Provides control over Dapr workflows, supporting 'Dapr Workflow Interaction', for example,
            if a goal is cancelled and its associated workflow is no longer needed.
        How:
            The actor calls Dapr to terminate the `workflow_instance_id`. In M6, can cancel handoff
            workflows if the overarching task is aborted.
            Aligns with 12-Factor Agents (Factor 8).

        Args:
            input (dict[str, object]): A dictionary containing all necessary data for processing.
                Expected keys typically include:
                - "workflow_instance_id": str, the ID of the Dapr workflow instance to terminate.
                - "workflow_component_name": str | None, the Dapr workflow component name.
                    Defaults to None.
        """
        pass
