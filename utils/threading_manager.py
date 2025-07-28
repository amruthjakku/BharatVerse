"""
Multithreading Manager for BharatVerse
Provides thread pool management and async utilities for improved performance
"""

import threading
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional, Union
import time
import logging
from functools import wraps
import queue
import streamlit as st
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreadingManager:
    """Centralized threading manager for BharatVerse"""
    
    def __init__(self, max_workers: int = None):
        """Initialize threading manager with configurable worker count"""
        # Auto-detect optimal worker count if not specified
        if max_workers is None:
            import os
            max_workers = min(32, (os.cpu_count() or 1) + 4)
        
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = {}
        self.task_counter = 0
        self._lock = threading.Lock()
        
        logger.info(f"ThreadingManager initialized with {max_workers} workers")
    
    def submit_task(self, func: Callable, *args, task_name: str = None, **kwargs) -> concurrent.futures.Future:
        """Submit a task to the thread pool"""
        with self._lock:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
            
        if task_name is None:
            task_name = f"{func.__name__}_{task_id}"
        
        future = self.executor.submit(func, *args, **kwargs)
        self.active_tasks[task_id] = {
            'future': future,
            'name': task_name,
            'start_time': time.time()
        }
        
        # Clean up completed tasks
        def cleanup_task(fut):
            with self._lock:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
        
        future.add_done_callback(cleanup_task)
        return future
    
    def submit_batch(self, func: Callable, items: List[Any], task_name: str = "batch_task") -> List[concurrent.futures.Future]:
        """Submit multiple tasks as a batch"""
        futures = []
        for i, item in enumerate(items):
            future = self.submit_task(func, item, task_name=f"{task_name}_{i}")
            futures.append(future)
        return futures
    
    def wait_for_completion(self, futures: List[concurrent.futures.Future], timeout: float = None) -> List[Any]:
        """Wait for all futures to complete and return results"""
        results = []
        for future in as_completed(futures, timeout=timeout):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Task failed: {e}")
                results.append(None)
        return results
    
    def get_active_tasks(self) -> Dict[str, Dict]:
        """Get information about currently active tasks"""
        with self._lock:
            return {
                task_id: {
                    'name': info['name'],
                    'running_time': time.time() - info['start_time'],
                    'done': info['future'].done()
                }
                for task_id, info in self.active_tasks.items()
            }
    
    def shutdown(self, wait: bool = True):
        """Shutdown the thread pool"""
        self.executor.shutdown(wait=wait)
        logger.info("ThreadingManager shutdown complete")

# Global threading manager instance
_threading_manager = None

def get_threading_manager() -> ThreadingManager:
    """Get the global threading manager instance"""
    global _threading_manager
    if _threading_manager is None:
        # Get max workers from environment or config
        import os
        max_workers = int(os.getenv('MAX_THREAD_WORKERS', 0)) or None
        _threading_manager = ThreadingManager(max_workers=max_workers)
    return _threading_manager

def threaded_task(task_name: str = None):
    """Decorator to automatically run a function in a separate thread"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            manager = get_threading_manager()
            return manager.submit_task(func, *args, task_name=task_name, **kwargs)
        return wrapper
    return decorator

def parallel_map(func: Callable, items: List[Any], max_workers: int = None, timeout: float = None) -> List[Any]:
    """Execute function on list of items in parallel"""
    if not items:
        return []
    
    if max_workers is None:
        max_workers = min(len(items), get_threading_manager().max_workers)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func, item) for item in items]
        results = []
        
        for future in as_completed(futures, timeout=timeout):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Parallel task failed: {e}")
                results.append(None)
        
        return results

def parallel_process_with_progress(func: Callable, items: List[Any], 
                                 progress_callback: Callable = None,
                                 max_workers: int = None) -> List[Any]:
    """Execute function on items in parallel with progress tracking"""
    if not items:
        return []
    
    if max_workers is None:
        max_workers = min(len(items), get_threading_manager().max_workers)
    
    results = [None] * len(items)
    completed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(func, item): i 
            for i, item in enumerate(items)
        }
        
        # Process completed tasks
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                results[index] = result
            except Exception as e:
                logger.error(f"Task {index} failed: {e}")
                results[index] = None
            
            completed += 1
            if progress_callback:
                progress_callback(completed, len(items))
    
    return results

class AsyncTaskQueue:
    """Asynchronous task queue for background processing"""
    
    def __init__(self, max_workers: int = 4):
        self.queue = queue.Queue()
        self.workers = []
        self.max_workers = max_workers
        self.running = False
        self.results = {}
        self._lock = threading.Lock()
    
    def start(self):
        """Start the worker threads"""
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"AsyncTaskQueue started with {self.max_workers} workers")
    
    def stop(self):
        """Stop the worker threads"""
        self.running = False
        # Add sentinel values to wake up workers
        for _ in range(self.max_workers):
            self.queue.put(None)
        
        for worker in self.workers:
            worker.join()
        
        self.workers.clear()
        logger.info("AsyncTaskQueue stopped")
    
    def _worker(self):
        """Worker thread function"""
        while self.running:
            try:
                item = self.queue.get(timeout=1)
                if item is None:  # Sentinel value
                    break
                
                task_id, func, args, kwargs = item
                try:
                    result = func(*args, **kwargs)
                    with self._lock:
                        self.results[task_id] = {'status': 'completed', 'result': result}
                except Exception as e:
                    with self._lock:
                        self.results[task_id] = {'status': 'error', 'error': str(e)}
                
                self.queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def submit(self, func: Callable, *args, task_id: str = None, **kwargs) -> str:
        """Submit a task to the queue"""
        if not self.running:
            self.start()
        
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000)}"
        
        with self._lock:
            self.results[task_id] = {'status': 'queued'}
        
        self.queue.put((task_id, func, args, kwargs))
        return task_id
    
    def get_result(self, task_id: str) -> Optional[Dict]:
        """Get result for a task"""
        with self._lock:
            return self.results.get(task_id)
    
    def get_status(self, task_id: str) -> str:
        """Get status of a task"""
        result = self.get_result(task_id)
        return result['status'] if result else 'not_found'

# Global async task queue
_async_queue = None

def get_async_queue() -> AsyncTaskQueue:
    """Get the global async task queue"""
    global _async_queue
    if _async_queue is None:
        _async_queue = AsyncTaskQueue()
    return _async_queue

@contextmanager
def thread_pool_context(max_workers: int = None):
    """Context manager for temporary thread pool"""
    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        yield executor
    finally:
        executor.shutdown(wait=True)

def batch_process_files(file_processor: Callable, files: List[Any], 
                       batch_size: int = 5, max_workers: int = None) -> List[Any]:
    """Process files in batches with multithreading"""
    if not files:
        return []
    
    # Split files into batches
    batches = [files[i:i + batch_size] for i in range(0, len(files), batch_size)]
    
    def process_batch(batch):
        return parallel_map(file_processor, batch, max_workers=max_workers)
    
    # Process batches in parallel
    batch_results = parallel_map(process_batch, batches, max_workers=len(batches))
    
    # Flatten results
    results = []
    for batch_result in batch_results:
        if batch_result:
            results.extend(batch_result)
    
    return results

def streamlit_threaded_operation(operation: Callable, *args, 
                                progress_text: str = "Processing...",
                                success_text: str = "Operation completed!",
                                **kwargs):
    """Execute operation in thread with Streamlit progress indication"""
    
    # Create progress indicators
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text(progress_text)
    
    def update_progress(current, total):
        progress = current / total if total > 0 else 0
        progress_bar.progress(progress)
        status_text.text(f"{progress_text} ({current}/{total})")
    
    try:
        # Submit task to thread pool
        manager = get_threading_manager()
        future = manager.submit_task(operation, *args, **kwargs)
        
        # Wait for completion with periodic updates
        start_time = time.time()
        while not future.done():
            elapsed = time.time() - start_time
            progress_bar.progress(min(elapsed / 10.0, 0.9))  # Fake progress up to 90%
            time.sleep(0.1)
        
        # Get result
        result = future.result()
        
        # Complete progress
        progress_bar.progress(1.0)
        status_text.text(success_text)
        
        # Clean up UI elements after a short delay
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return result
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"Operation failed: {e}")
        return None

# Performance monitoring for threading
class ThreadingMetrics:
    """Monitor threading performance"""
    
    def __init__(self):
        self.task_times = []
        self.active_threads = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self._lock = threading.Lock()
    
    def record_task_start(self):
        with self._lock:
            self.active_threads += 1
    
    def record_task_completion(self, duration: float, success: bool = True):
        with self._lock:
            self.active_threads -= 1
            self.task_times.append(duration)
            if success:
                self.completed_tasks += 1
            else:
                self.failed_tasks += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            avg_time = sum(self.task_times) / len(self.task_times) if self.task_times else 0
            return {
                'active_threads': self.active_threads,
                'completed_tasks': self.completed_tasks,
                'failed_tasks': self.failed_tasks,
                'average_task_time': avg_time,
                'total_tasks': len(self.task_times)
            }

# Global metrics instance
_threading_metrics = ThreadingMetrics()

def get_threading_metrics() -> ThreadingMetrics:
    """Get the global threading metrics instance"""
    return _threading_metrics

def monitored_task(func: Callable):
    """Decorator to monitor task performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        metrics = get_threading_metrics()
        metrics.record_task_start()
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            metrics.record_task_completion(duration, success=True)
            return result
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_task_completion(duration, success=False)
            raise e
    
    return wrapper

# Cleanup function for graceful shutdown
def cleanup_threading():
    """Clean up threading resources"""
    global _threading_manager, _async_queue
    
    if _threading_manager:
        _threading_manager.shutdown()
        _threading_manager = None
    
    if _async_queue:
        _async_queue.stop()
        _async_queue = None
    
    logger.info("Threading cleanup completed")

# Register cleanup function
import atexit
atexit.register(cleanup_threading)