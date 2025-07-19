#!/usr/bin/env python3
"""
Performance Testing Script for BharatVerse
Tests various performance optimizations and measures improvements
"""

import sys
import time
import asyncio
import statistics
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import performance utilities
from utils.performance_optimizer import get_performance_optimizer
from utils.async_client import AsyncAPIClient, ParallelProcessor
from utils.memory_manager import get_memory_manager, MemoryTracker
from utils.redis_cache import get_cache_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceTestSuite:
    """
    Comprehensive performance testing suite
    """
    
    def __init__(self):
        self.results = {}
        self.optimizer = get_performance_optimizer()
        self.memory_manager = get_memory_manager()
        self.cache_manager = get_cache_manager()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests"""
        logger.info("Starting performance test suite...")
        
        # Test categories
        test_categories = [
            ("Cache Performance", self.test_cache_performance),
            ("Memory Management", self.test_memory_management),
            ("Parallel Processing", self.test_parallel_processing),
            ("Database Operations", self.test_database_performance),
            ("API Client Performance", self.test_api_client_performance),
        ]
        
        for category, test_func in test_categories:
            logger.info(f"Running {category} tests...")
            try:
                self.results[category] = test_func()
                logger.info(f"✅ {category} tests completed")
            except Exception as e:
                logger.error(f"❌ {category} tests failed: {e}")
                self.results[category] = {"error": str(e)}
        
        # Generate summary
        self.results["summary"] = self.generate_summary()
        
        return self.results
    
    def test_cache_performance(self) -> Dict[str, Any]:
        """Test caching performance"""
        results = {}
        
        if not self.cache_manager or not self.cache_manager.is_connected():
            return {"error": "Redis cache not available"}
        
        # Test cache write performance
        write_times = []
        for i in range(100):
            start_time = time.time()
            self.cache_manager.set(f"test_key_{i}", f"test_value_{i}", 60)
            write_times.append(time.time() - start_time)
        
        results["cache_write"] = {
            "avg_time_ms": statistics.mean(write_times) * 1000,
            "min_time_ms": min(write_times) * 1000,
            "max_time_ms": max(write_times) * 1000,
            "operations": len(write_times)
        }
        
        # Test cache read performance
        read_times = []
        for i in range(100):
            start_time = time.time()
            self.cache_manager.get(f"test_key_{i}")
            read_times.append(time.time() - start_time)
        
        results["cache_read"] = {
            "avg_time_ms": statistics.mean(read_times) * 1000,
            "min_time_ms": min(read_times) * 1000,
            "max_time_ms": max(read_times) * 1000,
            "operations": len(read_times)
        }
        
        # Test cache hit rate
        hits = 0
        for i in range(100):
            if self.cache_manager.get(f"test_key_{i}") is not None:
                hits += 1
        
        results["cache_hit_rate"] = hits / 100 * 100
        
        # Cleanup test keys
        for i in range(100):
            self.cache_manager.delete(f"test_key_{i}")
        
        return results
    
    def test_memory_management(self) -> Dict[str, Any]:
        """Test memory management performance"""
        results = {}
        
        # Test memory tracking
        with MemoryTracker("memory_test") as tracker:
            # Create some memory-intensive operations
            large_list = [i for i in range(100000)]
            large_dict = {i: f"value_{i}" for i in range(10000)}
            
            # Simulate DataFrame operations
            import pandas as pd
            df = pd.DataFrame({
                'col1': range(10000),
                'col2': [f"text_{i}" for i in range(10000)],
                'col3': [i * 1.5 for i in range(10000)]
            })
            
            # Optimize DataFrame
            optimized_df = self.memory_manager.optimize_dataframe(df)
            
            # Clean up
            del large_list, large_dict, df
        
        results["memory_delta_mb"] = tracker.get_memory_delta()
        results["memory_tracking"] = "success"
        
        # Test memory cleanup
        cleanup_result = self.memory_manager.cleanup_memory(force=True)
        results["memory_cleanup"] = cleanup_result
        
        # Test memory usage monitoring
        memory_usage = self.memory_manager.get_memory_usage()
        results["current_memory_mb"] = memory_usage["rss_mb"]
        results["memory_percent"] = memory_usage["percent"]
        
        return results
    
    def test_parallel_processing(self) -> Dict[str, Any]:
        """Test parallel processing performance"""
        results = {}
        
        def cpu_intensive_task(n):
            """Simulate CPU-intensive work"""
            total = 0
            for i in range(n):
                total += i ** 2
            return total
        
        # Test sequential processing
        start_time = time.time()
        sequential_results = []
        for i in range(10):
            sequential_results.append(cpu_intensive_task(10000))
        sequential_time = time.time() - start_time
        
        # Test parallel processing
        start_time = time.time()
        with ParallelProcessor(max_workers=4) as processor:
            parallel_results = processor.parallel_execute(
                cpu_intensive_task, 
                [10000] * 10
            )
        parallel_time = time.time() - start_time
        
        results["sequential_time_s"] = sequential_time
        results["parallel_time_s"] = parallel_time
        results["speedup_factor"] = sequential_time / parallel_time if parallel_time > 0 else 0
        results["parallel_efficiency"] = len([r for r in parallel_results if isinstance(r, int)]) / len(parallel_results) * 100
        
        return results
    
    def test_database_performance(self) -> Dict[str, Any]:
        """Test database operation performance"""
        results = {}
        
        try:
            from utils.supabase_db import get_database_manager
            
            db_manager = get_database_manager()
            if not db_manager:
                return {"error": "Database not available"}
            
            # Test simple query performance
            query_times = []
            for _ in range(10):
                start_time = time.time()
                db_manager.execute_query("SELECT 1")
                query_times.append(time.time() - start_time)
            
            results["simple_query"] = {
                "avg_time_ms": statistics.mean(query_times) * 1000,
                "min_time_ms": min(query_times) * 1000,
                "max_time_ms": max(query_times) * 1000
            }
            
            # Test connection pool performance
            connection_times = []
            for _ in range(5):
                start_time = time.time()
                with db_manager.get_connection() as conn:
                    pass
                connection_times.append(time.time() - start_time)
            
            results["connection_pool"] = {
                "avg_time_ms": statistics.mean(connection_times) * 1000,
                "operations": len(connection_times)
            }
            
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    def test_api_client_performance(self) -> Dict[str, Any]:
        """Test async API client performance"""
        results = {}
        
        async def test_async_operations():
            # Test single request
            start_time = time.time()
            async with AsyncAPIClient() as client:
                response = await client.make_request("GET", "https://httpbin.org/delay/1")
            single_request_time = time.time() - start_time
            
            # Test parallel requests
            start_time = time.time()
            async with AsyncAPIClient() as client:
                requests = [
                    {"method": "GET", "url": "https://httpbin.org/delay/1"},
                    {"method": "GET", "url": "https://httpbin.org/delay/1"},
                    {"method": "GET", "url": "https://httpbin.org/delay/1"},
                ]
                responses = await client.batch_requests(requests)
            parallel_requests_time = time.time() - start_time
            
            return {
                "single_request_time_s": single_request_time,
                "parallel_requests_time_s": parallel_requests_time,
                "parallel_efficiency": single_request_time * 3 / parallel_requests_time if parallel_requests_time > 0 else 0,
                "successful_responses": len([r for r in responses if r.get("status") != "error"])
            }
        
        try:
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(test_async_operations())
            loop.close()
        except Exception as e:
            results = {"error": str(e)}
        
        return results
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate performance test summary"""
        summary = {
            "total_tests": len(self.results),
            "successful_tests": 0,
            "failed_tests": 0,
            "performance_score": 0,
            "recommendations": []
        }
        
        for category, result in self.results.items():
            if category == "summary":
                continue
                
            if "error" in result:
                summary["failed_tests"] += 1
            else:
                summary["successful_tests"] += 1
        
        # Calculate performance score (0-100)
        score_components = []
        
        # Cache performance score
        if "Cache Performance" in self.results and "error" not in self.results["Cache Performance"]:
            cache_result = self.results["Cache Performance"]
            if cache_result.get("cache_hit_rate", 0) > 90:
                score_components.append(20)
            elif cache_result.get("cache_hit_rate", 0) > 70:
                score_components.append(15)
            else:
                score_components.append(10)
        
        # Memory management score
        if "Memory Management" in self.results and "error" not in self.results["Memory Management"]:
            memory_result = self.results["Memory Management"]
            if memory_result.get("current_memory_mb", 1000) < 300:
                score_components.append(20)
            elif memory_result.get("current_memory_mb", 1000) < 500:
                score_components.append(15)
            else:
                score_components.append(10)
        
        # Parallel processing score
        if "Parallel Processing" in self.results and "error" not in self.results["Parallel Processing"]:
            parallel_result = self.results["Parallel Processing"]
            speedup = parallel_result.get("speedup_factor", 1)
            if speedup > 2:
                score_components.append(20)
            elif speedup > 1.5:
                score_components.append(15)
            else:
                score_components.append(10)
        
        # Database performance score
        if "Database Operations" in self.results and "error" not in self.results["Database Operations"]:
            db_result = self.results["Database Operations"]
            if "simple_query" in db_result:
                avg_time = db_result["simple_query"].get("avg_time_ms", 1000)
                if avg_time < 50:
                    score_components.append(20)
                elif avg_time < 100:
                    score_components.append(15)
                else:
                    score_components.append(10)
        
        # API client performance score
        if "API Client Performance" in self.results and "error" not in self.results["API Client Performance"]:
            api_result = self.results["API Client Performance"]
            efficiency = api_result.get("parallel_efficiency", 1)
            if efficiency > 2:
                score_components.append(20)
            elif efficiency > 1.5:
                score_components.append(15)
            else:
                score_components.append(10)
        
        summary["performance_score"] = sum(score_components) if score_components else 0
        
        # Generate recommendations
        if summary["performance_score"] < 60:
            summary["recommendations"].append("Consider optimizing caching strategies")
            summary["recommendations"].append("Review memory usage patterns")
            summary["recommendations"].append("Implement more parallel processing")
        elif summary["performance_score"] < 80:
            summary["recommendations"].append("Fine-tune existing optimizations")
            summary["recommendations"].append("Monitor performance metrics regularly")
        else:
            summary["recommendations"].append("Performance is excellent!")
            summary["recommendations"].append("Continue monitoring for regressions")
        
        return summary
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "="*60)
        print("BHARATVERSE PERFORMANCE TEST RESULTS")
        print("="*60)
        
        for category, result in self.results.items():
            if category == "summary":
                continue
                
            print(f"\n📊 {category}")
            print("-" * 40)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                for key, value in result.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for subkey, subvalue in value.items():
                            print(f"    {subkey}: {subvalue}")
                    else:
                        print(f"  {key}: {value}")
        
        # Print summary
        if "summary" in self.results:
            summary = self.results["summary"]
            print(f"\n🎯 SUMMARY")
            print("-" * 40)
            print(f"Performance Score: {summary['performance_score']}/100")
            print(f"Successful Tests: {summary['successful_tests']}")
            print(f"Failed Tests: {summary['failed_tests']}")
            
            print("\n💡 Recommendations:")
            for rec in summary["recommendations"]:
                print(f"  • {rec}")
        
        print("\n" + "="*60)

def main():
    """Run performance tests"""
    test_suite = PerformanceTestSuite()
    results = test_suite.run_all_tests()
    test_suite.print_results()
    
    # Save results to file
    import json
    from datetime import datetime
    
    results_file = project_root / "performance_test_results.json"
    results["test_timestamp"] = datetime.now().isoformat()
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Results saved to: {results_file}")

if __name__ == "__main__":
    main()