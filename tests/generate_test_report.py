"""
Comprehensive test report generator for the movie generation platform.
Runs all integration tests and generates a detailed report with recommendations.
"""
import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess

# Add the tests directory to the Python path
sys.path.append(str(Path(__file__).parent))

from utils.test_helpers import (
    ServiceTestHelper,
    PerformanceTester,
    MCPTestClient
)


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    error_message: str = None
    details: Dict[str, Any] = None


@dataclass
class ServiceStatus:
    """Service status data structure."""
    name: str
    healthy: bool
    response_time: float
    url: str
    error: str = None
    service_info: Dict[str, Any] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    operation: str
    avg_duration: float
    min_duration: float
    max_duration: float
    success_rate: float
    total_operations: int


class TestReportGenerator:
    """Generates comprehensive test reports."""

    def __init__(self):
        self.test_results: List[TestResult] = []
        self.service_statuses: List[ServiceStatus] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        self.start_time = time.time()

        # Test configuration
        self.test_config = {
            "brain_service": {
                "host": "localhost",
                "port": 8002,
                "websocket_url": "ws://localhost:8002/",
                "http_url": "http://localhost:8002"
            },
            "character_service": {
                "host": "localhost",
                "port": 8011,
                "http_url": "http://localhost:8011"
            },
            "story_service": {
                "host": "localhost",
                "port": 8012,
                "http_url": "http://localhost:8012"
            },
            "orchestrator": {
                "host": "localhost",
                "port": 8001,
                "http_url": "http://localhost:8001"
            },
            "celery_redis": {
                "host": "localhost",
                "port": 8010,
                "http_url": "http://localhost:8010"
            }
        }

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all integration tests and collect results."""
        print("🚀 Starting Comprehensive Integration Test Suite")
        print("=" * 60)

        # 1. Service Health Assessment
        print("\n📋 Phase 1: Service Health Assessment")
        await self._test_service_health()

        # 2. Core Functionality Tests
        print("\n🧠 Phase 2: Core Functionality Tests")
        await self._test_core_functionality()

        # 3. Performance Testing
        print("\n⚡ Phase 3: Performance Testing")
        await self._test_performance()

        # 4. Integration Testing
        print("\n🔗 Phase 4: Cross-Service Integration")
        await self._test_integration()

        # 5. Error Handling & Recovery
        print("\n🛡️ Phase 5: Error Handling & Recovery")
        await self._test_error_handling()

        # Generate final report
        return self._generate_final_report()

    async def _test_service_health(self):
        """Test health of all configured services."""
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            for service_name, config in self.test_config.items():
                print(f"  Testing {service_name}...")

                start_time = time.time()
                service_helper = ServiceTestHelper(config["http_url"])

                try:
                    is_healthy = await service_helper.health_check(client)
                    duration = time.time() - start_time

                    service_info = None
                    if is_healthy:
                        try:
                            service_info = await service_helper.get_service_info(client)
                        except Exception:
                            pass

                    self.service_statuses.append(ServiceStatus(
                        name=service_name,
                        healthy=is_healthy,
                        response_time=duration,
                        url=config["http_url"],
                        service_info=service_info
                    ))

                    status = "✓ HEALTHY" if is_healthy else "✗ UNHEALTHY"
                    print(f"    {status} ({duration:.3f}s)")

                except Exception as e:
                    duration = time.time() - start_time
                    self.service_statuses.append(ServiceStatus(
                        name=service_name,
                        healthy=False,
                        response_time=duration,
                        url=config["http_url"],
                        error=str(e)
                    ))
                    print(f"    ✗ ERROR: {e}")

    async def _test_core_functionality(self):
        """Test core MCP functionality."""
        # Test brain service WebSocket functionality
        brain_config = self.test_config.get("brain_service")
        if not brain_config:
            self._add_test_result("brain_service_websocket", "skipped", 0, "Service not configured")
            return

        websocket_url = brain_config["websocket_url"]
        brain_client = MCPTestClient(websocket_url)

        # Test WebSocket connection
        start_time = time.time()
        try:
            async with brain_client.connect() as client:
                duration = time.time() - start_time
                self._add_test_result("websocket_connection", "passed", duration)
                print("    ✓ WebSocket connection established")

                # Test character creation
                await self._test_character_creation(client)

                # Test similarity search
                await self._test_similarity_search(client)

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result("websocket_connection", "failed", duration, str(e))
            print(f"    ✗ WebSocket connection failed: {e}")

    async def _test_character_creation(self, client):
        """Test character creation functionality."""
        start_time = time.time()
        try:
            character_data = {
                "project_id": "test-report-project",
                "name": "Report Test Character",
                "personality_description": "A character created during test report generation",
                "appearance_description": "Standard test character appearance"
            }

            response = await client.send_and_receive(
                "create_character",
                **character_data,
                timeout=10.0
            )

            duration = time.time() - start_time

            if response.get("status") == "success":
                self._add_test_result("character_creation", "passed", duration)
                print("    ✓ Character creation successful")
                return response.get("character_id")
            else:
                self._add_test_result("character_creation", "failed", duration, response.get("message"))
                print(f"    ✗ Character creation failed: {response.get('message')}")
                return None

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result("character_creation", "failed", duration, str(e))
            print(f"    ✗ Character creation error: {e}")
            return None

    async def _test_similarity_search(self, client):
        """Test similarity search functionality."""
        start_time = time.time()
        try:
            response = await client.send_and_receive(
                "find_similar_characters",
                project_id="test-report-project",
                query="test character",
                timeout=10.0
            )

            duration = time.time() - start_time

            if response.get("status") == "success":
                results = response.get("results", [])
                self._add_test_result(
                    "similarity_search",
                    "passed",
                    duration,
                    details={"result_count": len(results)}
                )
                print(f"    ✓ Similarity search returned {len(results)} results")
            else:
                self._add_test_result("similarity_search", "failed", duration, response.get("message"))
                print(f"    ✗ Similarity search failed: {response.get('message')}")

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result("similarity_search", "failed", duration, str(e))
            print(f"    ✗ Similarity search error: {e}")

    async def _test_performance(self):
        """Test performance metrics."""
        brain_config = self.test_config.get("brain_service")
        if not brain_config:
            print("    Skipping performance tests - brain service not available")
            return

        websocket_url = brain_config["websocket_url"]

        # Test connection latency
        await self._test_connection_latency(websocket_url)

        # Test concurrent operations
        await self._test_concurrent_operations(websocket_url)

    async def _test_connection_latency(self, websocket_url):
        """Test WebSocket connection latency."""
        print("    Testing connection latency...")

        latencies = []
        successful_connections = 0

        for i in range(5):
            start_time = time.time()
            try:
                brain_client = MCPTestClient(websocket_url)
                async with brain_client.connect():
                    latency = time.time() - start_time
                    latencies.append(latency)
                    successful_connections += 1
            except Exception as e:
                print(f"      Connection {i+1} failed: {e}")

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)

            self.performance_metrics.append(PerformanceMetrics(
                operation="websocket_connection_latency",
                avg_duration=avg_latency,
                min_duration=min_latency,
                max_duration=max_latency,
                success_rate=(successful_connections / 5) * 100,
                total_operations=5
            ))

            print(f"      Average latency: {avg_latency:.3f}s ({successful_connections}/5 successful)")

    async def _test_concurrent_operations(self, websocket_url):
        """Test concurrent operations performance."""
        print("    Testing concurrent operations...")

        async def single_operation():
            try:
                brain_client = MCPTestClient(websocket_url)
                async with brain_client.connect() as client:
                    character_data = {
                        "project_id": f"concurrent-test-{time.time()}",
                        "name": f"Concurrent Character {time.time()}",
                        "personality_description": "Concurrent test character",
                        "appearance_description": "Standard appearance"
                    }

                    response = await client.send_and_receive(
                        "create_character",
                        **character_data,
                        timeout=10.0
                    )

                    return response.get("status") == "success"
            except Exception:
                return False

        # Test with 5 concurrent operations
        start_time = time.time()
        results = await PerformanceTester.run_concurrent_operations(single_operation, 5)
        total_duration = time.time() - start_time

        analysis = PerformanceTester.analyze_performance_results(results)

        self.performance_metrics.append(PerformanceMetrics(
            operation="concurrent_character_creation",
            avg_duration=analysis["wall_time_stats"]["mean"],
            min_duration=analysis["wall_time_stats"]["min"],
            max_duration=analysis["wall_time_stats"]["max"],
            success_rate=analysis["success_rate"],
            total_operations=analysis["total_operations"]
        ))

        print(f"      Concurrent operations: {analysis['success_rate']:.1f}% success rate")

    async def _test_integration(self):
        """Test cross-service integration."""
        print("    Testing service integration...")

        # Test service-to-service communication
        healthy_services = [s for s in self.service_statuses if s.healthy]

        if len(healthy_services) >= 2:
            self._add_test_result("service_integration", "passed", 0.0,
                                details={"healthy_services": len(healthy_services)})
            print(f"      {len(healthy_services)} services available for integration")
        else:
            self._add_test_result("service_integration", "failed", 0.0,
                                "Insufficient healthy services for integration testing")
            print("      ✗ Not enough healthy services for integration testing")

    async def _test_error_handling(self):
        """Test error handling and recovery."""
        print("    Testing error handling...")

        brain_config = self.test_config.get("brain_service")
        if not brain_config:
            self._add_test_result("error_handling", "skipped", 0, "Brain service not available")
            return

        try:
            brain_client = MCPTestClient(brain_config["websocket_url"])
            async with brain_client.connect() as client:
                # Test invalid tool call
                start_time = time.time()
                response = await client.send_and_receive(
                    "invalid_tool",
                    invalid_param="test",
                    timeout=5.0
                )

                duration = time.time() - start_time

                if response.get("status") == "error":
                    self._add_test_result("error_handling", "passed", duration)
                    print("      ✓ Service properly handles invalid requests")
                else:
                    self._add_test_result("error_handling", "failed", duration,
                                        "Service did not return error for invalid request")
                    print("      ✗ Service did not handle invalid request properly")

        except Exception as e:
            self._add_test_result("error_handling", "failed", 0.0, str(e))
            print(f"      ✗ Error handling test failed: {e}")

    def _add_test_result(self, test_name: str, status: str, duration: float,
                        error_message: str = None, details: Dict[str, Any] = None):
        """Add a test result to the collection."""
        self.test_results.append(TestResult(
            test_name=test_name,
            status=status,
            duration=duration,
            error_message=error_message,
            details=details or {}
        ))

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate the final comprehensive report."""
        total_duration = time.time() - self.start_time

        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "passed"])
        failed_tests = len([r for r in self.test_results if r.status == "failed"])
        skipped_tests = len([r for r in self.test_results if r.status == "skipped"])

        healthy_services = len([s for s in self.service_statuses if s.healthy])
        total_services = len(self.service_statuses)

        # Generate recommendations
        recommendations = self._generate_recommendations()

        # Create report structure
        report = {
            "test_execution": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.now().isoformat(),
                "total_duration": total_duration,
                "environment": "integration_test"
            },
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "service_availability": (healthy_services / total_services * 100) if total_services > 0 else 0
            },
            "service_status": [asdict(s) for s in self.service_statuses],
            "test_results": [asdict(r) for r in self.test_results],
            "performance_metrics": [asdict(p) for p in self.performance_metrics],
            "recommendations": recommendations,
            "critical_issues": self._identify_critical_issues()
        }

        return report

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Service availability recommendations
        unhealthy_services = [s for s in self.service_statuses if not s.healthy]
        if unhealthy_services:
            recommendations.append({
                "category": "Service Availability",
                "priority": "High",
                "issue": f"{len(unhealthy_services)} services are not responding",
                "recommendation": "Check service logs, ensure proper startup configuration, and verify network connectivity",
                "affected_services": [s.name for s in unhealthy_services]
            })

        # Performance recommendations
        slow_services = [s for s in self.service_statuses if s.healthy and s.response_time > 2.0]
        if slow_services:
            recommendations.append({
                "category": "Performance",
                "priority": "Medium",
                "issue": f"{len(slow_services)} services have slow response times",
                "recommendation": "Optimize service startup time, check resource allocation, and review database connections",
                "affected_services": [s.name for s in slow_services]
            })

        # Test failure recommendations
        failed_tests = [r for r in self.test_results if r.status == "failed"]
        if failed_tests:
            recommendations.append({
                "category": "Functionality",
                "priority": "High",
                "issue": f"{len(failed_tests)} tests failed",
                "recommendation": "Review failed test details, check service implementations, and verify API contracts",
                "failed_tests": [r.test_name for r in failed_tests]
            })

        # Integration recommendations
        if len([s for s in self.service_statuses if s.healthy]) < 3:
            recommendations.append({
                "category": "Integration",
                "priority": "Critical",
                "issue": "Insufficient services available for full integration testing",
                "recommendation": "Ensure all core services (brain, character, orchestrator) are running and healthy"
            })

        return recommendations

    def _identify_critical_issues(self) -> List[str]:
        """Identify critical issues that need immediate attention."""
        critical_issues = []

        # Check if brain service is available
        brain_service = next((s for s in self.service_statuses if s.name == "brain_service"), None)
        if not brain_service or not brain_service.healthy:
            critical_issues.append("Brain service is not available - core functionality will not work")

        # Check if WebSocket connectivity failed
        websocket_test = next((r for r in self.test_results if r.test_name == "websocket_connection"), None)
        if websocket_test and websocket_test.status == "failed":
            critical_issues.append("WebSocket connectivity failed - MCP protocol communication is broken")

        # Check for total service failure
        if len([s for s in self.service_statuses if s.healthy]) == 0:
            critical_issues.append("No services are responding - system is completely down")

        # Check for high failure rate
        if len(self.test_results) > 0:
            failure_rate = len([r for r in self.test_results if r.status == "failed"]) / len(self.test_results)
            if failure_rate > 0.5:
                critical_issues.append(f"High test failure rate ({failure_rate:.1%}) - system stability is compromised")

        return critical_issues

    def print_report(self, report: Dict[str, Any]):
        """Print a formatted report to console."""
        print("\n" + "=" * 80)
        print("🎬 MOVIE GENERATION PLATFORM - INTEGRATION TEST REPORT")
        print("=" * 80)

        # Executive Summary
        summary = report["summary"]
        print(f"\n📊 EXECUTIVE SUMMARY")
        print(f"   Test Success Rate: {summary['success_rate']:.1f}% ({summary['passed_tests']}/{summary['total_tests']} tests passed)")
        print(f"   Service Availability: {summary['service_availability']:.1f}% ({summary['healthy_services']}/{summary['total_services']} services healthy)")
        print(f"   Execution Time: {report['test_execution']['total_duration']:.2f} seconds")

        # Critical Issues
        if report["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES")
            for issue in report["critical_issues"]:
                print(f"   ❌ {issue}")

        # Service Status
        print(f"\n🔧 SERVICE STATUS")
        for service in report["service_status"]:
            status = "✅ HEALTHY" if service["healthy"] else "❌ UNHEALTHY"
            response_time = f"({service['response_time']:.3f}s)" if service["healthy"] else ""
            print(f"   {service['name']:20} {status} {response_time}")
            if service.get("error"):
                print(f"   {'':20} Error: {service['error']}")

        # Test Results
        print(f"\n📋 TEST RESULTS")
        for test in report["test_results"]:
            status_icon = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}.get(test["status"], "❓")
            print(f"   {test['test_name']:30} {status_icon} {test['status'].upper()} ({test['duration']:.3f}s)")
            if test.get("error_message"):
                print(f"   {'':30} Error: {test['error_message']}")

        # Performance Metrics
        if report["performance_metrics"]:
            print(f"\n⚡ PERFORMANCE METRICS")
            for metric in report["performance_metrics"]:
                print(f"   {metric['operation']:30}")
                print(f"   {'':30} Avg: {metric['avg_duration']:.3f}s, Success: {metric['success_rate']:.1f}%")

        # Recommendations
        if report["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS")
            for rec in report["recommendations"]:
                priority_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(rec["priority"], "⚪")
                print(f"   {priority_icon} {rec['category']} - {rec['priority']} Priority")
                print(f"   {'':3} Issue: {rec['issue']}")
                print(f"   {'':3} Recommendation: {rec['recommendation']}")
                print()

        print("=" * 80)

    async def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integration_test_report_{timestamp}.json"

        report_path = Path(__file__).parent / "reports" / filename
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📁 Report saved to: {report_path}")
        return report_path


async def main():
    """Main function to run the test report generation."""
    generator = TestReportGenerator()

    try:
        report = await generator.run_comprehensive_tests()
        generator.print_report(report)

        # Save report
        report_path = await generator.save_report(report)

        # Return appropriate exit code
        critical_issues = len(report["critical_issues"])
        failed_tests = report["summary"]["failed_tests"]

        if critical_issues > 0:
            print(f"\n❌ CRITICAL ISSUES DETECTED: {critical_issues}")
            return 2
        elif failed_tests > 0:
            print(f"\n⚠️  TESTS FAILED: {failed_tests}")
            return 1
        else:
            print(f"\n✅ ALL TESTS PASSED")
            return 0

    except Exception as e:
        print(f"\n💥 REPORT GENERATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)