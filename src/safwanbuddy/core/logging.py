import logging
import os
from datetime import datetime

class MemoryHandler(logging.Handler):
    def __init__(self, capacity=100):
        super().__init__()
        self.capacity = capacity
        self.buffer = []

    def emit(self, record):
        msg = self.format(record)
        self.buffer.append(msg)
        if len(self.buffer) > self.capacity:
            self.buffer.pop(0)

    def get_logs(self):
        return self.buffer

def setup_logging(log_level=logging.INFO, log_to_file=True):
    logger = logging.getLogger("SafwanBuddy")
    logger.setLevel(log_level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Memory handler for remote access
    mh = MemoryHandler(capacity=200)
    mh.setFormatter(formatter)
    logger.addHandler(mh)
    logger.memory_handler = mh
    
    if log_to_file:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f"safwanbuddy_{datetime.now().strftime('%Y%m%d')}.log")
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger

logger = setup_logging()
