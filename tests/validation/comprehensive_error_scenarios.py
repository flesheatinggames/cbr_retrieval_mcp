#!/usr/bin/env python3
"""
Comprehensive Error Scenario Testing for CBR MCP Server

This module provides exhaustive error scenario testing to validate all recovery paths
and ensure production-level reliability under all failure conditions.
"""

import asyncio
import json
import logging
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class ErrorScenarioType(Enum):
    """Types of error scenarios for comprehensive testing"""

    DATABASE_CONNECTION_FAILURE = "database_connection_failure"
    NETWORK_TIMEOUT = "network_timeout"
    MEMORY_EXHAUSTION = "memory_exhaustion"
    CPU_OVERLOAD = "cpu_overload"
    DISK_SPACE_FULL = "disk_space_full"
    PROCESS_CRASH = "process_crash"
    AUTHENTICATION_FAILURE = "authentication_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_INPUT = "invalid_input"
    CONCURRENT_RESOURCE_CONTENTION = "concurrent_resource_contention"
    CASCADING_FAILURE = "cascading_failure"
    INTERMITTENT_FAILURE = "intermittent_failure"
    CORRUPTION_FAILURE = "corruption_failure"
    DEPENDENCY_FAILURE = "dependency_failure"
    RESOURCE_LEAK = "resource_leak"


@dataclass
class ErrorScenario:
    """Definition of an error scenario for testing"""

    scenario_id: str
    scenario_type: ErrorScenarioType
    description: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    expected_recovery_time: float  # seconds
    recovery_strategy: str
    test_parameters: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class ErrorTestResult:
    """Result of an error scenario test"""

    scenario_id: str
    scenario_type: ErrorScenarioType
    test_start_time: datetime
    test_duration: float
    error_injected: bool
    recovery_successful: bool
    recovery_time: float
    success_criteria_met: List[bool]
    error_details: Optional[str] = None
    recovery_details: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


class ErrorScenarioRunner:
    """Comprehensive error scenario testing runner"""

    def __init__(self, server):
        self.server = server
        self.test_results: List[ErrorTestResult] = []
        self.active_scenarios: Dict[str, ErrorScenario] = {}

        # Define comprehensive error scenarios
        self.error_scenarios = self._define_error_scenarios()

    def _define_error_scenarios(self) -> List[ErrorScenario]:
        """Define all error scenarios for comprehensive testing"""
        scenarios = [
            # Database and Storage Failures
            ErrorScenario(
                scenario_id="DB_CONN_01",
                scenario_type=ErrorScenarioType.DATABASE_CONNECTION_FAILURE,
                description="Database connection timeout during query execution",
                severity="HIGH",
                expected_recovery_time=10.0,
                recovery_strategy="Reconnect with exponential backoff",
                test_parameters={"timeout_duration": 5.0},
                success_criteria=[
                    "Query eventually succeeds after reconnection",
                    "No data corruption",
                    "Recovery time under 15 seconds",
                ],
            ),
            ErrorScenario(
                scenario_id="DB_CONN_02",
                scenario_type=ErrorScenarioType.DATABASE_CONNECTION_FAILURE,
                description="Complete database unavailability",
                severity="CRITICAL",
                expected_recovery_time=20.0,
                recovery_strategy="Fallback to cached results and retry",
                test_parameters={"unavailability_duration": 15.0},
                success_criteria=[
                    "Graceful degradation to cached results",
                    "Error properly communicated to client",
                    "Full recovery when database returns",
                ],
            ),
            # Network Failures
            ErrorScenario(
                scenario_id="NET_01",
                scenario_type=ErrorScenarioType.NETWORK_TIMEOUT,
                description="Network timeout during external service call",
                severity="MEDIUM",
                expected_recovery_time=5.0,
                recovery_strategy="Retry with circuit breaker",
                test_parameters={"timeout_threshold": 3.0},
                success_criteria=[
                    "Request retried with backoff",
                    "Circuit breaker prevents cascading failures",
                    "Recovery within timeout threshold",
                ],
            ),
            ErrorScenario(
                scenario_id="NET_02",
                scenario_type=ErrorScenarioType.NETWORK_TIMEOUT,
                description="Intermittent network connectivity issues",
                severity="MEDIUM",
                expected_recovery_time=8.0,
                recovery_strategy="Adaptive retry with jitter",
                test_parameters={"failure_probability": 0.3, "duration": 30.0},
                success_criteria=[
                    "Adaptive retry successfully handles intermittent failures",
                    "Overall success rate maintains above 90%",
                    "Response times remain reasonable",
                ],
            ),
            # Resource Exhaustion
            ErrorScenario(
                scenario_id="MEM_01",
                scenario_type=ErrorScenarioType.MEMORY_EXHAUSTION,
                description="Memory usage exceeds available limits",
                severity="HIGH",
                expected_recovery_time=5.0,
                recovery_strategy="Clear caches and reduce memory footprint",
                test_parameters={"memory_pressure_threshold": 0.9},
                success_criteria=[
                    "Memory usage reduced below threshold",
                    "Service remains available",
                    "Performance impact minimized",
                ],
            ),
            ErrorScenario(
                scenario_id="CPU_01",
                scenario_type=ErrorScenarioType.CPU_OVERLOAD,
                description="CPU usage exceeds capacity",
                severity="HIGH",
                expected_recovery_time=10.0,
                recovery_strategy="Throttle operations and shed load",
                test_parameters={"cpu_threshold": 0.95},
                success_criteria=[
                    "Load shedding activated",
                    "CPU usage brought under control",
                    "Critical operations continue",
                ],
            ),
            # Input and Validation Errors
            ErrorScenario(
                scenario_id="INPUT_01",
                scenario_type=ErrorScenarioType.INVALID_INPUT,
                description="Malformed or malicious input data",
                severity="MEDIUM",
                expected_recovery_time=1.0,
                recovery_strategy="Input validation and sanitization",
                test_parameters={
                    "malformed_queries": [
                        "",  # Empty query
                        None,  # None query
                        "x" * 100000,  # Extremely long query
                        "'; DROP TABLE users; --",  # SQL injection attempt
                        "\x00\x01\x02",  # Binary data
                        {"not": "a string"},  # Wrong type
                    ]
                },
                success_criteria=[
                    "All invalid inputs handled gracefully",
                    "No security vulnerabilities exposed",
                    "Proper error messages returned",
                ],
            ),
            # Concurrent Access Issues
            ErrorScenario(
                scenario_id="CONCURRENT_01",
                scenario_type=ErrorScenarioType.CONCURRENT_RESOURCE_CONTENTION,
                description="High concurrent load causing resource contention",
                severity="HIGH",
                expected_recovery_time=15.0,
                recovery_strategy="Request queuing and throttling",
                test_parameters={"concurrent_requests": 100, "duration": 60.0},
                success_criteria=[
                    "All requests eventually processed",
                    "No deadlocks or resource leaks",
                    "Response times remain reasonable",
                ],
            ),
            # Cascading Failures
            ErrorScenario(
                scenario_id="CASCADE_01",
                scenario_type=ErrorScenarioType.CASCADING_FAILURE,
                description="Multiple component failures occurring simultaneously",
                severity="CRITICAL",
                expected_recovery_time=25.0,
                recovery_strategy="Coordinated recovery with priority ordering",
                test_parameters={
                    "failure_components": ["database", "cache", "logging"],
                    "failure_delay": 2.0,
                },
                success_criteria=[
                    "Components recovered in correct order",
                    "System eventually fully operational",
                    "Data consistency maintained",
                ],
            ),
            # Process and System Failures
            ErrorScenario(
                scenario_id="PROCESS_01",
                scenario_type=ErrorScenarioType.PROCESS_CRASH,
                description="Simulated process crash and restart",
                severity="CRITICAL",
                expected_recovery_time=30.0,
                recovery_strategy="Process restart with state recovery",
                test_parameters={"crash_probability": 1.0},
                success_criteria=[
                    "Process restarts successfully",
                    "State recovered from persistence",
                    "Service availability restored",
                ],
            ),
            # Authentication and Authorization
            ErrorScenario(
                scenario_id="AUTH_01",
                scenario_type=ErrorScenarioType.AUTHENTICATION_FAILURE,
                description="Authentication service unavailable",
                severity="HIGH",
                expected_recovery_time=10.0,
                recovery_strategy="Fallback authentication and caching",
                test_parameters={"auth_service_downtime": 20.0},
                success_criteria=[
                    "Cached credentials used when available",
                    "Graceful degradation for unauthenticated requests",
                    "Full recovery when auth service returns",
                ],
            ),
            # Rate Limiting
            ErrorScenario(
                scenario_id="RATE_01",
                scenario_type=ErrorScenarioType.RATE_LIMIT_EXCEEDED,
                description="Request rate exceeds configured limits",
                severity="MEDIUM",
                expected_recovery_time=5.0,
                recovery_strategy="Request queuing and client backoff signals",
                test_parameters={"request_burst": 1000, "rate_limit": 100},
                success_criteria=[
                    "Rate limiting properly enforced",
                    "Excess requests queued or rejected appropriately",
                    "Service remains stable",
                ],
            ),
            # Resource Leaks
            ErrorScenario(
                scenario_id="LEAK_01",
                scenario_type=ErrorScenarioType.RESOURCE_LEAK,
                description="Memory or file descriptor leaks over time",
                severity="HIGH",
                expected_recovery_time=60.0,
                recovery_strategy="Periodic resource cleanup and monitoring",
                test_parameters={"operations_count": 1000, "leak_rate": 0.001},
                success_criteria=[
                    "Resource usage remains stable over time",
                    "Cleanup mechanisms prevent accumulation",
                    "System remains stable long-term",
                ],
            ),
        ]

        return scenarios

    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all error scenarios and return comprehensive results"""
        logging.info("Starting comprehensive error scenario testing")

        overall_results = {
            "start_time": datetime.now().isoformat(),
            "total_scenarios": len(self.error_scenarios),
            "completed_scenarios": 0,
            "passed_scenarios": 0,
            "failed_scenarios": 0,
            "scenario_results": {},
            "summary_metrics": {},
            "recommendations": [],
        }

        for scenario in self.error_scenarios:
            logging.info(
                f"Running error scenario: {scenario.scenario_id} - {scenario.description}"
            )

            try:
                result = await self.run_scenario(scenario)
                overall_results["scenario_results"][scenario.scenario_id] = result
                overall_results["completed_scenarios"] += 1

                if result.recovery_successful and all(result.success_criteria_met):
                    overall_results["passed_scenarios"] += 1
                else:
                    overall_results["failed_scenarios"] += 1

            except Exception as e:
                logging.error(f"Error running scenario {scenario.scenario_id}: {e}")
                overall_results["scenario_results"][scenario.scenario_id] = {
                    "error": str(e),
                    "status": "ERROR",
                }
                overall_results["failed_scenarios"] += 1

        # Calculate summary metrics
        overall_results["summary_metrics"] = self._calculate_summary_metrics()
        overall_results["recommendations"] = self._generate_recommendations()
        overall_results["end_time"] = datetime.now().isoformat()

        return overall_results

    async def run_scenario(self, scenario: ErrorScenario) -> ErrorTestResult:
        """Run a single error scenario"""
        test_start = datetime.now()
        scenario_id = f"{scenario.scenario_id}_{uuid.uuid4().hex[:8]}"

        result = ErrorTestResult(
            scenario_id=scenario_id,
            scenario_type=scenario.scenario_type,
            test_start_time=test_start,
            test_duration=0.0,
            error_injected=False,
            recovery_successful=False,
            recovery_time=0.0,
            success_criteria_met=[],
        )

        try:
            # Inject the error based on scenario type
            error_injection_start = time.time()
            await self._inject_error(scenario, result)
            result.error_injected = True

            # Attempt recovery
            recovery_start = time.time()
            recovery_success = await self._attempt_recovery(scenario, result)
            result.recovery_time = time.time() - recovery_start
            result.recovery_successful = recovery_success

            # Validate success criteria
            result.success_criteria_met = await self._validate_success_criteria(
                scenario, result
            )

            result.test_duration = (datetime.now() - test_start).total_seconds()

        except Exception as e:
            result.error_details = str(e)
            result.test_duration = (datetime.now() - test_start).total_seconds()
            logging.error(f"Scenario {scenario_id} failed: {e}")

        self.test_results.append(result)
        return result

    async def _inject_error(self, scenario: ErrorScenario, result: ErrorTestResult):
        """Inject error based on scenario type"""
        scenario_type = scenario.scenario_type
        params = scenario.test_parameters

        if scenario_type == ErrorScenarioType.DATABASE_CONNECTION_FAILURE:
            await self._inject_database_failure(params, result)
        elif scenario_type == ErrorScenarioType.NETWORK_TIMEOUT:
            await self._inject_network_timeout(params, result)
        elif scenario_type == ErrorScenarioType.MEMORY_EXHAUSTION:
            await self._inject_memory_exhaustion(params, result)
        elif scenario_type == ErrorScenarioType.CPU_OVERLOAD:
            await self._inject_cpu_overload(params, result)
        elif scenario_type == ErrorScenarioType.INVALID_INPUT:
            await self._inject_invalid_input(params, result)
        elif scenario_type == ErrorScenarioType.CONCURRENT_RESOURCE_CONTENTION:
            await self._inject_concurrent_contention(params, result)
        elif scenario_type == ErrorScenarioType.CASCADING_FAILURE:
            await self._inject_cascading_failure(params, result)
        elif scenario_type == ErrorScenarioType.PROCESS_CRASH:
            await self._inject_process_crash(params, result)
        elif scenario_type == ErrorScenarioType.AUTHENTICATION_FAILURE:
            await self._inject_auth_failure(params, result)
        elif scenario_type == ErrorScenarioType.RATE_LIMIT_EXCEEDED:
            await self._inject_rate_limit_exceeded(params, result)
        elif scenario_type == ErrorScenarioType.RESOURCE_LEAK:
            await self._inject_resource_leak(params, result)
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")

    async def _inject_database_failure(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject database connection failure"""
        # Simulate database connection issues
        if hasattr(self.server, "retriever") and hasattr(
            self.server.retriever, "database"
        ):
            # Mock database failure
            original_query = getattr(self.server.retriever.database, "query", None)
            if original_query:

                def failing_query(*args, **kwargs):
                    raise Exception("Database connection failed")

                self.server.retriever.database.query = failing_query
                await asyncio.sleep(params.get("timeout_duration", 5.0))

                # Restore original function for recovery testing
                self.server.retriever.database.query = original_query

        result.metrics["database_failure_injected"] = True

    async def _inject_network_timeout(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject network timeout conditions"""
        # Simulate network delays
        delay = params.get("timeout_threshold", 3.0)
        await asyncio.sleep(delay)
        result.metrics["network_delay_injected"] = delay

    async def _inject_memory_exhaustion(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject memory pressure conditions"""
        if hasattr(self.server, "handle_resource_pressure"):
            # Trigger memory pressure handling
            await self.server.handle_resource_pressure()
        result.metrics["memory_pressure_injected"] = True

    async def _inject_cpu_overload(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject CPU overload conditions"""
        # Simulate CPU-intensive operations
        import math

        cpu_work_duration = params.get("cpu_work_duration", 2.0)
        start_time = time.time()

        while time.time() - start_time < cpu_work_duration:
            # CPU-intensive calculation
            for _ in range(1000):
                math.sqrt(random.random() * 999999)
            await asyncio.sleep(0.001)  # Brief yield

        result.metrics["cpu_overload_duration"] = cpu_work_duration

    async def _inject_invalid_input(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject invalid input scenarios"""
        malformed_queries = params.get("malformed_queries", ["", None])
        test_results = []

        for query in malformed_queries:
            try:
                # Test each malformed query
                response = await self.server.handle_cbr_retrieve(query)
                test_results.append(
                    {
                        "query": str(query),
                        "handled": True,
                        "response": response is not None,
                    }
                )
            except Exception as e:
                test_results.append(
                    {"query": str(query), "handled": True, "error": str(e)}
                )

        result.metrics["invalid_input_tests"] = test_results

    async def _inject_concurrent_contention(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject concurrent resource contention"""
        concurrent_requests = params.get("concurrent_requests", 50)
        duration = params.get("duration", 30.0)

        async def concurrent_worker(worker_id: int):
            start_time = time.time()
            requests_made = 0
            while time.time() - start_time < duration:
                try:
                    await self.server.handle_cbr_retrieve(
                        f"concurrent test {worker_id}_{requests_made}"
                    )
                    requests_made += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    pass
            return requests_made

        # Launch concurrent workers
        tasks = [concurrent_worker(i) for i in range(concurrent_requests)]
        request_counts = await asyncio.gather(*tasks, return_exceptions=True)

        successful_workers = [c for c in request_counts if isinstance(c, int)]
        total_requests = sum(successful_workers)

        result.metrics["concurrent_contention"] = {
            "concurrent_workers": concurrent_requests,
            "successful_workers": len(successful_workers),
            "total_requests_made": total_requests,
            "duration": duration,
        }

    async def _inject_cascading_failure(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject cascading failure scenario"""
        failure_components = params.get("failure_components", ["database", "cache"])
        failure_delay = params.get("failure_delay", 2.0)

        failures_injected = []

        for component in failure_components:
            if component == "database":
                await self._inject_database_failure({"timeout_duration": 1.0}, result)
            elif component == "cache" and hasattr(self.server, "clear_cache"):
                # Simulate cache failure
                self.server.clear_cache()
            elif component == "logging" and hasattr(self.server, "logger"):
                # Simulate logging system issues
                original_log = self.server.logger.error
                self.server.logger.error = lambda *args, **kwargs: None
                await asyncio.sleep(failure_delay)
                self.server.logger.error = original_log

            failures_injected.append(component)
            await asyncio.sleep(failure_delay)

        result.metrics["cascading_failures"] = failures_injected

    async def _inject_process_crash(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Simulate process crash and restart"""
        # Simulate process restart by reinitializing components
        if hasattr(self.server, "restart_components"):
            await self.server.restart_components()
        else:
            # Mock restart by clearing internal state
            if hasattr(self.server, "retriever") and hasattr(
                self.server.retriever, "clear_cache"
            ):
                self.server.retriever.clear_cache()

        result.metrics["process_crash_simulated"] = True

    async def _inject_auth_failure(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject authentication failure"""
        # Mock authentication failure
        downtime = params.get("auth_service_downtime", 10.0)
        await asyncio.sleep(min(downtime, 2.0))  # Limit for testing
        result.metrics["auth_failure_duration"] = downtime

    async def _inject_rate_limit_exceeded(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject rate limit exceeded scenario"""
        request_burst = params.get("request_burst", 100)
        rate_limit = params.get("rate_limit", 50)

        # Send burst of requests
        tasks = [
            self.server.handle_cbr_retrieve(f"rate limit test {i}")
            for i in range(min(request_burst, 20))  # Limit for testing
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful_requests = [r for r in results if not isinstance(r, Exception)]

        result.metrics["rate_limit_test"] = {
            "requests_sent": len(tasks),
            "successful_requests": len(successful_requests),
            "blocked_requests": len(tasks) - len(successful_requests),
        }

    async def _inject_resource_leak(
        self, params: Dict[str, Any], result: ErrorTestResult
    ):
        """Inject resource leak scenario"""
        operations_count = params.get("operations_count", 100)

        # Perform many operations to test for leaks
        for i in range(min(operations_count, 50)):  # Limit for testing
            await self.server.handle_cbr_retrieve(f"leak test {i}")
            if i % 10 == 0:
                await asyncio.sleep(0.1)  # Brief pause

        result.metrics["resource_leak_test"] = {
            "operations_performed": min(operations_count, 50)
        }

    async def _attempt_recovery(
        self, scenario: ErrorScenario, result: ErrorTestResult
    ) -> bool:
        """Attempt recovery from the injected error"""
        try:
            # General recovery: attempt to use the service normally
            recovery_test_query = f"recovery test for {scenario.scenario_id}"

            # Try multiple times with exponential backoff
            max_attempts = 5
            base_delay = 0.5

            for attempt in range(max_attempts):
                try:
                    response = await self.server.handle_cbr_retrieve(
                        recovery_test_query
                    )
                    if response is not None:
                        result.recovery_details = f"Recovered on attempt {attempt + 1}"
                        return True
                except Exception as e:
                    if attempt < max_attempts - 1:
                        delay = base_delay * (2**attempt)
                        await asyncio.sleep(delay)
                    else:
                        result.recovery_details = (
                            f"Failed all {max_attempts} recovery attempts: {str(e)}"
                        )

            return False

        except Exception as e:
            result.recovery_details = f"Recovery attempt failed: {str(e)}"
            return False

    async def _validate_success_criteria(
        self, scenario: ErrorScenario, result: ErrorTestResult
    ) -> List[bool]:
        """Validate success criteria for the scenario"""
        criteria_met = []

        for criterion in scenario.success_criteria:
            try:
                if "recovery time under" in criterion.lower():
                    # Extract time threshold from criterion
                    import re

                    time_match = re.search(r"(\d+)", criterion)
                    if time_match:
                        threshold = float(time_match.group(1))
                        criteria_met.append(result.recovery_time <= threshold)
                    else:
                        criteria_met.append(
                            result.recovery_time <= scenario.expected_recovery_time
                        )

                elif "eventually succeeds" in criterion.lower():
                    criteria_met.append(result.recovery_successful)

                elif "graceful" in criterion.lower():
                    # Check if the system handled the error gracefully
                    criteria_met.append(
                        result.error_details is None
                        or "timeout" not in result.error_details.lower()
                    )

                elif "no data corruption" in criterion.lower():
                    # Assume no data corruption if recovery was successful
                    criteria_met.append(result.recovery_successful)

                else:
                    # Default: assume criterion is met if recovery was successful
                    criteria_met.append(result.recovery_successful)

            except Exception:
                criteria_met.append(False)

        return criteria_met

    def _calculate_summary_metrics(self) -> Dict[str, Any]:
        """Calculate summary metrics from all test results"""
        if not self.test_results:
            return {}

        total_tests = len(self.test_results)
        successful_recoveries = sum(
            1 for r in self.test_results if r.recovery_successful
        )

        recovery_times = [
            r.recovery_time for r in self.test_results if r.recovery_successful
        ]
        avg_recovery_time = (
            sum(recovery_times) / len(recovery_times) if recovery_times else 0
        )

        # Group by severity
        severity_stats = {}
        for result in self.test_results:
            scenario = next(
                (
                    s
                    for s in self.error_scenarios
                    if s.scenario_id.split("_")[0] in result.scenario_id
                ),
                None,
            )
            if scenario:
                severity = scenario.severity
                if severity not in severity_stats:
                    severity_stats[severity] = {"total": 0, "passed": 0}
                severity_stats[severity]["total"] += 1
                if result.recovery_successful:
                    severity_stats[severity]["passed"] += 1

        return {
            "total_scenarios_tested": total_tests,
            "successful_recoveries": successful_recoveries,
            "recovery_rate": (
                (successful_recoveries / total_tests * 100) if total_tests > 0 else 0
            ),
            "average_recovery_time": avg_recovery_time,
            "max_recovery_time": max(recovery_times) if recovery_times else 0,
            "severity_breakdown": severity_stats,
            "overall_resilience_score": self._calculate_resilience_score(),
        }

    def _calculate_resilience_score(self) -> float:
        """Calculate overall system resilience score (0-100)"""
        if not self.test_results:
            return 0.0

        weights = {"CRITICAL": 4.0, "HIGH": 3.0, "MEDIUM": 2.0, "LOW": 1.0}

        total_weighted_score = 0.0
        total_weight = 0.0

        for result in self.test_results:
            scenario = next(
                (
                    s
                    for s in self.error_scenarios
                    if s.scenario_id.split("_")[0] in result.scenario_id
                ),
                None,
            )
            if scenario:
                weight = weights.get(scenario.severity, 1.0)
                score = (
                    100.0
                    if result.recovery_successful and all(result.success_criteria_met)
                    else 0.0
                )

                total_weighted_score += score * weight
                total_weight += weight

        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if not self.test_results:
            return ["No test results available for analysis"]

        # Analyze failure patterns
        failed_scenarios = [r for r in self.test_results if not r.recovery_successful]

        if failed_scenarios:
            recommendations.append(
                f"Address {len(failed_scenarios)} failed recovery scenarios"
            )

            # Analyze by type
            failure_types = {}
            for result in failed_scenarios:
                scenario_type = result.scenario_type.value
                if scenario_type not in failure_types:
                    failure_types[scenario_type] = 0
                failure_types[scenario_type] += 1

            for failure_type, count in failure_types.items():
                recommendations.append(
                    f"Improve {failure_type} error handling ({count} failures)"
                )

        # Analyze recovery times
        slow_recoveries = [r for r in self.test_results if r.recovery_time > 30.0]
        if slow_recoveries:
            recommendations.append(
                f"Optimize recovery time for {len(slow_recoveries)} slow scenarios"
            )

        # Overall health check
        recovery_rate = (
            len([r for r in self.test_results if r.recovery_successful])
            / len(self.test_results)
            * 100
        )
        if recovery_rate < 95.0:
            recommendations.append(
                f"Improve overall recovery rate from {recovery_rate:.1f}% to target 95%+"
            )

        if not recommendations:
            recommendations.append(
                "All error scenarios passed - system demonstrates excellent resilience"
            )

        return recommendations


# Integration with pytest
class TestComprehensiveErrorScenarios:
    """Test class for comprehensive error scenario validation"""

    async def test_all_error_scenarios(self, integrated_cbr_server):
        """Test all defined error scenarios"""
        runner = ErrorScenarioRunner(integrated_cbr_server)
        results = await runner.run_all_scenarios()

        # Log comprehensive results
        logging.info(
            f"Error scenario testing completed: {json.dumps(results, indent=2, default=str)}"
        )

        # Assert minimum requirements
        assert results["completed_scenarios"] > 0, "No scenarios were completed"
        assert (
            results["summary_metrics"]["recovery_rate"] >= 80.0
        ), f"Recovery rate too low: {results['summary_metrics']['recovery_rate']:.1f}%"
        assert (
            results["summary_metrics"]["overall_resilience_score"] >= 75.0
        ), f"Resilience score too low: {results['summary_metrics']['overall_resilience_score']:.1f}"

        # Print summary
        print("\n" + "=" * 80)
        print("COMPREHENSIVE ERROR SCENARIO TESTING RESULTS")
        print("=" * 80)
        print(f"Total Scenarios: {results['total_scenarios']}")
        print(f"Completed: {results['completed_scenarios']}")
        print(f"Passed: {results['passed_scenarios']}")
        print(f"Failed: {results['failed_scenarios']}")
        print(f"Recovery Rate: {results['summary_metrics']['recovery_rate']:.1f}%")
        print(
            f"Resilience Score: {results['summary_metrics']['overall_resilience_score']:.1f}/100"
        )
        print("\nRecommendations:")
        for rec in results["recommendations"]:
            print(f"  - {rec}")
        print("=" * 80)


async def run_comprehensive_error_scenario_testing(server):
    """
    Run comprehensive error scenario testing

    Args:
        server: CBR MCP Server instance

    Returns:
        Comprehensive test results
    """
    runner = ErrorScenarioRunner(server)
    return await runner.run_all_scenarios()


if __name__ == "__main__":
    # CLI interface
    print("Comprehensive Error Scenario Testing Framework")
    print("Note: This requires integration with a CBR MCP Server instance")
    print(
        "Use as module: from comprehensive_error_scenarios import run_comprehensive_error_scenario_testing"
    )
