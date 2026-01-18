import concurrent.futures
from src.safwanbuddy.core.logging import logger
from src.safwanbuddy.core.events import event_bus

class MultitaskingEngine:
    def __init__(self, max_workers: int = 5):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def submit_task(self, func, *args, **kwargs):
        event_bus.emit("task_submitted")
        future = self.executor.submit(func, *args, **kwargs)
        future.add_done_callback(self._task_done_callback)
        self.futures.append(future)
        return future

    def _task_done_callback(self, future):
        try:
            result = future.result()
            event_bus.emit("task_completed", result)
        except Exception as e:
            logger.error(f"Task failed: {e}")
            event_bus.emit("task_failed", str(e))

multitasking_engine = MultitaskingEngine()
