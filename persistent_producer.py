class PersistentProducer:
    def __init__(self, stream, store: EventStore):
        self.stream = stream
        self.store = store

    async def send(self, event_type: str, payload: dict):
        event = {
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Persist first
        await self.store.append(event)

        # Then publish
        from_event = Event(event["type"], event["payload"])
        await self.stream.publish(from_event)
