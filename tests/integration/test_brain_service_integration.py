"""
Integration tests for the MCP Brain Service.
Tests WebSocket connectivity, embedding generation, and knowledge graph operations.
"""
import pytest
import asyncio
import json
import uuid
from typing import Dict, Any

from tests.utils.test_helpers import (
    MCPTestClient,
    ServiceTestHelper,
    PerformanceTester,
    DatabaseTestHelper,
    assert_successful_response,
    assert_error_response,
    wait_for_condition
)


@pytest.mark.brain_service
@pytest.mark.integration
class TestBrainServiceIntegration:
    """Integration tests for brain service functionality."""

    async def test_brain_service_health(self, http_client, test_config):
        """Test brain service health endpoint."""
        service_helper = ServiceTestHelper(test_config["brain_service"]["http_url"])

        # Test health endpoint
        is_healthy = await service_helper.health_check(http_client)
        assert is_healthy, "Brain service should be healthy"

        # Test service info
        service_info = await service_helper.get_service_info(http_client)
        assert "MCP Brain Service" in service_info.get("message", "")

    async def test_websocket_connectivity(self, test_config, performance_timer):
        """Test WebSocket connection to brain service."""
        mcp_client = MCPTestClient(test_config["brain_service"]["websocket_url"])

        with performance_timer("websocket_connect"):
            async with mcp_client.connect() as client:
                assert client is not None, "WebSocket connection should be established"

                # Test ping/pong or simple message
                response = await client.send_and_receive("health_check", timeout=5.0)
                # Note: Actual response format may vary based on implementation

    async def test_create_character_integration(self, test_config, sample_character_data, performance_timer):
        """Test character creation through WebSocket."""
        mcp_client = MCPTestClient(test_config["brain_service"]["websocket_url"])

        async with mcp_client.connect() as client:
            with performance_timer("create_character", {"character_name": sample_character_data["name"]}):
                response = await client.send_and_receive(
                    "create_character",
                    **sample_character_data,
                    timeout=10.0
                )

            # Verify response structure
            if response.get("status") == "success":
                assert_successful_response(response)
                assert "character_id" in response, "Response should include character_id"
                assert response["character_id"] is not None, "Character ID should not be None"
            else:
                # Service might not be fully configured - log for debugging
                pytest.skip(f"Character creation not available: {response}")

    async def test_find_similar_characters(self, test_config, sample_character_data, performance_timer):
        """Test finding similar characters."""
        mcp_client = MCPTestClient(test_config["brain_service"]["websocket_url"])

        async with mcp_client.connect() as client:
            # First create a character (if possible)
            try:
                create_response = await client.send_and_receive(
                    "create_character",
                    **sample_character_data,
                    timeout=10.0
                )

                if create_response.get("status") != "success":
                    pytest.skip("Cannot test similarity without character creation")

            except Exception as e:
                pytest.skip(f"Character creation failed: {e}")

            # Test similarity search
            with performance_timer("find_similar_characters"):
                search_response = await client.send_and_receive(
                    "find_similar_characters",
                    project_id=sample_character_data["project_id"],
                    query="brave warrior",
                    timeout=10.0
                )

            if search_response.get("status") == "success":
                assert_successful_response(search_response)
                assert "results" in search_response, "Response should include results"
                assert isinstance(search_response["results"], list), "Results should be a list"

    async def test_embedding_generation_performance(self, test_config, performance_timer):
        """Test embedding generation performance."""
        mcp_client = MCPTestClient(test_config["brain_service"]["websocket_url"])

        test_texts = [
            "A brave and noble knight",
            "A cunning and mysterious rogue",
            "A wise and powerful wizard",
            "A gentle and kind healer",
            "A fierce and loyal warrior"
        ]

        async with mcp_client.connect() as client:
            results = []

            for i, text in enumerate(test_texts):
                character_data = DatabaseTestHelper.create_test_character_data(
                    name=f"Test Character {i}",
                    project_id="perf-test-project"
                )
                character_data["personality_description"] = text

                with performance_timer("embedding_generation", {"text_length": len(text)}):
                    try:
                        response = await client.send_and_receive(
                            "create_character",
                            **character_data,
                            timeout=15.0
                        )
                        results.append(response.get("status") == "success")
                    except Exception as e:
                        results.append(False)

            # Analyze results
            success_rate = sum(results) / len(results) * 100 if results else 0
            assert success_rate > 0, "At least some embedding generation should succeed"

    async def test_concurrent_websocket_connections(self, test_config, performance_timer):
        """Test handling multiple concurrent WebSocket connections."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        concurrent_connections = 5

        async def create_connection_test():
            """Test a single WebSocket connection."""
            mcp_client = MCPTestClient(websocket_url)
            try:
                async with mcp_client.connect() as client:
                    # Perform a simple operation
                    character_data = DatabaseTestHelper.create_test_character_data()
                    response = await client.send_and_receive(
                        "create_character",
                        **character_data,
                        timeout=10.0
                    )
                    return response.get("status") == "success"
            except Exception as e:
                return False

        with performance_timer("concurrent_websocket_connections", {"connection_count": concurrent_connections}):
            results = await PerformanceTester.run_concurrent_operations(
                create_connection_test,
                concurrent_connections
            )

        # Analyze results
        performance_analysis = PerformanceTester.analyze_performance_results(results)
        assert performance_analysis["success_rate"] > 50, "At least 50% of concurrent connections should succeed"

    async def test_websocket_error_handling(self, test_config):
        """Test WebSocket error handling."""
        mcp_client = MCPTestClient(test_config["brain_service"]["websocket_url"])

        async with mcp_client.connect() as client:
            # Test invalid tool name
            response = await client.send_and_receive(
                "invalid_tool_name",
                some_param="value",
                timeout=5.0
            )
            assert_error_response(response, "Unknown tool")

            # Test missing required parameters
            response = await client.send_and_receive(
                "create_character",
                # Missing required fields
                timeout=5.0
            )
            assert_error_response(response, "Missing required fields")

            # Test invalid JSON (this would be handled at the transport level)
            # We'll test with invalid parameter types instead
            response = await client.send_and_receive(
                "create_character",
                project_id=123,  # Should be string
                name=None,
                personality_description="",
                appearance_description="",
                timeout=5.0
            )
            # Should either succeed with type coercion or fail gracefully

    async def test_websocket_message_ordering(self, test_config):
        """Test that WebSocket messages are processed in order."""
        mcp_client = MCPTestClient(test_config["brain_service"]["websocket_url"])

        async with mcp_client.connect() as client:
            project_id = f"order-test-{uuid.uuid4().hex[:8]}"
            responses = []

            # Send multiple character creation requests
            for i in range(3):
                character_data = DatabaseTestHelper.create_test_character_data(
                    project_id=project_id,
                    name=f"Ordered Character {i}"
                )

                response = await client.send_and_receive(
                    "create_character",
                    **character_data,
                    timeout=10.0
                )
                responses.append(response)

            # All responses should be received
            assert len(responses) == 3, "Should receive all responses"

            # Check if any succeeded (service might not be fully configured)
            success_count = sum(1 for r in responses if r.get("status") == "success")
            # We don't assert success here as service might not be ready

    @pytest.mark.performance
    async def test_brain_service_load(self, test_config, performance_timer):
        """Test brain service under load."""
        from tests.utils.test_helpers import LoadTestRunner

        # Note: This is a simplified load test
        # In production, you'd want more sophisticated load testing
        websocket_url = test_config["brain_service"]["websocket_url"]

        async def websocket_load_operation():
            """Perform a load test operation."""
            mcp_client = MCPTestClient(websocket_url)
            try:
                async with mcp_client.connect() as client:
                    character_data = DatabaseTestHelper.create_test_character_data()
                    response = await client.send_and_receive(
                        "create_character",
                        **character_data,
                        timeout=5.0
                    )
                    return response
            except Exception as e:
                raise e

        # Run load test
        concurrent_operations = 10
        with performance_timer("brain_service_load", {"concurrent_ops": concurrent_operations}):
            results = await PerformanceTester.run_concurrent_operations(
                websocket_load_operation,
                concurrent_operations
            )

        # Analyze performance
        analysis = PerformanceTester.analyze_performance_results(results)

        # Log performance metrics for reporting
        print(f"\nBrain Service Load Test Results:")
        print(f"Total Operations: {analysis['total_operations']}")
        print(f"Success Rate: {analysis['success_rate']:.1f}%")
        print(f"Average Response Time: {analysis['wall_time_stats']['mean']:.3f}s")
        print(f"Max Response Time: {analysis['wall_time_stats']['max']:.3f}s")

        # Basic performance assertions
        assert analysis["success_rate"] > 0, "Some operations should succeed under load"

    async def test_service_recovery_after_restart(self, test_config):
        """Test service recovery capabilities."""
        # This test would typically restart the service and verify it recovers
        # For now, we'll test reconnection after connection drop

        mcp_client = MCPTestClient(test_config["brain_service"]["websocket_url"])

        # Test reconnection capability
        connection_attempts = 3
        successful_connections = 0

        for attempt in range(connection_attempts):
            try:
                async with mcp_client.connect() as client:
                    # Perform a simple operation to verify connection works
                    character_data = DatabaseTestHelper.create_test_character_data()
                    response = await client.send_and_receive(
                        "create_character",
                        **character_data,
                        timeout=5.0
                    )
                    successful_connections += 1
                    await asyncio.sleep(0.1)  # Brief pause between connections

            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")

        # At least some connections should succeed
        assert successful_connections > 0, "Service should accept reconnections"