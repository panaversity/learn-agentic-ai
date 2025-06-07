import logging
from dapr.actor import Actor
from dapr.actor.actor_interface import ActorInterface, actormethod

class UserSessionActorInterface(ActorInterface):
    @actormethod(name="AddMessage")
    async def add_message(self, message_data: dict) -> None:
        ...

    @actormethod(name="GetConversationHistory")
    async def get_conversation_history(self) -> list[dict] | None:
        ...

class UserSessionActor(Actor, UserSessionActorInterface):
    def __init__(self, ctx, actor_id):
        super(UserSessionActor, self).__init__(ctx, actor_id)
        self._history_key = f"history-{actor_id.id}"

    async def _on_activate(self) -> None:
        """Initialize state on actor activation."""
        logging.info(f"Activating actor for {self._history_key}")
        try:
            history = await self._state_manager.get_state(self._history_key)
            if history is None:  # State doesn’t exist yet
                logging.info(f"State not found for {self._history_key}, initializing")
                await self._state_manager.set_state(self._history_key, [])
            else:
                logging.info(f"State found for {self._history_key}: {history}")
        except Exception as e:
            logging.warning(f"Non-critical error in _on_activate for {self._history_key}: {e}")
            # Ensure state is initialized even if get_state fails
            await self._state_manager.set_state(self._history_key, [])

    async def add_message(self, message_data: dict) -> None:
        """Add a message and reply to history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            current_history = history if isinstance(history, list) else []
            current_history.append(message_data)
            if len(current_history) > 5:  # Limit to last 5 messages
                current_history = current_history[-5:]
            await self._state_manager.set_state(self._history_key, current_history)
        except Exception as e:
            logging.error(f"Error adding message for {self._history_key}: {e}")
            raise

    async def get_conversation_history(self) -> list[dict]:
        """Retrieve conversation history."""
        try:
            history = await self._state_manager.get_state(self._history_key)
            return history if isinstance(history, list) else []
        except Exception as e:
            logging.error(f"Error getting history for {self._history_key}: {e}")
            return []