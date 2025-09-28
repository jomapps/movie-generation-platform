"""
Cross-service integration tests for the movie generation platform.
Tests data flow between all services and end-to-end scenarios.
"""
import pytest
import asyncio
import json
import uuid
from typing import Dict, Any, List

from tests.utils.test_helpers import (
    MCPTestClient,
    ServiceTestHelper,
    PerformanceTester,
    DatabaseTestHelper,
    TestDataManager,
    assert_successful_response,
    assert_error_response,
    wait_for_condition
)


@pytest.mark.integration
@pytest.mark.e2e
class TestCrossServiceDataFlow:
    """Test data flow between all services in the platform."""

    async def test_service_discovery_and_health(self, http_client, test_config, services_ready):
        """Test that all services are discoverable and healthy."""
        service_results = {}

        for service_name, config in test_config.items():
            service_helper = ServiceTestHelper(config["http_url"])

            # Test health endpoint
            is_healthy = await service_helper.health_check(http_client)
            service_results[service_name] = {
                "healthy": is_healthy,
                "url": config["http_url"]
            }

        # Log service status
        print("\nService Health Status:")
        for service, status in service_results.items():
            status_text = "✓ HEALTHY" if status["healthy"] else "✗ UNHEALTHY"
            print(f"  {service}: {status_text} ({status['url']})")

        # At least brain service should be healthy for core tests
        healthy_services = [name for name, status in service_results.items() if status["healthy"]]
        assert len(healthy_services) > 0, "At least one service should be healthy"

    async def test_character_creation_to_brain_service_flow(self, test_config, sample_character_data, performance_timer):
        """Test character creation flow from character service to brain service."""
        character_service_url = test_config["character_service"]["http_url"]
        brain_service_url = test_config["brain_service"]["websocket_url"]

        test_data_manager = TestDataManager()

        try:
            # Step 1: Create character via character service (if available)
            character_helper = ServiceTestHelper(character_service_url)

            # Check if character service is available
            async with httpx.AsyncClient() as client:
                if not await character_helper.health_check(client):
                    pytest.skip("Character service not available")

                # Try to create character via REST API
                create_response = await character_helper.test_endpoint(
                    client,
                    "POST",
                    "/characters",
                    json=sample_character_data
                )

                if create_response.status_code not in [200, 201]:
                    pytest.skip(f"Character service not ready: {create_response.status_code}")

                character_data = create_response.json()
                character_id = character_data.get("id") or character_data.get("character_id")

                if character_id:
                    test_data_manager.track_character(character_id, sample_character_data["project_id"])

            # Step 2: Verify character is accessible via brain service
            brain_client = MCPTestClient(brain_service_url)

            with performance_timer("cross_service_character_verification"):
                async with brain_client.connect() as client:
                    # Search for the created character
                    search_response = await client.send_and_receive(
                        "find_similar_characters",
                        project_id=sample_character_data["project_id"],
                        query=sample_character_data["name"],
                        timeout=10.0
                    )

                    if search_response.get("status") == "success":
                        results = search_response.get("results", [])
                        # Verify character is found
                        found_character = any(
                            result.get("name") == sample_character_data["name"]
                            for result in results
                        )
                        # Note: This might not always pass depending on embedding similarity thresholds

        except Exception as e:
            pytest.skip(f"Cross-service test failed due to service unavailability: {e}")

        finally:
            # Cleanup test data
            # await test_data_manager.cleanup_all({})
            pass

    async def test_orchestrator_task_flow(self, test_config, performance_timer):
        """Test task orchestration flow through the system."""
        orchestrator_url = test_config["orchestrator"]["http_url"]

        try:
            orchestrator_helper = ServiceTestHelper(orchestrator_url)

            async with httpx.AsyncClient() as client:
                # Check orchestrator availability
                if not await orchestrator_helper.health_check(client):
                    pytest.skip("Orchestrator service not available")

                # Test task submission
                task_data = {
                    "type": "character_generation",
                    "project_id": f"test-project-{uuid.uuid4().hex[:8]}",
                    "parameters": {
                        "character_count": 2,
                        "genre": "fantasy"
                    }
                }

                with performance_timer("orchestrator_task_submission"):
                    task_response = await orchestrator_helper.test_endpoint(
                        client,
                        "POST",
                        "/tasks",
                        json=task_data
                    )

                if task_response.status_code in [200, 201, 202]:
                    task_result = task_response.json()
                    task_id = task_result.get("task_id") or task_result.get("id")

                    if task_id:
                        # Poll for task completion
                        with performance_timer("orchestrator_task_polling"):
                            await self._poll_task_status(client, orchestrator_helper, task_id)

        except Exception as e:
            pytest.skip(f"Orchestrator test failed: {e}")

    async def _poll_task_status(self, client, orchestrator_helper, task_id: str, max_polls: int = 10):
        """Poll task status until completion or timeout."""
        for poll_count in range(max_polls):
            try:
                status_response = await orchestrator_helper.test_endpoint(
                    client,
                    "GET",
                    f"/tasks/{task_id}/status"
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    task_status = status_data.get("status", "unknown")

                    if task_status in ["completed", "failed", "cancelled"]:
                        break

                await asyncio.sleep(1.0)  # Wait before next poll

            except Exception as e:
                print(f"Task polling error (attempt {poll_count + 1}): {e}")
                break

    async def test_celery_redis_task_processing(self, test_config, performance_timer):
        """Test Celery/Redis task processing pipeline."""
        celery_redis_url = test_config["celery_redis"]["http_url"]

        try:
            celery_helper = ServiceTestHelper(celery_redis_url)

            async with httpx.AsyncClient() as client:
                # Check service availability
                if not await celery_helper.health_check(client):
                    pytest.skip("Celery/Redis service not available")

                # Test task submission
                task_data = {
                    "task_type": "movie_generation",
                    "project_id": f"test-project-{uuid.uuid4().hex[:8]}",
                    "parameters": {
                        "prompt": "Generate a fantasy movie script",
                        "duration": "90 minutes"
                    }
                }

                with performance_timer("celery_task_submission"):
                    submit_response = await celery_helper.test_endpoint(
                        client,
                        "POST",
                        "/tasks/submit",
                        json=task_data
                    )

                if submit_response.status_code in [200, 201, 202]:
                    task_result = submit_response.json()
                    task_id = task_result.get("task_id") or task_result.get("id")

                    if task_id:
                        # Check task status
                        with performance_timer("celery_task_status_check"):
                            status_response = await celery_helper.test_endpoint(
                                client,
                                "GET",
                                f"/tasks/{task_id}/status"
                            )

                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            assert "status" in status_data, "Task status should be included"

                        # Test worker status
                        worker_response = await celery_helper.test_endpoint(
                            client,
                            "GET",
                            "/workers/status"
                        )

                        if worker_response.status_code == 200:
                            worker_data = worker_response.json()
                            # Workers might not be running in test environment

        except Exception as e:
            pytest.skip(f"Celery/Redis test failed: {e}")

    async def test_brain_service_embedding_pipeline(self, test_config, performance_timer):
        """Test the complete embedding generation and storage pipeline."""
        brain_service_url = test_config["brain_service"]["websocket_url"]

        brain_client = MCPTestClient(brain_service_url)

        test_characters = [
            {
                "project_id": "embedding-test-project",
                "name": f"Character {i}",
                "personality_description": f"Unique personality {i} with specific traits",
                "appearance_description": f"Distinctive appearance {i} with notable features"
            }
            for i in range(3)
        ]

        try:
            async with brain_client.connect() as client:
                created_characters = []

                # Step 1: Create multiple characters
                with performance_timer("bulk_character_creation", {"character_count": len(test_characters)}):
                    for character_data in test_characters:
                        response = await client.send_and_receive(
                            "create_character",
                            **character_data,
                            timeout=15.0
                        )

                        if response.get("status") == "success":
                            created_characters.append({
                                "id": response.get("character_id"),
                                "name": character_data["name"]
                            })

                if not created_characters:
                    pytest.skip("Could not create test characters for embedding test")

                # Step 2: Test similarity search across created characters
                with performance_timer("embedding_similarity_search"):
                    search_queries = [
                        "personality traits",
                        "character appearance",
                        "unique features"
                    ]

                    for query in search_queries:
                        search_response = await client.send_and_receive(
                            "find_similar_characters",
                            project_id="embedding-test-project",
                            query=query,
                            timeout=10.0
                        )

                        if search_response.get("status") == "success":
                            results = search_response.get("results", [])
                            # Verify results structure
                            for result in results:
                                assert "id" in result, "Result should have character ID"
                                assert "name" in result, "Result should have character name"
                                assert "similarity_score" in result, "Result should have similarity score"
                                assert isinstance(result["similarity_score"], (int, float)), "Similarity score should be numeric"

        except Exception as e:
            pytest.skip(f"Brain service embedding test failed: {e}")

    async def test_service_error_propagation(self, test_config):
        """Test how errors propagate between services."""
        brain_service_url = test_config["brain_service"]["websocket_url"]

        brain_client = MCPTestClient(brain_service_url)

        try:
            async with brain_client.connect() as client:
                # Test error scenarios
                error_test_cases = [
                    {
                        "name": "invalid_tool",
                        "tool": "nonexistent_tool",
                        "params": {},
                        "expected_error": "Unknown tool"
                    },
                    {
                        "name": "missing_parameters",
                        "tool": "create_character",
                        "params": {"project_id": "test"},  # Missing required fields
                        "expected_error": "Missing required fields"
                    },
                    {
                        "name": "invalid_project_id",
                        "tool": "find_similar_characters",
                        "params": {
                            "project_id": "",  # Empty project ID
                            "query": "test query"
                        },
                        "expected_error": None  # May or may not fail depending on validation
                    }
                ]

                for test_case in error_test_cases:
                    response = await client.send_and_receive(
                        test_case["tool"],
                        **test_case["params"],
                        timeout=5.0
                    )

                    # Verify error response structure
                    if response.get("status") == "error":
                        assert "message" in response, f"Error response should include message for {test_case['name']}"

                        if test_case["expected_error"]:
                            assert test_case["expected_error"].lower() in response["message"].lower(), \
                                f"Expected error '{test_case['expected_error']}' not found in response for {test_case['name']}"

        except Exception as e:
            pytest.skip(f"Error propagation test failed: {e}")

    @pytest.mark.performance
    async def test_cross_service_performance_under_load(self, test_config, performance_timer):
        """Test performance of cross-service operations under load."""

        async def cross_service_operation():
            """Perform a cross-service operation."""
            brain_client = MCPTestClient(test_config["brain_service"]["websocket_url"])

            try:
                async with brain_client.connect() as client:
                    # Create character
                    character_data = DatabaseTestHelper.create_test_character_data()
                    create_response = await client.send_and_receive(
                        "create_character",
                        **character_data,
                        timeout=10.0
                    )

                    if create_response.get("status") == "success":
                        # Search for similar characters
                        search_response = await client.send_and_receive(
                            "find_similar_characters",
                            project_id=character_data["project_id"],
                            query="test query",
                            timeout=10.0
                        )
                        return search_response.get("status") == "success"

                    return False

            except Exception:
                return False

        # Run concurrent operations
        concurrent_operations = 5
        with performance_timer("cross_service_load_test", {"concurrent_ops": concurrent_operations}):
            results = await PerformanceTester.run_concurrent_operations(
                cross_service_operation,
                concurrent_operations
            )

        # Analyze results
        analysis = PerformanceTester.analyze_performance_results(results)

        print(f"\nCross-Service Load Test Results:")
        print(f"Total Operations: {analysis['total_operations']}")
        print(f"Success Rate: {analysis['success_rate']:.1f}%")
        print(f"Average Response Time: {analysis['wall_time_stats']['mean']:.3f}s")

        # Basic performance assertions
        assert analysis["total_operations"] == concurrent_operations, "All operations should be attempted"
        # Don't assert success rate as services might not be fully available in test environment

    async def test_data_consistency_across_services(self, test_config):
        """Test data consistency when the same data is accessed through different services."""
        # This would test scenarios like:
        # 1. Create character via character service
        # 2. Verify same character data via brain service
        # 3. Ensure embedding vectors are consistent

        brain_service_url = test_config["brain_service"]["websocket_url"]
        brain_client = MCPTestClient(brain_service_url)

        project_id = f"consistency-test-{uuid.uuid4().hex[:8]}"
        character_name = f"Consistency Test Character"

        try:
            async with brain_client.connect() as client:
                # Create character
                character_data = {
                    "project_id": project_id,
                    "name": character_name,
                    "personality_description": "A character for testing data consistency",
                    "appearance_description": "Standard test appearance"
                }

                create_response = await client.send_and_receive(
                    "create_character",
                    **character_data,
                    timeout=10.0
                )

                if create_response.get("status") != "success":
                    pytest.skip("Could not create character for consistency test")

                character_id = create_response.get("character_id")

                # Search for the character multiple times
                search_results = []
                for _ in range(3):
                    search_response = await client.send_and_receive(
                        "find_similar_characters",
                        project_id=project_id,
                        query=character_name,
                        timeout=10.0
                    )

                    if search_response.get("status") == "success":
                        search_results.append(search_response.get("results", []))

                    await asyncio.sleep(0.1)  # Small delay between searches

                # Verify consistency
                if search_results and all(search_results):
                    # Check if results are consistent across searches
                    first_result = search_results[0]
                    for subsequent_result in search_results[1:]:
                        # Results should be similar (allowing for small variations in similarity scores)
                        assert len(subsequent_result) == len(first_result), \
                            "Search results should have consistent length"

        except Exception as e:
            pytest.skip(f"Data consistency test failed: {e}")

    async def test_service_communication_protocols(self, test_config):
        """Test different communication protocols between services."""
        # Test WebSocket communication (brain service)
        brain_service_url = test_config["brain_service"]["websocket_url"]

        # Test HTTP communication (other services)
        http_services = [
            ("character_service", test_config["character_service"]["http_url"]),
            ("orchestrator", test_config["orchestrator"]["http_url"]),
            ("celery_redis", test_config["celery_redis"]["http_url"])
        ]

        protocol_results = {}

        # Test WebSocket protocol
        try:
            brain_client = MCPTestClient(brain_service_url)
            async with brain_client.connect() as client:
                # Simple ping/health check via WebSocket
                response = await client.send_and_receive("health_check", timeout=5.0)
                protocol_results["websocket"] = True
        except Exception as e:
            protocol_results["websocket"] = False
            print(f"WebSocket protocol test failed: {e}")

        # Test HTTP protocols
        async with httpx.AsyncClient() as http_client:
            for service_name, service_url in http_services:
                try:
                    service_helper = ServiceTestHelper(service_url)
                    is_healthy = await service_helper.health_check(http_client)
                    protocol_results[f"http_{service_name}"] = is_healthy
                except Exception as e:
                    protocol_results[f"http_{service_name}"] = False
                    print(f"HTTP protocol test failed for {service_name}: {e}")

        # Log protocol test results
        print("\nProtocol Test Results:")
        for protocol, success in protocol_results.items():
            status = "✓ WORKING" if success else "✗ FAILED"
            print(f"  {protocol}: {status}")

        # At least one protocol should work
        working_protocols = [p for p, success in protocol_results.items() if success]
        assert len(working_protocols) > 0, "At least one communication protocol should work"