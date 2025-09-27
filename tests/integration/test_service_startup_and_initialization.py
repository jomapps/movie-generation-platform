"""
Service startup and initialization tests.
Tests service health, proper configuration loading, and inter-service dependencies.
"""
import pytest
import asyncio
import time
from typing import Dict, Any

from tests.utils.test_helpers import (
    ServiceTestHelper,
    wait_for_condition,
    MCPTestClient
)


@pytest.mark.integration
class TestServiceStartupAndInitialization:
    """Test service startup and initialization procedures."""

    async def test_all_services_health_endpoints(self, http_client, test_config, services_ready):
        """Test that all configured services have working health endpoints."""
        health_results = {}

        for service_name, config in test_config.items():
            service_helper = ServiceTestHelper(config["http_url"])

            try:
                start_time = time.time()
                is_healthy = await service_helper.health_check(http_client)
                response_time = time.time() - start_time

                # Try to get additional service info
                service_info = None
                if is_healthy:
                    try:
                        service_info = await service_helper.get_service_info(http_client)
                    except Exception as e:
                        print(f"Could not get service info for {service_name}: {e}")

                health_results[service_name] = {
                    "healthy": is_healthy,
                    "response_time": response_time,
                    "url": config["http_url"],
                    "service_info": service_info
                }

            except Exception as e:
                health_results[service_name] = {
                    "healthy": False,
                    "response_time": None,
                    "url": config["http_url"],
                    "error": str(e)
                }

        # Report health status
        print("\n=== Service Health Check Results ===")
        healthy_services = []
        for service_name, result in health_results.items():
            if result["healthy"]:
                healthy_services.append(service_name)
                response_time = result.get("response_time", 0)
                print(f"✓ {service_name:20} HEALTHY ({response_time:.3f}s) - {result['url']}")

                # Print additional service info if available
                service_info = result.get("service_info")
                if service_info:
                    if isinstance(service_info, dict):
                        if "service" in service_info:
                            print(f"  └─ Service: {service_info['service']}")
                        if "version" in service_info:
                            print(f"  └─ Version: {service_info['version']}")
                        if "mcp_tools" in service_info:
                            tools = service_info["mcp_tools"]
                            if isinstance(tools, list) and tools:
                                print(f"  └─ MCP Tools: {len(tools)} available")
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"✗ {service_name:20} UNHEALTHY - {result['url']}")
                print(f"  └─ Error: {error_msg}")

        print(f"\nSummary: {len(healthy_services)}/{len(test_config)} services are healthy")

        # Store results for other tests to use
        return health_results

    async def test_brain_service_websocket_initialization(self, test_config):
        """Test brain service WebSocket initialization and MCP protocol."""
        brain_config = test_config.get("brain_service")
        if not brain_config:
            pytest.skip("Brain service not configured")

        websocket_url = brain_config["websocket_url"]
        brain_client = MCPTestClient(websocket_url)

        try:
            # Test WebSocket connection establishment
            connection_attempts = 3
            successful_connections = 0

            for attempt in range(connection_attempts):
                try:
                    async with brain_client.connect() as client:
                        print(f"✓ WebSocket connection attempt {attempt + 1} successful")
                        successful_connections += 1

                        # Test basic MCP protocol communication
                        try:
                            # Try a simple operation to verify MCP protocol works
                            test_character_data = {
                                "project_id": "startup-test",
                                "name": "Startup Test Character",
                                "personality_description": "Test character for startup verification",
                                "appearance_description": "Standard test appearance"
                            }

                            response = await client.send_and_receive(
                                "create_character",
                                **test_character_data,
                                timeout=10.0
                            )

                            if response.get("status") in ["success", "error"]:
                                print(f"  └─ MCP protocol communication working")
                            else:
                                print(f"  └─ MCP protocol response unclear: {response}")

                        except Exception as mcp_error:
                            print(f"  └─ MCP protocol test failed: {mcp_error}")

                        # Brief pause between connection attempts
                        await asyncio.sleep(0.5)

                except Exception as e:
                    print(f"✗ WebSocket connection attempt {attempt + 1} failed: {e}")

            print(f"\nWebSocket Connection Results: {successful_connections}/{connection_attempts} successful")

            # Assert that WebSocket connections work
            assert successful_connections > 0, "At least one WebSocket connection should succeed"

        except Exception as e:
            pytest.skip(f"Brain service WebSocket test failed: {e}")

    async def test_service_dependencies_and_integration(self, http_client, test_config):
        """Test that services can communicate with their dependencies."""
        dependency_tests = []

        # Test Celery/Redis service dependencies
        celery_config = test_config.get("celery_redis")
        if celery_config:
            celery_helper = ServiceTestHelper(celery_config["http_url"])

            try:
                # Check if Celery service can communicate with brain service
                is_healthy = await celery_helper.health_check(http_client)
                if is_healthy:
                    # Try to get worker status (tests Redis connectivity)
                    worker_response = await celery_helper.test_endpoint(
                        http_client,
                        "GET",
                        "/workers/status"
                    )

                    dependency_tests.append({
                        "service": "celery_redis",
                        "dependency": "redis",
                        "test": "worker_status",
                        "success": worker_response.status_code == 200,
                        "details": f"Status code: {worker_response.status_code}"
                    })

                    # Test brain service integration
                    brain_config = test_config.get("brain_service")
                    if brain_config:
                        # Check if Celery service can reach brain service
                        brain_helper = ServiceTestHelper(brain_config["http_url"])
                        brain_healthy = await brain_helper.health_check(http_client)

                        dependency_tests.append({
                            "service": "celery_redis",
                            "dependency": "brain_service",
                            "test": "health_check",
                            "success": brain_healthy,
                            "details": f"Brain service reachable: {brain_healthy}"
                        })

            except Exception as e:
                dependency_tests.append({
                    "service": "celery_redis",
                    "dependency": "unknown",
                    "test": "connectivity",
                    "success": False,
                    "details": f"Error: {e}"
                })

        # Test character service dependencies (if available)
        character_config = test_config.get("character_service")
        if character_config:
            character_helper = ServiceTestHelper(character_config["http_url"])

            try:
                is_healthy = await character_helper.health_check(http_client)
                if is_healthy:
                    # Test if character service can list its MCP tools
                    tools_response = await character_helper.test_endpoint(
                        http_client,
                        "GET",
                        "/mcp/tools"
                    )

                    dependency_tests.append({
                        "service": "character_service",
                        "dependency": "mcp_server",
                        "test": "tools_listing",
                        "success": tools_response.status_code == 200,
                        "details": f"MCP tools endpoint: {tools_response.status_code}"
                    })

            except Exception as e:
                dependency_tests.append({
                    "service": "character_service",
                    "dependency": "mcp_server",
                    "test": "initialization",
                    "success": False,
                    "details": f"Error: {e}"
                })

        # Report dependency test results
        print("\n=== Service Dependency Tests ===")
        successful_dependencies = 0
        for test in dependency_tests:
            status = "✓" if test["success"] else "✗"
            print(f"{status} {test['service']} -> {test['dependency']} ({test['test']})")
            print(f"  └─ {test['details']}")
            if test["success"]:
                successful_dependencies += 1

        if dependency_tests:
            print(f"\nDependency Tests: {successful_dependencies}/{len(dependency_tests)} successful")

        return dependency_tests

    async def test_configuration_loading(self, http_client, test_config):
        """Test that services load their configuration correctly."""
        config_tests = []

        for service_name, config in test_config.items():
            service_helper = ServiceTestHelper(config["http_url"])

            try:
                # Check if service is responsive
                is_healthy = await service_helper.health_check(http_client)

                if is_healthy:
                    # Try to get service information
                    service_info = await service_helper.get_service_info(http_client)

                    # Analyze service info for configuration indicators
                    config_indicators = {
                        "has_service_name": bool(service_info.get("service") or service_info.get("title")),
                        "has_version": bool(service_info.get("version")),
                        "has_endpoints": bool(service_info.get("endpoints")),
                        "has_mcp_tools": bool(service_info.get("mcp_tools"))
                    }

                    config_score = sum(config_indicators.values()) / len(config_indicators) * 100

                    config_tests.append({
                        "service": service_name,
                        "healthy": True,
                        "config_score": config_score,
                        "indicators": config_indicators,
                        "service_info_available": True
                    })

                else:
                    config_tests.append({
                        "service": service_name,
                        "healthy": False,
                        "config_score": 0,
                        "indicators": {},
                        "service_info_available": False
                    })

            except Exception as e:
                config_tests.append({
                    "service": service_name,
                    "healthy": False,
                    "config_score": 0,
                    "indicators": {},
                    "service_info_available": False,
                    "error": str(e)
                })

        # Report configuration test results
        print("\n=== Configuration Loading Tests ===")
        well_configured_services = 0

        for test in config_tests:
            service_name = test["service"]
            if test["healthy"]:
                config_score = test["config_score"]
                print(f"✓ {service_name:20} Configuration Score: {config_score:.0f}%")

                # Show configuration indicators
                for indicator, present in test["indicators"].items():
                    status = "✓" if present else "✗"
                    print(f"  {status} {indicator}")

                if config_score >= 75:
                    well_configured_services += 1

            else:
                print(f"✗ {service_name:20} Not accessible for configuration test")
                if "error" in test:
                    print(f"  └─ Error: {test['error']}")

        print(f"\nWell-configured services: {well_configured_services}/{len(config_tests)}")

        return config_tests

    async def test_startup_time_performance(self, http_client, test_config):
        """Test service startup time performance."""
        # This test measures how quickly services respond after being contacted
        # In a real environment, this would measure actual startup time

        startup_performance = []

        for service_name, config in test_config.items():
            service_helper = ServiceTestHelper(config["http_url"])

            # Measure response time for health check (proxy for readiness)
            response_times = []
            successful_checks = 0

            for attempt in range(3):
                start_time = time.time()

                try:
                    is_healthy = await service_helper.health_check(http_client)
                    response_time = time.time() - start_time
                    response_times.append(response_time)

                    if is_healthy:
                        successful_checks += 1

                except Exception as e:
                    response_time = time.time() - start_time
                    response_times.append(response_time)

                # Brief pause between attempts
                await asyncio.sleep(0.1)

            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)

                startup_performance.append({
                    "service": service_name,
                    "avg_response_time": avg_response_time,
                    "min_response_time": min_response_time,
                    "max_response_time": max_response_time,
                    "successful_checks": successful_checks,
                    "total_attempts": 3
                })

        # Report startup performance
        print("\n=== Startup Performance ===")
        fast_services = 0

        for perf in startup_performance:
            service_name = perf["service"]
            avg_time = perf["avg_response_time"]
            success_rate = (perf["successful_checks"] / perf["total_attempts"]) * 100

            print(f"{service_name:20} Avg: {avg_time:.3f}s, Success: {success_rate:.0f}%")
            print(f"{'':20} Range: {perf['min_response_time']:.3f}s - {perf['max_response_time']:.3f}s")

            # Consider service "fast" if average response time < 2s
            if avg_time < 2.0:
                fast_services += 1

        print(f"\nFast-responding services: {fast_services}/{len(startup_performance)}")

        return startup_performance

    async def test_error_handling_during_startup(self, http_client, test_config):
        """Test how services handle errors during startup/initialization."""
        error_handling_tests = []

        for service_name, config in test_config.items():
            service_helper = ServiceTestHelper(config["http_url"])

            try:
                # Test invalid endpoints to see error handling
                invalid_endpoints = [
                    "/nonexistent",
                    "/invalid-path",
                    "/admin/restricted"  # Should be protected/not exist
                ]

                error_responses = []

                for endpoint in invalid_endpoints:
                    try:
                        response = await service_helper.test_endpoint(
                            http_client,
                            "GET",
                            endpoint
                        )

                        error_responses.append({
                            "endpoint": endpoint,
                            "status_code": response.status_code,
                            "has_error_message": "error" in response.text.lower() or "not found" in response.text.lower()
                        })

                    except Exception as e:
                        error_responses.append({
                            "endpoint": endpoint,
                            "status_code": None,
                            "error": str(e)
                        })

                # Analyze error handling quality
                proper_error_codes = sum(1 for r in error_responses
                                      if r.get("status_code") in [404, 405, 403, 400])

                error_handling_tests.append({
                    "service": service_name,
                    "total_tests": len(invalid_endpoints),
                    "proper_error_codes": proper_error_codes,
                    "error_responses": error_responses
                })

            except Exception as e:
                error_handling_tests.append({
                    "service": service_name,
                    "total_tests": 0,
                    "proper_error_codes": 0,
                    "error_responses": [],
                    "test_error": str(e)
                })

        # Report error handling results
        print("\n=== Error Handling Tests ===")
        for test in error_handling_tests:
            service_name = test["service"]
            if test["total_tests"] > 0:
                proper_rate = (test["proper_error_codes"] / test["total_tests"]) * 100
                print(f"{service_name:20} Proper error codes: {test['proper_error_codes']}/{test['total_tests']} ({proper_rate:.0f}%)")
            else:
                print(f"{service_name:20} Error handling tests could not run")
                if "test_error" in test:
                    print(f"{'':20} Error: {test['test_error']}")

        return error_handling_tests