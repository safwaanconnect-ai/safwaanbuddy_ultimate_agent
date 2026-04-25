import concurrent.futures
from src.safwanbuddy.core import logger, event_bus

class MultitaskingEngine:
    def __init__(self, max_workers: int = 5):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def submit_task(self, func, *args, **kwargs):
        """Submits a task to the thread pool."""
        task_name = kwargs.pop('task_name', func.__name__)
        event_bus.emit("task_submitted", {"name": task_name})
        future = self.executor.submit(func, *args, **kwargs)
        future._task_name = task_name # Attach name for callback
        future.add_done_callback(self._task_done_callback)
        self.futures.append(future)
        return future

    def _task_done_callback(self, future):
        task_name = getattr(future, '_task_name', 'unknown')
        try:
            result = future.result()
            event_bus.emit("task_completed", {"name": task_name, "result": result})
        except Exception as e:
            logger.error(f"Task '{task_name}' failed: {e}")
            event_bus.emit("task_failed", {"name": task_name, "error": str(e)})
        finally:
            if future in self.futures:
                self.futures.remove(future)

    def shutdown(self, wait=True):
        """Shuts down the executor."""
        self.executor.shutdown(wait=wait)
        logger.info("Multitasking engine shut down.")

    def cancel_all(self):
        for future in self.futures:
            future.cancel()
        self.futures = []
        logger.info("All tasks cancelled.")

multitasking_engine = MultitaskingEngine()
