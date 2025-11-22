from typing import Dict, Callable, Any, List

class Event:
    """Represents a simple event with a type and payload."""
    def __init__(self, event_type: str, payload: Dict[str, Any]):
        self.type = event_type
        self.payload = payload

    def __repr__(self):
        return f"Event(type={self.type}, payload={self.payload})"


class EventStream:
    """A lightweight event bus supporting subscription and publishing."""

    def __init__(self):
        # Dictionary: event_type -> list of subscriber callbacks
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Register a callback for a given event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

        def publish(self, event: Event) -> None:
        """Dispatch an event to all registered subscribers."""
        subscribers = self._subscribers.get(event.type, [])
        if not subscribers:
            print(f"(no subscribers for '{event.type}')")
            return

        for callback in subscribers:
            try:
                callback(event)
            except Exception as e:
                print(f"⚠️ Handler error for {event.type}: {e}")


class EventProducer:
    """Simulates a producer that sends events into the EventStream."""

    def __init__(self, stream: EventStream):
        self.stream = stream

    def send(self, event_type: str, payload: Dict[str, Any]) -> None:
        event = Event(event_type, payload)
        self.stream.publish(event)


# --- Example Handlers (Callbacks) ---

def log_handler(event: Event):
    print(f"[LOG] {event.type} -> {event.payload}")

def critical_alert_handler(event: Event):
    if event.payload.get("severity") == "critical":
        print(f"[ALERT] Critical event detected! {event.payload}")


if __name__ == "__main__":
    stream = EventStream()
    producer = EventProducer(stream)

    # Subscribe handlers
    stream.subscribe("vulnerability", log_handler)
    stream.subscribe("vulnerability", critical_alert_handler)
    stream.subscribe("heartbeat", log_handler)

    # Simulate incoming events
    producer.send("vulnerability", {"id": 1, "severity": "low"})
    producer.send("vulnerability", {"id": 2, "severity": "critical"})
    producer.send("heartbeat", {"status": "ok"})