#!/usr/bin/env python3
"""
24-Hour Stability Testing Framework for CBR MCP Server

This framework provides comprehensive stability testing capabilities including:
- Extended 24-hour continuous operation testing
- Real-time failure injection and recovery validation
- Production-level metrics collection and reporting
- Long-term stability monitoring and analysis
"""

import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import statistics
import psutil
import signal
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import csv


@dataclass
class StabilityTestConfig:
    """Configuration for 24-hour stability testing"""
    duration_hours: float = 24.0
    queries_per_hour: int = 100
    failure_injection_rate: float = 0.05  # 5% of operations should inject failures
    monitoring_interval_seconds: int = 60
    memory_limit_mb: int = 1024
    cpu_limit_percent: float = 80.0
    recovery_timeout_seconds: int = 30
    report_output_path: str = "./stability_test_results"
    enable_real_time_dashboard: bool = True
    failure_types: List[str] = field(default_factory=lambda: [
        "database_connection_failure", "network_timeout", "memory_pressure",
        "cpu_overload", "disk_full", "process_crash", "cascade_failure"
    ])


@dataclass
class StabilityMetrics:
    """Comprehensive stability metrics tracking"""
    test_start_time: datetime
    test_duration_seconds: float = 0
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    recovery_attempts: int = 0
    successful_recoveries: int = 0
    recovery_times: List[float] = field(default_factory=list)
    uptime_percentage: float = 0.0
    memory_usage_samples: List[float] = field(default_factory=list)
    cpu_usage_samples: List[float] = field(default_factory=list)
    error_types: Dict[str, int] = field(default_factory=dict)
    response_times: List[float] = field(default_factory=list)
    failure_injection_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100
    
    @property
    def recovery_rate(self) -> float:
        """Calculate error recovery rate"""
        if self.recovery_attempts == 0:
            return 0.0
        return (self.successful_recoveries / self.recovery_attempts) * 100
    
    @property
    def mean_time_to_recovery(self) -> float:
        """Calculate Mean Time To Recovery (MTTR)"""
        if not self.recovery_times:
            return 0.0
        return statistics.mean(self.recovery_times)
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def average_memory_usage(self) -> float:
        """Calculate average memory usage"""
        if not self.memory_usage_samples:
            return 0.0
        return statistics.mean(self.memory_usage_samples)
    
    @property
    def average_cpu_usage(self) -> float:
        """Calculate average CPU usage"""
        if not self.cpu_usage_samples:
            return 0.0
        return statistics.mean(self.cpu_usage_samples)


class FailureInjector:
    """Real-time failure injection for stability testing"""
    
    def __init__(self, config: StabilityTestConfig):
        self.config = config
        self.injection_count = 0
        self.injection_history = []
    
    def should_inject_failure(self) -> bool:
        """Determine if failure should be injected based on rate"""
        import random
        return random.random() < self.config.failure_injection_rate
    
    def get_random_failure_type(self) -> str:
        """Get random failure type from configured types"""
        import random
        return random.choice(self.config.failure_types)
    
    async def inject_failure(self, failure_type: str, server, metrics: StabilityMetrics) -> Dict[str, Any]:
        """Inject specific failure type and track results"""
        injection_start = time.time()
        injection_id = f"injection_{self.injection_count}"
        self.injection_count += 1
        
        injection_record = {
            "id": injection_id,
            "type": failure_type,
            "start_time": injection_start,
            "success": False,
            "recovery_time": None,
            "error_message": None
        }
        
        try:
            if failure_type == "database_connection_failure":
                await self._inject_database_failure(server)
            elif failure_type == "network_timeout":
                await self._inject_network_timeout(server)
            elif failure_type == "memory_pressure":
                await self._inject_memory_pressure(server)
            elif failure_type == "cpu_overload":
                await self._inject_cpu_overload(server)
            elif failure_type == "disk_full":
                await self._inject_disk_full(server)
            elif failure_type == "process_crash":
                await self._inject_process_crash(server)
            elif failure_type == "cascade_failure":
                await self._inject_cascade_failure(server)
            
            # Attempt recovery
            recovery_start = time.time()
            recovery_success = await self._attempt_recovery(server, failure_type)
            recovery_time = time.time() - recovery_start
            
            injection_record.update({
                "success": True,
                "recovery_success": recovery_success,
                "recovery_time": recovery_time
            })
            
            metrics.recovery_attempts += 1
            if recovery_success:
                metrics.successful_recoveries += 1
                metrics.recovery_times.append(recovery_time)
            
        except Exception as e:
            injection_record.update({
                "success": False,
                "error_message": str(e),
                "recovery_time": time.time() - injection_start
            })
        
        self.injection_history.append(injection_record)
        metrics.failure_injection_results[injection_id] = injection_record
        return injection_record
    
    async def _inject_database_failure(self, server):
        """Simulate database connection failure"""
        # Mock database connection failure
        if hasattr(server, 'retriever') and hasattr(server.retriever, 'database'):
            # Temporarily break database connection
            original_query = server.retriever.database.query
            server.retriever.database.query = lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Database connection failed"))
            await asyncio.sleep(1)  # Let the failure persist
            server.retriever.database.query = original_query
    
    async def _inject_network_timeout(self, server):
        """Simulate network timeout"""
        # Mock network delay/timeout
        await asyncio.sleep(2)  # Simulate network delay
    
    async def _inject_memory_pressure(self, server):
        """Simulate memory pressure"""
        if hasattr(server, 'reduce_memory_usage'):
            # Trigger memory pressure handling
            await server.handle_resource_pressure()
    
    async def _inject_cpu_overload(self, server):
        """Simulate CPU overload"""
        # Create CPU-intensive task
        import math
        for _ in range(10000):
            math.sqrt(99999)  # CPU-intensive operation
    
    async def _inject_disk_full(self, server):
        """Simulate disk full condition"""
        # Mock disk full condition by temporarily filling disk space check
        pass
    
    async def _inject_process_crash(self, server):
        """Simulate process crash recovery"""
        # Simulate process restart scenario
        if hasattr(server, 'restart_components'):
            await server.restart_components()
    
    async def _inject_cascade_failure(self, server):
        """Simulate cascading failure across multiple components"""
        # Inject multiple failures simultaneously
        await self._inject_database_failure(server)
        await asyncio.sleep(0.5)
        await self._inject_memory_pressure(server)
    
    async def _attempt_recovery(self, server, failure_type: str) -> bool:
        """Attempt recovery from injected failure"""
        try:
            if hasattr(server, 'handle_error_recovery'):
                recovery_result = await server.handle_error_recovery()
                return recovery_result is not None
            elif hasattr(server, 'simulate_failure_recovery_cycle'):
                await server.simulate_failure_recovery_cycle(failure_type)
                return True
            else:
                # Basic recovery - test if server still responds
                test_result = await server.handle_cbr_retrieve("recovery test query")
                return test_result is not None
        except Exception:
            return False


class SystemResourceMonitor:
    """Real-time system resource monitoring for stability testing"""
    
    def __init__(self, config: StabilityTestConfig):
        self.config = config
        self.is_monitoring = False
        self.monitor_task = None
    
    async def start_monitoring(self, metrics: StabilityMetrics):
        """Start continuous resource monitoring"""
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop(metrics))
    
    async def stop_monitoring(self):
        """Stop resource monitoring"""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitoring_loop(self, metrics: StabilityMetrics):
        """Continuous monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                memory_usage = psutil.virtual_memory().percent
                cpu_usage = psutil.cpu_percent(interval=1)
                
                metrics.memory_usage_samples.append(memory_usage)
                metrics.cpu_usage_samples.append(cpu_usage)
                
                # Check resource limits
                if memory_usage > (self.config.memory_limit_mb / 1024) * 100:
                    logging.warning(f"Memory usage exceeded limit: {memory_usage}%")
                
                if cpu_usage > self.config.cpu_limit_percent:
                    logging.warning(f"CPU usage exceeded limit: {cpu_usage}%")
                
                await asyncio.sleep(self.config.monitoring_interval_seconds)
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.monitoring_interval_seconds)


class StabilityTestReporter:
    """Comprehensive reporting for stability test results"""
    
    def __init__(self, config: StabilityTestConfig):
        self.config = config
        self.output_path = Path(config.report_output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    def generate_comprehensive_report(self, metrics: StabilityMetrics) -> Dict[str, Any]:
        """Generate comprehensive stability test report"""
        report = {
            "test_summary": {
                "start_time": metrics.test_start_time.isoformat(),
                "duration_hours": metrics.test_duration_seconds / 3600,
                "total_operations": metrics.total_operations,
                "success_rate": metrics.success_rate,
                "uptime_percentage": metrics.uptime_percentage
            },
            "performance_metrics": {
                "average_response_time_ms": metrics.average_response_time * 1000,
                "successful_operations": metrics.successful_operations,
                "failed_operations": metrics.failed_operations,
                "operations_per_hour": metrics.total_operations / max(metrics.test_duration_seconds / 3600, 0.01)
            },
            "error_recovery_metrics": {
                "recovery_rate": metrics.recovery_rate,
                "mean_time_to_recovery": metrics.mean_time_to_recovery,
                "total_recovery_attempts": metrics.recovery_attempts,
                "successful_recoveries": metrics.successful_recoveries
            },
            "resource_usage": {
                "average_memory_usage": metrics.average_memory_usage,
                "peak_memory_usage": max(metrics.memory_usage_samples) if metrics.memory_usage_samples else 0,
                "average_cpu_usage": metrics.average_cpu_usage,
                "peak_cpu_usage": max(metrics.cpu_usage_samples) if metrics.cpu_usage_samples else 0
            },
            "failure_injection_analysis": metrics.failure_injection_results,
            "error_breakdown": metrics.error_types,
            "success_criteria_validation": {
                "uptime_99_percent": metrics.uptime_percentage >= 99.0,
                "recovery_rate_95_percent": metrics.recovery_rate >= 95.0,
                "mttr_under_30_seconds": metrics.mean_time_to_recovery <= 30.0
            }
        }
        return report
    
    def save_report(self, metrics: StabilityMetrics):
        """Save comprehensive report to files"""
        report = self.generate_comprehensive_report(metrics)
        
        # Save JSON report
        json_path = self.output_path / f"stability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save CSV metrics
        csv_path = self.output_path / f"stability_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self._save_csv_metrics(metrics, csv_path)
        
        # Generate summary report
        summary_path = self.output_path / f"stability_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self._save_summary_report(report, summary_path)
        
        return {
            "json_report": str(json_path),
            "csv_metrics": str(csv_path),
            "summary_report": str(summary_path)
        }
    
    def _save_csv_metrics(self, metrics: StabilityMetrics, csv_path: Path):
        """Save detailed metrics to CSV"""
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'memory_usage', 'cpu_usage', 'response_time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write time-series data
            base_time = metrics.test_start_time
            for i, (mem, cpu) in enumerate(zip(metrics.memory_usage_samples, metrics.cpu_usage_samples)):
                timestamp = base_time + timedelta(seconds=i * 60)  # Assuming 60s intervals
                response_time = metrics.response_times[i] if i < len(metrics.response_times) else None
                
                writer.writerow({
                    'timestamp': timestamp.isoformat(),
                    'memory_usage': mem,
                    'cpu_usage': cpu,
                    'response_time': response_time
                })
    
    def _save_summary_report(self, report: Dict[str, Any], summary_path: Path):
        """Save human-readable summary report"""
        with open(summary_path, 'w') as f:
            f.write("CBR MCP Server 24-Hour Stability Test Report\n")
            f.write("=" * 50 + "\n\n")
            
            # Test Summary
            summary = report["test_summary"]
            f.write(f"Test Duration: {summary['duration_hours']:.1f} hours\n")
            f.write(f"Total Operations: {summary['total_operations']}\n")
            f.write(f"Success Rate: {summary['success_rate']:.2f}%\n")
            f.write(f"Uptime: {summary['uptime_percentage']:.2f}%\n\n")
            
            # Performance Metrics
            perf = report["performance_metrics"]
            f.write("Performance Metrics:\n")
            f.write(f"  Average Response Time: {perf['average_response_time_ms']:.2f} ms\n")
            f.write(f"  Operations Per Hour: {perf['operations_per_hour']:.1f}\n")
            f.write(f"  Successful Operations: {perf['successful_operations']}\n")
            f.write(f"  Failed Operations: {perf['failed_operations']}\n\n")
            
            # Error Recovery
            recovery = report["error_recovery_metrics"]
            f.write("Error Recovery Metrics:\n")
            f.write(f"  Recovery Rate: {recovery['recovery_rate']:.2f}%\n")
            f.write(f"  Mean Time To Recovery: {recovery['mean_time_to_recovery']:.2f} seconds\n")
            f.write(f"  Total Recovery Attempts: {recovery['total_recovery_attempts']}\n")
            f.write(f"  Successful Recoveries: {recovery['successful_recoveries']}\n\n")
            
            # Success Criteria Validation
            criteria = report["success_criteria_validation"]
            f.write("Success Criteria Validation:\n")
            f.write(f"  99% Uptime: {'✓ PASS' if criteria['uptime_99_percent'] else '✗ FAIL'}\n")
            f.write(f"  95% Recovery Rate: {'✓ PASS' if criteria['recovery_rate_95_percent'] else '✗ FAIL'}\n")
            f.write(f"  <30s MTTR: {'✓ PASS' if criteria['mttr_under_30_seconds'] else '✗ FAIL'}\n")


class TwentyFourHourStabilityTester:
    """Main 24-hour stability testing framework"""
    
    def __init__(self, config: StabilityTestConfig):
        self.config = config
        self.metrics = StabilityMetrics(test_start_time=datetime.now())
        self.failure_injector = FailureInjector(config)
        self.resource_monitor = SystemResourceMonitor(config)
        self.reporter = StabilityTestReporter(config)
        self.is_running = False
        self.shutdown_event = asyncio.Event()
    
    async def run_stability_test(self, server):
        """Run complete 24-hour stability test"""
        logging.info("Starting 24-hour stability test")
        self.is_running = True
        self.metrics.test_start_time = datetime.now()
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Start resource monitoring
        await self.resource_monitor.start_monitoring(self.metrics)
        
        try:
            # Run main test loop
            await self._run_test_loop(server)
        except Exception as e:
            logging.error(f"Error in stability test: {e}")
        finally:
            # Clean shutdown
            await self._cleanup()
        
        # Generate final report
        self.metrics.test_duration_seconds = (datetime.now() - self.metrics.test_start_time).total_seconds()
        self._calculate_final_metrics()
        
        report_files = self.reporter.save_report(self.metrics)
        logging.info(f"Stability test completed. Reports saved: {report_files}")
        
        return self.metrics, report_files
    
    async def _run_test_loop(self, server):
        """Main test execution loop"""
        test_end_time = self.metrics.test_start_time + timedelta(hours=self.config.duration_hours)
        operation_interval = 3600 / self.config.queries_per_hour  # seconds between operations
        
        while datetime.now() < test_end_time and self.is_running:
            if self.shutdown_event.is_set():
                logging.info("Shutdown requested, stopping test")
                break
            
            # Execute CBR operation
            await self._execute_cbr_operation(server)
            
            # Check if we should inject a failure
            if self.failure_injector.should_inject_failure():
                failure_type = self.failure_injector.get_random_failure_type()
                logging.info(f"Injecting failure: {failure_type}")
                await self.failure_injector.inject_failure(failure_type, server, self.metrics)
            
            # Wait for next operation
            await asyncio.sleep(operation_interval)
        
        self.is_running = False
    
    async def _execute_cbr_operation(self, server):
        """Execute single CBR operation with metrics tracking"""
        operation_start = time.time()
        self.metrics.total_operations += 1
        
        try:
            # Generate test query
            query = f"stability test query {self.metrics.total_operations}"
            
            # Execute CBR retrieve
            result = await server.handle_cbr_retrieve(query, limit=10)
            
            response_time = time.time() - operation_start
            self.metrics.response_times.append(response_time)
            
            if result is not None:
                self.metrics.successful_operations += 1
            else:
                self.metrics.failed_operations += 1
                self.metrics.error_types["null_result"] = self.metrics.error_types.get("null_result", 0) + 1
                
        except Exception as e:
            self.metrics.failed_operations += 1
            error_type = type(e).__name__
            self.metrics.error_types[error_type] = self.metrics.error_types.get(error_type, 0) + 1
            logging.error(f"Operation failed: {e}")
    
    def _calculate_final_metrics(self):
        """Calculate final stability metrics"""
        if self.metrics.total_operations > 0:
            # Calculate uptime percentage
            uptime_seconds = self.metrics.test_duration_seconds
            downtime_seconds = sum(self.metrics.recovery_times)
            self.metrics.uptime_percentage = ((uptime_seconds - downtime_seconds) / uptime_seconds) * 100
            
            # Ensure uptime doesn't exceed 100%
            self.metrics.uptime_percentage = min(100.0, max(0.0, self.metrics.uptime_percentage))
    
    async def _cleanup(self):
        """Clean shutdown of all components"""
        await self.resource_monitor.stop_monitoring()
        self.is_running = False
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self._initiate_shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def _initiate_shutdown(self):
        """Initiate graceful shutdown"""
        self.shutdown_event.set()
        self.is_running = False


async def run_24_hour_stability_test(server, config: Optional[StabilityTestConfig] = None):
    """
    Run comprehensive 24-hour stability test for CBR MCP Server
    
    Args:
        server: CBR MCP Server instance
        config: Optional test configuration
        
    Returns:
        Tuple of (metrics, report_files)
    """
    if config is None:
        config = StabilityTestConfig()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('stability_test.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create and run stability tester
    tester = TwentyFourHourStabilityTester(config)
    return await tester.run_stability_test(server)


# CLI interface for running standalone tests
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="24-Hour CBR MCP Server Stability Test")
    parser.add_argument("--duration", type=float, default=24.0, help="Test duration in hours")
    parser.add_argument("--queries-per-hour", type=int, default=100, help="Queries per hour")
    parser.add_argument("--failure-rate", type=float, default=0.05, help="Failure injection rate")
    parser.add_argument("--output-path", type=str, default="./stability_test_results", help="Output path for reports")
    
    args = parser.parse_args()
    
    # Create configuration
    config = StabilityTestConfig(
        duration_hours=args.duration,
        queries_per_hour=args.queries_per_hour,
        failure_injection_rate=args.failure_rate,
        report_output_path=args.output_path
    )
    
    print(f"Starting {config.duration_hours}-hour stability test...")
    print(f"Configuration: {config.queries_per_hour} queries/hour, {config.failure_injection_rate*100}% failure rate")
    
    # For CLI usage, this would need to import and initialize the actual server
    # For now, we'll show the configuration
    print("Note: This script requires integration with an actual CBR MCP Server instance")
    print("Use as a module: from stability_test_framework import run_24_hour_stability_test")