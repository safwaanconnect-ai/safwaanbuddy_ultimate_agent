#!/usr/bin/env python3
"""
Event Bus Implementation
Thread-safe event system for SafwanBuddy components
"""

import threading
import queue
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import weakref
import time

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Event data class"""
    name: str
    data: Any = None
    timestamp: datetime = None
    source: str = "unknown"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class EventBus:
    """Thread-safe event bus for inter-component communication"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue = queue.Queue()
        self._processing = False
        self._lock = threading.RLock()
        self._stats = {
            'events_emitted': 0,
            'events_processed': 0,
            'subscribers_count': 0
        }
        
    def subscribe(self, event_name: str, callback: Callable, source: str = "unknown") -> str:
        """
        Subscribe to an event
        
        Args:
            event_name: Name of the event to subscribe to
            callback: Function to call when event is emitted
            source: Source identifier for the subscriber
            
        Returns:
            str: Subscription ID for unsubscribing
        """
        with self._lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            
            # Use weak reference to avoid circular dependencies
            weak_callback = weakref.WeakMethod(callback) if hasattr(callback, '__self__') else weakref.ref(callback)
            subscription_id = f"{event_name}:{id(weak_callback)}:{time.time()}"
            
            self._subscribers[event_name].append({
                'callback': weak_callback,
                'source': source,
                'id': subscription_id,
                'subscribed_at': datetime.now()
            })
            
            self._stats['subscribers_count'] = len(self._subscribers)
            logger.debug(f"Subscribed to '{event_name}' from {source}")
            
            return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from an event
        
        Args:
            subscription_id: ID returned by subscribe()
            
        Returns:
            bool: True if successfully unsubscribed
        """
        with self._lock:
            for event_name, subscribers in self._subscribers.items():
                for i, subscriber in enumerate(subscribers):
                    if subscriber['id'] == subscription_id:
                        del self._subscribers[event_name][i]
                        logger.debug(f"Unsubscribed from '{event_name}'")
                        
                        # Clean up empty event lists
                        if not self._subscribers[event_name]:
                            del self._subscribers[event_name]
                        
                        return True
            
            return False
    
    def unsubscribe_all(self, source: str = None) -> int:
        """
        Unsubscribe all listeners for a source or all listeners
        
        Args:
            source: Source to unsubscribe, or None for all
            
        Returns:
            int: Number of subscriptions removed
        """
        removed_count = 0
        
        with self._lock:
            if source is None:
                # Remove all subscribers
                for event_name in list(self._subscribers.keys()):
                    removed_count += len(self._subscribers[event_name])
                    del self._subscribers[event_name]
                logger.info(f"Removed all {removed_count} subscriptions")
            else:
                # Remove subscribers from specific source
                for event_name, subscribers in list(self._subscribers.items()):
                    for i in range(len(subscribers) - 1, -1, -1):
                        if subscribers[i]['source'] == source:
                            del subscribers[i]
                            removed_count += 1
                    
                    # Clean up empty lists
                    if not subscribers:
                        del self._subscribers[event_name]
                
                logger.debug(f"Removed {removed_count} subscriptions for source '{source}'")
            
            self._stats['subscribers_count'] = sum(len(subs) for subs in self._subscribers.values())
        
        return removed_count
    
    def emit(self, event_name: str, data: Any = None, source: str = "unknown", immediate: bool = False) -> bool:
        """
        Emit an event
        
        Args:
            event_name: Name of the event to emit
            data: Event data to pass to subscribers
            source: Source identifier for the event
            immediate: If True, process immediately; if False, queue for async processing
            
        Returns:
            bool: True if event was emitted successfully
        """
        event = Event(event_name, data, datetime.now(), source)
        
        with self._lock:
            self._stats['events_emitted'] += 1
        
        if immediate or not self._processing:
            # Process immediately
            self._process_event(event)
            return True
        else:
            # Queue for async processing
            try:
                self._event_queue.put(event, timeout=1.0)
                return True
            except queue.Full:
                logger.warning(f"Event queue full, dropping event '{event_name}'")
                return False
    
    def _process_event(self, event: Event):
        """Process an event by calling all subscribers"""
        with self._lock:
            subscribers = self._subscribers.get(event.name, [])
        
        if not subscribers:
            return
        
        # Create a copy of subscribers list to avoid modification during iteration
        current_subscribers = subscribers[:]
        
        for subscriber in current_subscribers:
            try:
                # Get the callback (weak reference)
                callback = subscriber['callback']()
                
                if callback is None:
                    # Callback was garbage collected, remove subscriber
                    self.unsubscribe(subscriber['id'])
                    continue
                
                # Call the callback
                logger.debug(f"Calling subscriber for '{event.name}' from {subscriber['source']}")
                callback(event)
                
            except Exception as e:
                logger.error(f"Error in event subscriber for '{event.name}' from {subscriber['source']}: {e}")
        
        with self._lock:
            self._stats['events_processed'] += 1
    
    def start_processing(self):
        """Start asynchronous event processing"""
        if self._processing:
            return
        
        self._processing = True
        self._processor_thread = threading.Thread(target=self._event_processor, daemon=True)
        self._processor_thread.start()
        logger.info("Event processing started")
    
    def stop_processing(self):
        """Stop asynchronous event processing"""
        if not self._processing:
            return
        
        self._processing = False
        
        # Add a special stop event to wake up the processor
        try:
            self._event_queue.put(Event("__STOP_PROCESSING__", None), timeout=1.0)
        except queue.Full:
            pass
        
        if hasattr(self, '_processor_thread') and self._processor_thread.is_alive():
            self._processor_thread.join(timeout=2.0)
        
        logger.info("Event processing stopped")
    
    def _event_processor(self):
        """Background thread for processing queued events"""
        logger.debug("Event processor thread started")
        
        while self._processing:
            try:
                # Get next event with timeout
                event = self._event_queue.get(timeout=1.0)
                
                # Check for stop signal
                if event.name == "__STOP_PROCESSING__":
                    break
                
                # Process the event
                self._process_event(event)
                
            except queue.Empty:
                # No events to process, continue
                continue
            except Exception as e:
                logger.error(f"Error in event processor: {e}")
        
        logger.debug("Event processor thread stopped")
    
    def process_pending_events(self):
        """Process all pending events immediately"""
        processed = 0
        
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                self._process_event(event)
                processed += 1
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error processing pending event: {e}")
        
        return processed
    
    def clear_queue(self):
        """Clear all pending events from the queue"""
        cleared = 0
        
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
                cleared += 1
            except queue.Empty:
                break
        
        logger.debug(f"Cleared {cleared} events from queue")
        return cleared
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        with self._lock:
            return {
                **self._stats,
                'active_events': len(self._subscribers),
                'queue_size': self._event_queue.qsize(),
                'processing': self._processing
            }
    
    def list_subscribers(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get list of all subscribers"""
        with self._lock:
            result = {}
            for event_name, subscribers in self._subscribers.items():
                result[event_name] = []
                for sub in subscribers:
                    result[event_name].append({
                        'source': sub['source'],
                        'id': sub['id'],
                        'subscribed_at': sub['subscribed_at'].isoformat()
                    })
            return result
    
    def wait_for_event(self, event_name: str, timeout: float = None, data_filter: Callable = None) -> Optional[Event]:
        """
        Wait for a specific event to be emitted
        
        Args:
            event_name: Name of event to wait for
            timeout: Maximum time to wait (None for no timeout)
            data_filter: Optional function to filter event data
            
        Returns:
            Event: The event that was emitted, or None if timeout
        """
        result_queue = queue.Queue()
        
        def event_handler(event):
            if data_filter is None or data_filter(event.data):
                result_queue.put(event)
        
        # Subscribe temporarily
        sub_id = self.subscribe(event_name, event_handler, "wait_for_event")
        
        try:
            # Wait for event
            try:
                event = result_queue.get(timeout=timeout)
                return event
            except queue.Empty:
                return None
        finally:
            # Clean up subscription
            self.unsubscribe(sub_id)
    
    def __enter__(self):
        """Context manager entry"""
        self.start_processing()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_processing()
        self.unsubscribe_all()

# Convenience functions for global event bus usage
_global_event_bus = None

def get_global_event_bus() -> EventBus:
    """Get or create the global event bus instance"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus

def subscribe(event_name: str, callback: Callable, source: str = "unknown") -> str:
    """Subscribe to event on global event bus"""
    return get_global_event_bus().subscribe(event_name, callback, source)

def unsubscribe(subscription_id: str) -> bool:
    """Unsubscribe from global event bus"""
    return get_global_event_bus().unsubscribe(subscription_id)

def emit(event_name: str, data: Any = None, source: str = "unknown", immediate: bool = False) -> bool:
    """Emit event on global event bus"""
    return get_global_event_bus().emit(event_name, data, source, immediate)

def start_global_processing():
    """Start global event bus processing"""
    get_global_event_bus().start_processing()

def stop_global_processing():
    """Stop global event bus processing"""
    get_global_event_bus().stop_processing()