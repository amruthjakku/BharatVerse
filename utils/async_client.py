"""
Async API Client for BharatVerse
Handles parallel API calls and async operations for better performance
"""

import asyncio
import aiohttp
import streamlit as st
from typing import List, Dict, Any, Optional, Callable
import logging
from datetime import datetime
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools

logger = logging.getLogger(__name__)

class AsyncAPIClient:
    """
    Async API client for parallel operations
    Optimized for cloud deployment with rate limiting and error handling
    """
    
    def __init__(self, max_concurrent_requests: int = 5, timeout: int = 30):
        self.max_concurrent_requests = max_concurrent_requests
        self.timeout = timeout
        self.session = None
        self.rate_limiter = asyncio.Semaphore(max_concurrent_requests)
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent_requests,
            limit_per_host=self.max_concurrent_requests,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'BharatVerse/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make an async HTTP request with rate limiting
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request parameters
            
        Returns:
            Response data as dictionary
        """
        async with self.rate_limiter:
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        if response.content_type == 'application/json':
                            return await response.json()
                        else:
                            text = await response.text()
                            return {"text": text, "status": "success"}
                    else:
                        error_text = await response.text()
                        return {
                            "error": f"HTTP {response.status}: {error_text}",
                            "status": "error"
                        }
            except asyncio.TimeoutError:
                return {"error": "Request timeout", "status": "error"}
            except Exception as e:
                return {"error": str(e), "status": "error"}
    
    async def batch_requests(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple requests in parallel
        
        Args:
            requests: List of request dictionaries with 'method', 'url', and optional params
            
        Returns:
            List of response dictionaries
        """
        tasks = []
        for req in requests:
            method = req.get('method', 'GET')
            url = req['url']
            params = {k: v for k, v in req.items() if k not in ['method', 'url']}
            
            task = self.make_request(method, url, **params)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error dictionaries
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "status": "error"
                })
            else:
                processed_results.append(result)
        
        return processed_results

class ParallelProcessor:
    """
    Parallel processor for CPU-bound tasks using ThreadPoolExecutor
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
    
    def parallel_execute(self, func: Callable, tasks: List[Any], 
                        timeout: int = 60) -> List[Any]:
        """
        Execute function in parallel with multiple inputs
        
        Args:
            func: Function to execute
            tasks: List of inputs for the function
            timeout: Timeout for each task
            
        Returns:
            List of results
        """
        futures = []
        results = []
        
        # Submit all tasks
        for task in tasks:
            if isinstance(task, (list, tuple)):
                future = self.executor.submit(func, *task)
            else:
                future = self.executor.submit(func, task)
            futures.append(future)
        
        # Collect results
        for future in as_completed(futures, timeout=timeout):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Parallel task failed: {e}")
                results.append({"error": str(e), "status": "error"})
        
        return results

# Streamlit integration functions
@st.cache_data(ttl=1800, show_spinner=False)
def cached_parallel_api_calls(api_configs: List[Dict], cache_key: str = None):
    """
    Execute parallel API calls with Streamlit caching
    
    Args:
        api_configs: List of API configuration dictionaries
        cache_key: Optional cache key for better cache management
        
    Returns:
        List of API responses
    """
    return run_parallel_api_calls(api_configs)

def run_parallel_api_calls(api_configs: List[Dict]) -> List[Dict]:
    """
    Run parallel API calls synchronously (for Streamlit compatibility)
    
    Args:
        api_configs: List of API configuration dictionaries
        
    Returns:
        List of API responses
    """
    async def _run_async():
        async with AsyncAPIClient() as client:
            return await client.batch_requests(api_configs)
    
    # Run async code in sync context
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, _run_async())
                return future.result(timeout=60)
        else:
            return asyncio.run(_run_async())
    except Exception as e:
        logger.error(f"Parallel API calls failed: {e}")
        return [{"error": str(e), "status": "error"} for _ in api_configs]

def warm_up_apis(api_endpoints: List[str], timeout: int = 10) -> Dict[str, bool]:
    """
    Warm up API endpoints to avoid cold starts
    
    Args:
        api_endpoints: List of API endpoint URLs
        timeout: Timeout for each request
        
    Returns:
        Dictionary mapping endpoint to success status
    """
    warmup_configs = [
        {
            "method": "GET",
            "url": endpoint,
            "timeout": timeout
        }
        for endpoint in api_endpoints
    ]
    
    results = run_parallel_api_calls(warmup_configs)
    
    warmup_status = {}
    for endpoint, result in zip(api_endpoints, results):
        warmup_status[endpoint] = result.get("status") != "error"
    
    return warmup_status

# Performance monitoring decorators
def async_performance_monitor(func):
    """Decorator to monitor async function performance"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Store metrics in session state
            if "async_performance_metrics" not in st.session_state:
                st.session_state.async_performance_metrics = {}
            
            st.session_state.async_performance_metrics[func.__name__] = {
                "last_execution_time": execution_time,
                "last_executed": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"Async {func.__name__} completed in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            if "async_performance_metrics" not in st.session_state:
                st.session_state.async_performance_metrics = {}
            
            st.session_state.async_performance_metrics[func.__name__] = {
                "last_execution_time": execution_time,
                "last_executed": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
            
            logger.error(f"Async {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

def parallel_performance_monitor(func):
    """Decorator to monitor parallel function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Store metrics in session state
            if "parallel_performance_metrics" not in st.session_state:
                st.session_state.parallel_performance_metrics = {}
            
            st.session_state.parallel_performance_metrics[func.__name__] = {
                "last_execution_time": execution_time,
                "last_executed": datetime.now().isoformat(),
                "success": True
            }
            
            logger.info(f"Parallel {func.__name__} completed in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            if "parallel_performance_metrics" not in st.session_state:
                st.session_state.parallel_performance_metrics = {}
            
            st.session_state.parallel_performance_metrics[func.__name__] = {
                "last_execution_time": execution_time,
                "last_executed": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
            
            logger.error(f"Parallel {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

# Utility functions for common patterns
@parallel_performance_monitor
def parallel_ai_inference(texts: List[str], model_endpoint: str) -> List[Dict]:
    """
    Run AI inference on multiple texts in parallel
    
    Args:
        texts: List of text inputs
        model_endpoint: AI model endpoint URL
        
    Returns:
        List of inference results
    """
    api_configs = []
    for text in texts:
        api_configs.append({
            "method": "POST",
            "url": model_endpoint,
            "json": {"text": text}
        })
    
    return run_parallel_api_calls(api_configs)

@parallel_performance_monitor
def parallel_database_queries(queries: List[Dict]) -> List[Any]:
    """
    Execute multiple database queries in parallel
    
    Args:
        queries: List of query dictionaries with 'query' and 'params'
        
    Returns:
        List of query results
    """
    from utils.supabase_db import get_database_manager
    
    db_manager = get_database_manager()
    if not db_manager:
        return []
    
    def execute_query(query_config):
        return db_manager.execute_query(
            query_config['query'], 
            query_config.get('params', {})
        )
    
    with ParallelProcessor() as processor:
        return processor.parallel_execute(execute_query, queries)

# Example usage functions
def example_parallel_api_usage():
    """Example of how to use parallel API calls"""
    api_configs = [
        {
            "method": "GET",
            "url": "https://api.example1.com/data"
        },
        {
            "method": "POST",
            "url": "https://api.example2.com/process",
            "json": {"input": "test data"}
        },
        {
            "method": "GET",
            "url": "https://api.example3.com/status"
        }
    ]
    
    # Execute in parallel with caching
    results = cached_parallel_api_calls(api_configs, cache_key="example_batch")
    
    return results

def example_parallel_processing():
    """Example of parallel CPU-bound processing"""
    def process_item(item):
        # Simulate CPU-bound work
        import time
        time.sleep(0.1)
        return {"processed": item, "timestamp": datetime.now().isoformat()}
    
    items = ["item1", "item2", "item3", "item4", "item5"]
    
    with ParallelProcessor(max_workers=3) as processor:
        results = processor.parallel_execute(process_item, items)
    
    return results