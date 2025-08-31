import asyncio
from agents import SQLiteSession

async def memory_operations_demo():
    session = SQLiteSession("memory_ops", "test.db")

    # Add some conversation items manually
    conversation_items = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help you?"},
        {"role": "user", "content": "What's the weather like?"},
        {"role": "assistant", "content": "I don't have access to weather data."}
    ]

    await session.add_items(conversation_items)
    print("Added conversation to memory!")

    # View all items in memory
    items = await session.get_items()
    print(f"\nMemory contains {len(items)} items:")
    for item in items:
        print(f"  {item['role']}: {item['content']}")

    # Remove the last item (undo)
    last_item = await session.pop_item()
    print(f"\nRemoved last item: {last_item}")

    # View memory again
    items = await session.get_items()
    print(f"\nMemory now contains {len(items)} items:")
    for item in items:
        print(f"  {item['role']}: {item['content']}")

    # Clear all memory
    await session.clear_session()
    print("\nCleared all memory!")

    # Verify memory is empty
    items = await session.get_items()
    print(f"Memory now contains {len(items)} items")

# Run the async demo
asyncio.run(memory_operations_demo())