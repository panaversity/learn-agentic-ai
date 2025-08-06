"""
This file implements the BaseActor for the DACA Actor Runtime.
It provides the foundational capabilities for all DACA agents, inheriting from Dapr's Actor and Remindable classes, and implementing the comprehensive BaseActorInterface.
"""

import json
import logging

from typing import cast
from datetime import timedelta, datetime, UTC

from ambient_actor.agents.engine_adapter import AgenticEngineAdapter
from ambient_actor.agents.openai_adapter import OpenAIEngineAdapter
from dapr.actor import Actor, Remindable, ActorId
from dapr.clients import DaprClient
from ambient_actor.actors.interface import BaseActorInterface

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BaseActor(Actor, BaseActorInterface, Remindable):
    """
    Base class for DACA actors, providing core Dapr integration and
    stub implementations for the DACA BaseActorInterface.
    """

    def __init__(self, ctx, actor_id: ActorId):
        super().__init__(ctx, actor_id)
        self.actor_type = self.__class__.__name__
        self.agentic_engine: AgenticEngineAdapter | OpenAIEngineAdapter | None = None

        # self.actor_id is already available via self.id from the base Actor class
        # but having it explicitly can be convenient. self.id is ActorId type.
        logger.info(f"Actor '{self.id.id}' of type '{self.actor_type}' __init__ called.")

    async def _on_activate(self) -> None:
        """
        Called when an actor is activated.
        This method is invoked by the Dapr runtime when an actor instance is being
        brought into memory. It's the ideal place for:
        - Initializing actor state (if not already present).
        - Loading actor-specific configuration.
        - Registering any default reminders or timers needed for the actor's lifecycle.
        """
        logger.info(f"Actor '{self.id.id}' of type '{self.actor_type}' _on_activate: Activating.")

        # Example: Initialize a basic status state if it doesn't exist
        status_exists = await self._state_manager.contains_state("actor_status")
        if not status_exists:
            initial_status = {
                "status": "active",
                "last_activated_at": datetime.now(UTC).isoformat(),
                "version": "1.0.0",  # Example version
            }
            await self._state_manager.set_state("actor_status", initial_status)
            logger.info(f"Actor '{self.id.id}': Initialized 'actor_status' state. Initial state: {initial_status}")
        else:
            # Optionally update activation time if status exists
            current_status = await self._get_actor_state("actor_status", default={})
            if isinstance(current_status, dict):  # Ensure it's a dictionary
                current_status["last_activated_at"] = datetime.now(UTC).isoformat()
                await self._state_manager.set_state("actor_status", current_status)
                logger.info(f"Actor '{self.id.id}': Updated 'last_activated_at' in 'actor_status'. Current state: {current_status}")
            else:
                logger.warning(f"Actor '{self.id.id}': 'actor_status' state exists but is not a dictionary. Re-initializing.")
                initial_status = {
                    "status": "active_reinitialized",
                    "last_activated_at": datetime.now(UTC).isoformat(),
                    "version": "1.0.0",  # Example version
                }
                await self._state_manager.set_state("actor_status", initial_status)

        # Further initialization, such as loading configuration or setting up
        # default reminders/timers, would go here.
        # E.g., await self._load_configuration()
        logger.info(f"Actor '{self.id.id}' of type '{self.actor_type}' _on_activate: Activation complete.")

    async def _on_deactivate(self) -> None:
        """
        Called when an actor is deactivated.
        This method is invoked by the Dapr runtime before an actor instance is
        removed from memory (garbage collected due to inactivity). It's the place for:
        - Performing any cleanup operations.
        - Persisting any final volatile state if necessary (though Dapr actors
          generally encourage immediate state persistence).
        """
        logger.info(f"Actor '{self.id.id}' of type '{self.actor_type}' _on_deactivate: Deactivating.")
        # Perform any cleanup here, e.g., releasing external resources if any were acquired
        # and not managed by Dapr bindings or components.
        logger.info(f"Actor '{self.id.id}' of type '{self.actor_type}' _on_deactivate: Deactivation complete.")

    async def _timer_event_adapter(self, packed_state_bytes: bytes) -> None:
        """
        Adapter for Dapr timer callbacks to match the linter-expected signature.
        It decodes the actual timer name from packed_state_bytes, then calls
        the main receive_reminder method. The full packed_state_bytes is passed
        as 'state' to receive_reminder, which will then decode the user_task_data.
        """
        actual_timer_name_for_dispatch = "unknown_timer_via_adapter"  # Fallback

        try:
            decoded_wrapper = json.loads(packed_state_bytes.decode("utf-8"))
            if (
                isinstance(decoded_wrapper, dict)
                and "actual_timer_name_for_dispatch" in decoded_wrapper
            ):
                actual_timer_name_for_dispatch = decoded_wrapper[
                    "actual_timer_name_for_dispatch"
                ]
            else:
                logger.warning(
                    f"Actor '{self.id.id}': Timer state for _timer_event_adapter "
                    f"did not contain 'actual_timer_name_for_dispatch'. Using fallback name '{actual_timer_name_for_dispatch}'."
                )
        except Exception as e:
            logger.warning(
                f"Actor '{self.id.id}': Failed to decode wrapped state in _timer_event_adapter: {e}. "
                f"Using fallback name '{actual_timer_name_for_dispatch}'. Raw state: {packed_state_bytes[:100]!r}"
            )

        # Call receive_reminder. Due_time, period, ttl are conceptual here,
        # as Dapr provides them to receive_reminder based on registration when called by string name.
        # The adapter pattern means we pass indicative values.
        await self.receive_reminder(
            name=actual_timer_name_for_dispatch,
            # Pass the full wrapper, receive_reminder will parse user_task_data
            state=packed_state_bytes,
            due_time=timedelta(seconds=0),
            period=timedelta(seconds=0),
            ttl=None,
        )

    async def receive_reminder(
        self,
        name: str,
        state: bytes,
        due_time: timedelta,
        period: timedelta,
        ttl: timedelta | None = None,
    ) -> None:
        """
        Dapr runtime callback when a reminder or timer fires.
        The `name` corresponds to the `reminder_name` or `timer_name` used during scheduling.
        If called via `_timer_event_adapter` for a timer, `name` is the extracted actual timer name,
        and `state` is the `packed_state_bytes` containing the wrapper.
        """
        logger.info(
            f"Actor '{self.id.id}' received reminder/timer '{name}' "
            f"due at {due_time}, with period {period}."
        )
        try:
            task_data_dict: dict[str, object] = {}
            if state:
                decoded_outer_state = {}
                try:
                    decoded_outer_state = json.loads(state.decode("utf-8"))
                except json.JSONDecodeError:
                    logger.warning(
                        f"Actor '{self.id.id}': State for '{name}' was not valid JSON. Raw: {state.decode('utf-8', errors='replace')[:100]}"
                    )
                    # If state is not JSON at all, task_data_dict remains empty, or handle as non-JSON if expected for some reminders.

                if (
                    isinstance(decoded_outer_state, dict)
                    and "actual_timer_name_for_dispatch" in decoded_outer_state
                    and "user_task_data" in decoded_outer_state
                ):
                    # This indicates the state came from _timer_event_adapter (it's the wrapper)
                    task_data_dict = decoded_outer_state.get("user_task_data", {})
                    # 'name' should already be the actual_timer_name_for_dispatch set by the adapter
                    logger.info(
                        f"Actor '{self.id.id}': Timer event for '{name}' via adapter. Extracted user_task_data."
                    )
                # It's a JSON dict, but not the timer wrapper
                elif isinstance(decoded_outer_state, dict):
                    # Assume this is a reminder or a timer called directly (if that path existed)
                    # where the state is directly the user's task_data.
                    task_data_dict = decoded_outer_state
                    logger.info(
                        f"Actor '{self.id.id}': Reminder event or direct timer event for '{name}'. State is task_data."
                    )
                else:  # Not a dict or not the wrapper
                    logger.info(
                        f"Actor '{self.id.id}': State for '{name}' was not a dictionary after decoding or not the timer wrapper. Content: {str(decoded_outer_state)[:100]}"
                    )

            logger.info(
                f"Actor '{self.id.id}': Decoded task_data for '{name}': {task_data_dict}"
            )

            # Example: Generic handler, actual logic would dispatch based on 'name'
            # or a 'task_type' field within task_data_dict.
            if name == "example_reminder_from_interface":
                logger.info(
                    f"Actor '{self.id.id}': Handling specific reminder '{name}' with data: {task_data_dict}"
                )
                # TODO: Implement actual logic for this reminder
            # This check now correctly uses the extracted/passed timer name
            elif name.startswith("timer_"):
                logger.info(
                    f"Actor '{self.id.id}': Handling specific timer '{name}' with data: {task_data_dict}"
                )
                # TODO: Implement actual logic for this timer
            else:
                logger.warning(
                    f"Actor '{self.id.id}': No specific handler for reminder/timer '{name}'. Data: {task_data_dict}"
                )

            # Example: If it's a one-time reminder/timer (period is zero or not meaningful for timers after first fire),
            # and it's not intended to be rescheduled by its handler, no further action here.
            # If it's recurring, it will fire again based on 'period'.

        except (
            json.JSONDecodeError
        ):  # This might be less likely now if initial parsing is robust
            logger.error(
                f"Actor '{self.id.id}': Outer JSON decode failed for reminder/timer state for '{name}'. Raw state: {state.decode('utf-8', errors='replace')}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Actor '{self.id.id}': Error processing reminder/timer '{name}': {e}",
                exc_info=True,
            )
            raise
        # Pass is implicit if no other statements are present

    # --- Interface Method Implementations (Stubs) ---

    # --- Core Interaction & Event Handling ---
    async def process_message(
        self, input: dict[str, str | list | dict]
    ) -> dict[str, object] | None:
        logger.info(f"Actor '{self.id.id}' method 'process_message' called with: {input}")
        
        message_data = cast(dict, input.get("message_data", None))
        engine_config = cast(dict, input.get("engine_config", None))
        engine_type = cast(str, input.get("engine_type", "openai"))
        
        if engine_config is None:
            raise ValueError("Engine config is required")
        
        engine = await self._get_engine(engine_type=engine_type if isinstance(engine_type, str) else "openai", engine_config=engine_config if isinstance(engine_config, dict) else {})
        
        # get conversation and context from state
        conversation = await self._get_actor_state("conversation")
        
        if conversation is None or not isinstance(conversation, list):
            conversation = []
            
        # add message to conversation
        conversation.append(message_data)
        
        logger.info(f"\n\n Pre-engine Conversation: {conversation}\n\n")
        
        run_method = engine_config.get("run_method", "run")
        
        if run_method not in ["run", "run_sync"]:
            raise ValueError(f"Invalid run_method: {run_method}")
        
        if run_method == "stream":
            raise ValueError("Streaming is not supported yet")
        
        result = await engine.process_input(conversation, run_method= run_method)
        
        logger.info(f"\n\nEngine result: {result}\n\n")
        
        # We can get and save output if run_method is as run or run_sync
        if run_method in ["run", "run_sync"]:
            await self._state_manager.set_state("conversation", result.get("conversation"))
        else:
            logger.warning(f"No output from engine for message: {message_data}")        
        
        logger.info(f"\n\n Post-engine Conversation: {result.get('conversation')}\n\n")
        return {
            "status": "received",
            "actor_id": self.id.id,
            "conversation": result.get("conversation"),
            "final_output": result.get("final_output")
        }

    async def get_conversation_history(self) -> list[dict]:
        """Retrieve conversation history."""
        try:
            history = await self._state_manager.get_state("conversation")
            return history if isinstance(history, list) else []
        except Exception as e:
            logging.error(f"Error getting history for {self._history_key}: {e}")
            return []
    
    async def process_event(
        self, input: dict[str, object]
    ) -> None:
        event_payload = cast(dict[str, object], input.get("event_payload"))
        event_metadata = cast(dict[str, object] | None, input.get("event_metadata"))
        logger.info(
            f"Actor '{self.id.id}' method 'process_event' called with payload: {event_payload}, metadata: {event_metadata}"
        )
        # TODO: Implement actual event processing logic, ensure idempotency using event_metadata
        pass

    # --- Proactive Behavior & Task Management ---
    async def schedule_reminder(
        self, input: dict[str, object]
    ) -> str | None:
        reminder_name = cast(str, input.get("reminder_name"))
        task_data = cast(dict[str, object] | None, input.get("task_data"))
        due_time_seconds = cast(int, input.get("due_time_seconds", 0))
        period_seconds = cast(int, input.get("period_seconds", 0))
        ttl_seconds = cast(int | None, input.get("ttl_seconds"))
        logger.info(
            f"Actor '{self.id.id}' method 'schedule_reminder' called for '{reminder_name}'"
        )
        try:
            # Dapr reminders require state to be bytes. Convert dict to JSON string then bytes.
            state_bytes = b""
            if task_data:
                state_bytes = json.dumps(task_data).encode("utf-8")

            due_time_td = timedelta(seconds=due_time_seconds)
            period_td = (
                timedelta(seconds=period_seconds)
                if period_seconds > 0
                else timedelta(seconds=0)
            )  # Dapr period 0 means not recurring after first fire
            ttl_td = timedelta(seconds=ttl_seconds) if ttl_seconds is not None else None

            await self.register_reminder(
                name=reminder_name,
                state=state_bytes,
                due_time=due_time_td,
                period=period_td,
                ttl=ttl_td,  # Pass TTL if provided
            )
            logger.info(
                f"Actor '{self.id.id}': Successfully registered reminder '{reminder_name}'."
            )
            return reminder_name
        except Exception as e:
            logger.error(
                f"Actor '{self.id.id}': Failed to schedule reminder '{reminder_name}': {e}",
                exc_info=True,
            )
            return None

    async def cancel_reminder(self, reminder_name: str) -> None:
        logger.info(
            f"Actor '{self.id.id}' method 'cancel_reminder' called for '{reminder_name}'"
        )
        try:
            await self.unregister_reminder(reminder_name)
            logger.info(
                f"Actor '{self.id.id}': Successfully unregistered reminder '{reminder_name}'."
            )
        except (
            Exception
        ) as e:  # Dapr might raise if reminder not found, handle gracefully
            # Not necessarily an error
            logger.warning(
                f"Actor '{self.id.id}': Failed to unregister reminder '{reminder_name}' (it might not exist): {e}",
                exc_info=False,
            )
        pass

    # --- State, Memory & Knowledge Management ---
    async def update_knowledge_entry(
        self, input: dict[str, object]
    ) -> None:
        entry_id = cast(str, input.get("entry_id"))
        data_payload = cast(dict[str, object], input.get("data_payload"))
        metadata = cast(dict[str, object] | None, input.get("metadata"))
        logger.info(
            f"Actor '{self.id.id}' method 'update_knowledge_entry' called for entry_id: {entry_id}"
        )
        # Combine data and metadata for storage if needed, or store separately
        # For this stub, we'll just save the payload under entry_id. Metadata handling can be more complex.
        combined_entry = {"payload": data_payload, "metadata": metadata or {}}
        await self._state_manager.set_state(entry_id, combined_entry)
        pass

    async def query_knowledge(
        self, input: dict[str, object]
    ) -> dict[str, object] | None:
        query = cast(dict[str, object], input.get("query"))
        memory_types = cast(list[str] | None, input.get("memory_types"))
        query_config = cast(dict[str, object] | None, input.get("query_config"))
        logger.info(
            f"Actor '{self.id.id}' method 'query_knowledge' called with query: {query}"
        )
        # TODO: Implement actual knowledge querying logic
        # This might involve querying Dapr state, vector DBs, etc.
        if "entry_id" in query and isinstance(query["entry_id"], str):
            entry_id_to_query = query["entry_id"]
            knowledge_entry = await self._get_actor_state(entry_id_to_query)
            if knowledge_entry is not None and isinstance(knowledge_entry, dict):
                return {"entry_id": entry_id_to_query, "data": knowledge_entry}
            else:
                logger.info(
                    f"Actor '{self.id.id}': Knowledge entry '{entry_id_to_query}' not found or not a dict."
                )
                return None
        return {
            "status": "not_implemented",
            "query_received": query,
            "actor_id": self.id.id,
        }

    async def delete_knowledge_entry(self, entry_id: str) -> None:
        logger.info(
            f"Actor '{self.id.id}' method 'delete_knowledge_entry' called for entry_id: {entry_id}"
        )
        await self._state_manager.remove_state(entry_id)
        pass

    async def prepare_context(
        self, input: dict[str, object]
    ) -> dict[str, object] | None:
        query = cast(dict[str, object], input.get("query"))
        config = cast(dict[str, object], input.get("config"))
        logger.info(
            f"Actor '{self.id.id}' method 'prepare_context' called with query: {query}, config: {config}"
        )
        # TODO: Implement context preparation logic
        return {
            "status": "not_implemented",
            "context_for_query": query,
            "actor_id": self.id.id,
        }

    # --- Data Streaming ---
    async def ingest_stream_chunk(
        self, input: dict[str, object]
    ) -> None:
        stream_id = cast(str, input.get("stream_id"))
        chunk_data = cast(bytes, input.get("chunk_data"))
        sequence_number = cast(int, input.get("sequence_number"))
        is_last_chunk = cast(bool, input.get("is_last_chunk"))
        metadata = cast(dict[str, object], input.get("metadata"))
        logger.info(
            f"Actor '{self.id.id}' method 'ingest_stream_chunk' called for stream_id: {stream_id}, seq: {sequence_number}, last: {is_last_chunk}"
        )
        # TODO: Implement stream chunk ingestion logic
        pass

    async def initiate_outgoing_stream(
        self, input: dict[str, object]
    ) -> dict[str, object] | None:
        stream_id = cast(str, input.get("stream_id"))
        recipient_details = cast(dict[str, object], input.get("recipient_details"))
        metadata = cast(dict[str, object], input.get("metadata"))
        logger.info(
            f"Actor '{self.id.id}' method 'initiate_outgoing_stream' for stream_id: {stream_id}"
        )
        # TODO: Implement outgoing stream initiation
        # This would typically involve setting up a pub/sub topic or other mechanism
        return {
            "status": "not_implemented",
            "stream_id": stream_id,
            "output_topic": f"actor_streams/{self.id.id}/{stream_id}/output",
            "actor_id": self.id.id,
        }

    # --- Planning & Goal-Oriented Execution ---
    async def initiate_goal_plan(
        self, input: dict[str, object]
    ) -> str | None:
        goal_description = cast(str, input.get("goal_description"))
        plan_parameters = cast(dict[str, object], input.get("plan_parameters"))
        logger.info(
            f"Actor '{self.id.id}' method 'initiate_goal_plan' for goal: {goal_description}"
        )
        # TODO: Implement plan initiation logic
        plan_id = f"plan_{self.id.id}_{datetime.utcnow().timestamp()}"
        await self._state_manager.set_state(
            f"plan_{plan_id}_status",
            {
                "goal": goal_description,
                "status": "initiated",
                "steps": [],
                "parameters": plan_parameters or {},
            },
        )
        return plan_id

    async def get_plan_execution_status(self, plan_id: str) -> dict[str, object] | None:
        logger.info(
            f"Actor '{self.id.id}' method 'get_plan_execution_status' for plan_id: {plan_id}"
        )
        plan_status = await self._get_actor_state(f"plan_{plan_id}_status")
        if plan_status and isinstance(plan_status, dict):
            return plan_status
        logger.info(
            f"Actor '{self.id.id}': Plan status for '{plan_id}' not found or not a dict."
        )
        return {"status": "not_found", "plan_id": plan_id, "actor_id": self.id.id}

    async def control_goal_plan(
        self, input: dict[str, object]
    ) -> None:
        plan_id = cast(str, input.get("plan_id"))
        action = cast(str, input.get("action"))
        parameters = cast(dict[str, object], input.get("parameters"))
        logger.info(
            f"Actor '{self.id.id}' method 'control_goal_plan' for plan_id: {plan_id}, action: {action}"
        )
        # TODO: Implement plan control logic
        # Example: update plan status based on action
        # current_plan_status = await self._get_actor_state(f"plan_{plan_id}_status", default={})
        # if isinstance(current_plan_status, dict):
        #     current_plan_status['last_action'] = action
        #     current_plan_status['last_action_params'] = parameters
        #     current_plan_status['status'] = f"controlled_action_{action}" # Placeholder
        #     await self._state_manager.set_state(f"plan_{plan_id}_status", current_plan_status)
        pass

    async def cancel_goal_plan(self, plan_id: str) -> None:
        logger.info(
            f"Actor '{self.id.id}' method 'cancel_goal_plan' for plan_id: {plan_id}"
        )
        # TODO: Implement plan cancellation logic
        plan_status_key = f"plan_{plan_id}_status"
        current_plan_status = await self._get_actor_state(plan_status_key, default={})
        if isinstance(current_plan_status, dict):
            current_plan_status["status"] = "cancelled"
            await self._state_manager.set_state(plan_status_key, current_plan_status)
            logger.info(f"Actor '{self.id.id}': Plan '{plan_id}' marked as cancelled.")
        else:
            # If plan doesn't exist or state is malformed, still attempt to set a cancelled status
            await self._state_manager.set_state(
                plan_status_key,
                {
                    "status": "cancelled",
                    "note": "Original plan status not found or malformed.",
                },
            )
            logger.info(
                f"Actor '{self.id.id}': Plan '{plan_id}' status set to cancelled (original not found/malformed)."
            )
        pass

    async def list_active_goal_plans(self) -> list[dict[str, object]] | None:
        logger.info(f"Actor '{self.id.id}' method 'list_active_goal_plans' called")
        # TODO: Implement logic to list active plans (this is more complex)
        # Would require querying state for all keys matching a pattern, e.g., "plan_*_status"
        # and filtering them. This is not directly supported by basic key-value state stores easily.
        # For now, returning an empty list. A more robust implementation might involve
        # maintaining an index of active plans in a separate state entry.
        return []


    async def get_agent_profile(self) -> dict[str, object] | None:
        logger.info(f"Actor '{self.id.id}' method 'get_agent_profile' called")
        # TODO: Implement agent profile generation
        try:
            capabilities = [
                method_name
                for method_name in dir(BaseActorInterface)
                if callable(getattr(BaseActorInterface, method_name))
                and not method_name.startswith("_")
                and hasattr(getattr(BaseActorInterface, method_name), "__actormethod__")
            ]
        except Exception as e:
            logger.error(
                f"Actor '{self.id.id}': Error introspecting BaseActorInterface for capabilities: {e}",
                exc_info=True,
            )
            capabilities = ["error_introspecting_capabilities"]

        return {
            "actor_id": self.id.id,
            "actor_type": self.actor_type,
            "daca_interface_version": "1.0",  # Example
            "capabilities": capabilities,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # --- Human-in-the-Loop (HITL) ---
    async def flag_for_human_review(
        self,
        input: dict[str, object]
    ) -> None:
        review_request_id = cast(str, input.get("review_request_id"))
        task_context = cast(dict[str, object], input.get("task_context"))
        review_instructions = cast(str, input.get("review_instructions"))
        confidence_score = cast(float, input.get("confidence_score"))
        assigned_to = cast(str, input.get("assigned_to"))
        logger.info(
            f"Actor '{self.id.id}' method 'flag_for_human_review' called for request_id: {review_request_id}"
        )
        # TODO: Implement HITL flagging logic (e.g., publish event to HITL system)
        hitl_event = {
            "review_request_id": review_request_id,
            "task_context": task_context,
            "review_instructions": review_instructions,
            "confidence_score": confidence_score,
            "assigned_to": assigned_to,
            "actor_id": self.id.id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "flagged_for_review",
        }
        # Example: await self._publish_dapr_event("hitl_requests_topic", hitl_event)
        # For now, we can save this to actor state or just log
        await self._state_manager.set_state(f"hitl_review_{review_request_id}", hitl_event)
        logger.info(f"HITL_FLAGGED: {json.dumps(hitl_event)}")
        pass

    async def provide_human_feedback(
        self,
        input: dict[str, object]
    ) -> None:
        review_request_id = cast(str, input.get("review_request_id"))
        feedback_payload = cast(dict[str, object], input.get("feedback_payload"))
        reviewer_details = cast(dict[str, object], input.get("reviewer_details"))
        resolution_status = cast(str, input.get("resolution_status"))
        logger.info(
            f"Actor '{self.id.id}' method 'provide_human_feedback' for request_id: {review_request_id}"
        )
        # TODO: Implement logic to process human feedback
        # This might involve updating state, resuming a plan, etc.
        feedback_event = {
            "review_request_id": review_request_id,
            "feedback_payload": feedback_payload,
            "reviewer_details": reviewer_details,
            "resolution_status": resolution_status,
            "actor_id": self.id.id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "feedback_received",
        }
        # Example: update the state of the HITL request
        await self._state_manager.set_state(f"hitl_review_{review_request_id}", feedback_event)
        logger.info(f"HITL_FEEDBACK_RECEIVED: {json.dumps(feedback_event)}")
        # Potentially trigger further processing based on feedback
        # if resolution_status == "approved":
        #    await self._resume_task_after_hitl(review_request_id, feedback_payload)
        pass

    # --- Dapr Workflow Interaction (Retained for explicit orchestration if needed) ---
    # Note: These require dapr.clients.DaprClient, which means the actor needs
    # to be able to instantiate it. This is generally fine but adds a dependency.
    async def start_external_workflow(
        self,
        input: dict[str, object]
    ) -> str | None:
        workflow_name = cast(str, input.get("workflow_name"))
        workflow_component_name = cast(str, input.get("workflow_component_name", "dapr"))
        workflow_input = cast(dict[str, object], input.get("workflow_input"))
        workflow_options = cast(dict[str, str], input.get("workflow_options"))
        
        logger.info(
            f"Actor '{self.id.id}' method 'start_external_workflow' for workflow_name: {workflow_name}"
        )
        try:

            with DaprClient() as d:
                instance_id = d.start_workflow(
                    workflow_component=workflow_component_name,
                    workflow_name=workflow_name,
                    input=workflow_input,
                    instance_id=workflow_options.get("instance_id")
                    if workflow_options
                    else None,
                    workflow_options=workflow_options,  # Pass other options like task_queue
                )
                logger.info(
                    f"Actor '{self.id.id}': Started workflow '{workflow_name}' with instance_id '{instance_id}'."
                )
                return instance_id.instance_id
        except Exception as e:
            logger.error(
                f"Actor '{self.id.id}': Failed to start workflow '{workflow_name}': {e}",
                exc_info=True,
            )
            return None

    async def send_event_to_workflow(
        self,
        input: dict[str, object]
    ) -> None:
        workflow_instance_id = cast(str, input.get("workflow_instance_id"))
        event_name = cast(str, input.get("event_name"))
        event_payload = cast(dict[str, object], input.get("event_payload"))
        workflow_component_name = cast(str, input.get("workflow_component_name", "dapr"))
        
        logger.info(
            f"Actor '{self.id.id}' method 'send_event_to_workflow' for instance_id: {workflow_instance_id}, event: {event_name}"
        )
        try:

            with DaprClient() as d:
                d.raise_workflow_event(
                    instance_id=workflow_instance_id,
                    workflow_component=workflow_component_name,
                    event_name=event_name,
                    event_data=event_payload,
                )
                logger.info(
                    f"Actor '{self.id.id}': Sent event '{event_name}' to workflow '{workflow_instance_id}'."
                )
        except Exception as e:
            logger.error(
                f"Actor '{self.id.id}': Failed to send event '{event_name}' to workflow '{workflow_instance_id}': {e}",
                exc_info=True,
            )
        pass

    async def get_external_workflow_status(
        self, 
        input: dict[str, object]
    ) -> dict[str, object] | None:
        workflow_instance_id = cast(str, input.get("workflow_instance_id"))
        workflow_component_name = cast(str, input.get("workflow_component_name", "dapr"))
        logger.info(
            f"Actor '{self.id.id}' method 'get_external_workflow_status' for instance_id: {workflow_instance_id}"
        )
        try:

            with DaprClient() as d:
                resp = d.get_workflow(
                    instance_id=workflow_instance_id,
                    workflow_component=workflow_component_name,
                )
                logger.info(
                    f"Actor '{self.id.id}': Retrieved status for workflow '{workflow_instance_id}'."
                )
                # The response object (WorkflowReference) has attributes like instance_id, runtime_status, etc.
                # Convert to dict for generic return type if needed.
                return {
                    "instance_id": resp.instance_id,
                    "workflow_name": resp.workflow_name,
                    "created_at": resp.created_at.isoformat()
                    if resp.created_at
                    else None,
                    "last_updated_at": resp.last_updated_at.isoformat()
                    if resp.last_updated_at
                    and isinstance(resp.last_updated_at, datetime)
                    else resp.last_updated_at,
                    "runtime_status": resp.runtime_status,
                    "properties": resp.properties,  # Contains input, output, custom_status if set
                }
        except Exception as e:
            logger.error(
                f"Actor '{self.id.id}': Failed to get status for workflow '{workflow_instance_id}': {e}",
                exc_info=True,
            )
            return None

    async def terminate_external_workflow(
        self, 
        input: dict[str, object]
    ) -> None:
        workflow_instance_id = cast(str, input.get("workflow_instance_id"))
        workflow_component_name = cast(str, input.get("workflow_component_name", "dapr"))
        logger.info(
            f"Actor '{self.id.id}' method 'terminate_external_workflow' for instance_id: {workflow_instance_id}"
        )
        try:
            with DaprClient() as d:
                d.terminate_workflow(
                    instance_id=workflow_instance_id,
                    workflow_component=workflow_component_name,
                )
                logger.info(
                    f"Actor '{self.id.id}': Terminated workflow '{workflow_instance_id}'."
                )
        except Exception as e:
            logger.error(
                f"Actor '{self.id.id}': Failed to terminate workflow '{workflow_instance_id}': {e}",
                exc_info=True,
            )
        pass

    # --- Internal Helper Methods ---
    # These methods are for internal use by the BaseActor and are not part of the
    # external BaseActorInterface. They are fundamental for the actor's operation.

    async def _get_actor_state(
        self, state_name: str, default: list[dict[str, str]] | None = []
    ) -> object | list[dict[str, str]] | None:
        """
        Helper to retrieve a specific state value.
        This is a thin wrapper around self._state_manager.get_state() primarily
        for centralized logging and default value handling.
        It could be replaced by direct calls if desired, sacrificing some logging clarity.
        """
        logger.debug(f"Actor '{self.id.id}': Attempting to get state '{state_name}'.")
        try:
            # Dapr's state_manager.get_state returns the value directly if found.
            # It raises a KeyError if not found.
            value = await self._state_manager.get_state(state_name)
            logger.debug(
                f"Actor '{self.id.id}': Retrieved state '{state_name}' successfully."
            )
            return value
        except (
            KeyError
        ):  # Dapr's actor._state_manager.get_state raises KeyError if key not found.
            logger.info(
                f"Actor '{self.id.id}': State '{state_name}' not found, returning default."
            )
            # add a new state with the default value
            await self._state_manager.set_state(state_name, default)
            return default
        except Exception as e:
            logger.error(
                f"Actor '{self.id.id}': Error getting state '{state_name}': {e}",
                exc_info=True,
            )
            return default
        
    async def _create_engine(self, engine_type: str, engine_config: dict[str, str | list]) -> None:
        if engine_type == "openai":
            engine = OpenAIEngineAdapter()
            await engine.initialize(
                agent_name=engine_config.get("name", "DACA Agent"), # type: ignore
                agent_instructions=engine_config.get("instructions", "You are a helpful assistant"), # type: ignore
                agent_tools=engine_config.get("tools", []), # type: ignore
                model=engine_config.get("model", "gpt-4") # type: ignore
            )
            self.agentic_engine = engine
        else:
            raise ValueError(f"Unsupported engine type: {engine_type}")
        
    async def _get_engine(self, engine_config: dict[str, str | list], engine_type: str = "openai") -> AgenticEngineAdapter:
        if self.agentic_engine is None:
            await self._create_engine(engine_type=engine_type, engine_config=engine_config)
        
        if not isinstance(self.agentic_engine, AgenticEngineAdapter):
            raise ValueError("Agentic engine is not properly initialized")
        
        return self.agentic_engine
