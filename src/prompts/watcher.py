import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from loguru import logger
from src.prompts.loader import prompt_loader
from src.security.audit import log_audit_event

class PromptChangeHandler(FileSystemEventHandler):
    def __init__(self, callback=None):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.yaml', '.yml')):
            logger.info(f"Detected change in prompt file: {event.src_path}")
            # Reload all prompts
            prompt_loader.load_all()
            log_audit_event("PROMPT_RELOADED", {"file": os.path.basename(event.src_path)})
            if self.callback:
                self.callback()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.yaml', '.yml')):
            logger.info(f"New prompt file detected: {event.src_path}")
            prompt_loader.load_all()
            log_audit_event("PROMPT_CREATED", {"file": os.path.basename(event.src_path)})
            if self.callback:
                self.callback()

class PromptWatcher:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self.observer = Observer()
        self.callbacks = []
        self._started = False

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def _trigger_callbacks(self):
        for cb in self.callbacks:
            try:
                cb()
            except Exception as e:
                logger.error(f"Error in prompt watcher callback: {e}")

    def start(self):
        # Initial load
        logger.info(f"Initializing prompt watcher on: {self.prompts_dir}")
        try:
            prompt_loader.load_all()
            
            if not os.path.exists(self.prompts_dir):
                logger.error(f"Prompts directory does not exist: {self.prompts_dir}")
                return

            event_handler = PromptChangeHandler(callback=self._trigger_callbacks)
            self.observer.schedule(event_handler, self.prompts_dir, recursive=False)
            self.observer.start()
            self._started = True
            logger.info("Prompt watcher thread started successfully.")
        except Exception as e:
            logger.error(f"Failed to start prompt watcher: {e}")

    def stop(self):
        if self._started:
            logger.info("Stopping prompt watcher...")
            self.observer.stop()
            self.observer.join()
            self._started = False

# Global watcher instance
prompt_watcher = PromptWatcher()
