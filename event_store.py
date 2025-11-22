import asyncio
import json
from typing import AsyncIterator
from datetime import datetime


class EventStore:
    """Append-only async event log."""

    def __init__(self, path: str):
        self.path = path
        self._lock = asyncio.Lock()

    async def append(self, event: dict) -> None:
        """Persist event to disk."""
        line = json.dumps(event) + "\n"
        async with self._lock:
            # aiofiles makes this non-blocking
            import aiofiles
            async with aiofiles.open(self.path, "a") as f:
                await f.write(line)

    async def load_events(self) -> AsyncIterator[dict]:
        """Replay stored events."""
        import aiofiles
        async with aiofiles.open(self.path, "r") as f:
            async for line in f:
                yield json.loads(line)

class EventReplayer:
    def __init__(self, stream, store: EventStore):
        self.stream = stream
        self.store = store

    async def replay_all(self):
        async for stored in self.store.load_events():
            event = Event(stored["type"], stored["payload"])
            await self.stream.publish(event)

async def main():
    stream = EventStream()
    store = EventStore("events.log")
    producer = PersistentProducer(stream, store)
    replayer = EventReplayer(stream, store)

    # Subscribe
    await stream.subscribe("vulnerability", async_log_handler)
    await stream.subscribe("vulnerability", critical_async_handler)
    await stream.subscribe("heartbeat", sync_log_handler)

    # Send a few events
    await producer.send("vulnerability", {"id": 1, "severity": "low"})
    await producer.send("vulnerability", {"id": 2, "severity": "critical"})
    await producer.send("heartbeat", {"status": "ok"})

    print("\n--- Replaying stored events ---\n")
    await replayer.replay_all()

asyncio.run(main())
