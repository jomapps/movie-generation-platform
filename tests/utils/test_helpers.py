"""
Test utility functions and helpers for the movie generation platform.
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from contextlib import asynccontextmanager
import websockets
import httpx
import logging

logger = logging.getLogger(__name__)


class WebSocketTestClient:
    """WebSocket test client with helper methods."""

    def __init__(self, websocket):
        self.websocket = websocket
        self.message_id_counter = 0

    async def send_message(self, tool: str, **kwargs) -> str:
        """Send a message to the WebSocket and return message ID."""
        message_id = f"test-{self.message_id_counter}-{uuid.uuid4().hex[:8]}"
        self.message_id_counter += 1

        message = {
            "id": message_id,
            "tool": tool,
            **kwargs
        }

        await self.websocket.send(json.dumps(message))
        logger.debug(f"Sent WebSocket message: {message}")
        return message_id

    async def receive_message(self, timeout: float = 5.0) -> Dict[str, Any]:
        """Receive a message from the WebSocket."""
        try:
            response_text = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=timeout
            )
            response = json.loads(response_text)
            logger.debug(f"Received WebSocket message: {response}")
            return response
        except asyncio.TimeoutError:
            raise TimeoutError(f"No message received within {timeout} seconds")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")

    async def send_and_receive(self, tool: str, timeout: float = 5.0, **kwargs) -> Dict[str, Any]:
        """Send a message and wait for response."""
        message_id = await self.send_message(tool, **kwargs)
        response = await self.receive_message(timeout)
        return response


class MCPTestClient:
    """MCP client for testing MCP tool calls."""

    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.websocket = None

    @asynccontextmanager
    async def connect(self):
        """Connect to MCP WebSocket."""
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                self.websocket = WebSocketTestClient(websocket)
                yield self.websocket
        finally:
            self.websocket = None

    async def test_tool(self, tool_name: str, **params) -> Dict[str, Any]:
        """Test a specific MCP tool."""
        async with self.connect() as client:
            return await client.send_and_receive(tool_name, **params)


class ServiceTestHelper:
    """Helper for testing service interactions."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def health_check(self, client: httpx.AsyncClient) -> bool:
        """Check if service is healthy."""
        try:
            response = await client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {self.base_url}: {e}")
            return False

    async def get_service_info(self, client: httpx.AsyncClient) -> Dict[str, Any]:
        """Get service information."""
        response = await client.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.json()

    async def test_endpoint(self, client: httpx.AsyncClient, method: str,
                          path: str, **kwargs) -> httpx.Response:
        """Test a service endpoint."""
        url = f"{self.base_url}{path}"
        response = await client.request(method, url, **kwargs)
        return response


class PerformanceTester:
    """Performance testing utilities."""

    @staticmethod
    async def measure_operation(operation: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Measure the performance of an async operation."""
        start_time = time.time()
        start_cpu = time.process_time()

        try:
            result = await operation(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = time.time()
        end_cpu = time.process_time()

        return {
            "success": success,
            "result": result,
            "error": error,
            "wall_time": end_time - start_time,
            "cpu_time": end_cpu - start_cpu,
            "timestamp": start_time
        }

    @staticmethod
    async def run_concurrent_operations(operation: Callable, count: int,
                                      *args, **kwargs) -> List[Dict[str, Any]]:
        """Run multiple operations concurrently and measure performance."""
        tasks = []
        for i in range(count):
            task = asyncio.create_task(
                PerformanceTester.measure_operation(operation, *args, **kwargs)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "result": None,
                    "error": str(result),
                    "wall_time": 0,
                    "cpu_time": 0,
                    "timestamp": time.time()
                })
            else:
                processed_results.append(result)

        return processed_results

    @staticmethod
    def analyze_performance_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance test results."""
        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]

        if not successful_results:
            return {
                "total_operations": len(results),
                "successful_operations": 0,
                "failed_operations": len(failed_results),
                "success_rate": 0.0,
                "errors": [r["error"] for r in failed_results]
            }

        wall_times = [r["wall_time"] for r in successful_results]
        cpu_times = [r["cpu_time"] for r in successful_results]

        return {
            "total_operations": len(results),
            "successful_operations": len(successful_results),
            "failed_operations": len(failed_results),
            "success_rate": len(successful_results) / len(results) * 100,
            "wall_time_stats": {
                "mean": sum(wall_times) / len(wall_times),
                "min": min(wall_times),
                "max": max(wall_times),
                "total": sum(wall_times)
            },
            "cpu_time_stats": {
                "mean": sum(cpu_times) / len(cpu_times),
                "min": min(cpu_times),
                "max": max(cpu_times),
                "total": sum(cpu_times)
            },
            "throughput": len(successful_results) / max(wall_times) if wall_times else 0,
            "errors": [r["error"] for r in failed_results]
        }


class DatabaseTestHelper:
    """Helper for database testing operations."""

    @staticmethod
    def create_test_character_data(project_id: str = None, name: str = None) -> Dict[str, Any]:
        """Create test character data."""
        project_id = project_id or f"test-project-{uuid.uuid4().hex[:8]}"
        name = name or f"Test Character {uuid.uuid4().hex[:8]}"

        return {
            "project_id": project_id,
            "name": name,
            "personality_description": f"Personality for {name}",
            "appearance_description": f"Appearance for {name}"
        }

    @staticmethod
    def create_test_story_data(project_id: str = None, title: str = None) -> Dict[str, Any]:
        """Create test story data."""
        project_id = project_id or f"test-project-{uuid.uuid4().hex[:8]}"
        title = title or f"Test Story {uuid.uuid4().hex[:8]}"

        return {
            "project_id": project_id,
            "title": title,
            "genre": "fantasy",
            "premise": f"Test premise for {title}",
            "characters": [f"Character {i}" for i in range(1, 4)]
        }

    @staticmethod
    async def verify_embedding_generation(embedding_service, text: str) -> Dict[str, Any]:
        """Verify embedding generation works correctly."""
        try:
            embedding = await embedding_service.generate_embedding(text)

            return {
                "success": True,
                "embedding_length": len(embedding) if embedding else 0,
                "embedding_type": type(embedding).__name__,
                "non_zero_values": sum(1 for x in embedding if x != 0) if embedding else 0,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "embedding_length": 0,
                "embedding_type": None,
                "non_zero_values": 0,
                "error": str(e)
            }


class TestDataManager:
    """Manages test data lifecycle."""

    def __init__(self):
        self.created_characters = []
        self.created_stories = []
        self.created_projects = []

    def track_character(self, character_id: str, project_id: str):
        """Track a created character for cleanup."""
        self.created_characters.append({"id": character_id, "project_id": project_id})

    def track_story(self, story_id: str, project_id: str):
        """Track a created story for cleanup."""
        self.created_stories.append({"id": story_id, "project_id": project_id})

    def track_project(self, project_id: str):
        """Track a created project for cleanup."""
        self.created_projects.append(project_id)

    async def cleanup_all(self, services: Dict[str, Any]):
        """Clean up all tracked test data."""
        cleanup_errors = []

        # Cleanup characters
        for character in self.created_characters:
            try:
                # Add character cleanup logic here
                logger.debug(f"Cleaning up character {character['id']}")
            except Exception as e:
                cleanup_errors.append(f"Failed to cleanup character {character['id']}: {e}")

        # Cleanup stories
        for story in self.created_stories:
            try:
                # Add story cleanup logic here
                logger.debug(f"Cleaning up story {story['id']}")
            except Exception as e:
                cleanup_errors.append(f"Failed to cleanup story {story['id']}: {e}")

        # Cleanup projects
        for project_id in self.created_projects:
            try:
                # Add project cleanup logic here
                logger.debug(f"Cleaning up project {project_id}")
            except Exception as e:
                cleanup_errors.append(f"Failed to cleanup project {project_id}: {e}")

        if cleanup_errors:
            logger.warning(f"Cleanup errors: {cleanup_errors}")

        # Clear tracking lists
        self.created_characters.clear()
        self.created_stories.clear()
        self.created_projects.clear()


def assert_response_structure(response: Dict[str, Any], required_fields: List[str]):
    """Assert that a response has the required structure."""
    for field in required_fields:
        assert field in response, f"Missing required field: {field}"


def assert_successful_response(response: Dict[str, Any]):
    """Assert that a response indicates success."""
    assert "status" in response, "Response missing status field"
    assert response["status"] == "success", f"Expected success, got: {response.get('status')}"


def assert_error_response(response: Dict[str, Any], expected_error: str = None):
    """Assert that a response indicates an error."""
    assert "status" in response, "Response missing status field"
    assert response["status"] == "error", f"Expected error, got: {response.get('status')}"

    if expected_error:
        assert "message" in response, "Error response missing message field"
        assert expected_error in response["message"], f"Expected error '{expected_error}' not found in: {response['message']}"


async def wait_for_condition(condition: Callable, timeout: float = 10.0,
                           check_interval: float = 0.1) -> bool:
    """Wait for a condition to become true."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            if await condition() if asyncio.iscoroutinefunction(condition) else condition():
                return True
        except Exception as e:
            logger.debug(f"Condition check failed: {e}")

        await asyncio.sleep(check_interval)

    return False


class LoadTestRunner:
    """Run load tests against services."""

    def __init__(self, target_url: str, concurrent_users: int = 10):
        self.target_url = target_url
        self.concurrent_users = concurrent_users

    async def run_load_test(self, duration_seconds: int = 60) -> Dict[str, Any]:
        """Run a load test for specified duration."""
        start_time = time.time()
        end_time = start_time + duration_seconds

        results = []
        active_tasks = []

        # Start concurrent user tasks
        for user_id in range(self.concurrent_users):
            task = asyncio.create_task(
                self._simulate_user_load(user_id, end_time)
            )
            active_tasks.append(task)

        # Wait for all tasks to complete
        user_results = await asyncio.gather(*active_tasks, return_exceptions=True)

        # Combine results
        for user_result in user_results:
            if isinstance(user_result, Exception):
                logger.error(f"User task failed: {user_result}")
            else:
                results.extend(user_result)

        return PerformanceTester.analyze_performance_results(results)

    async def _simulate_user_load(self, user_id: int, end_time: float) -> List[Dict[str, Any]]:
        """Simulate load from a single user."""
        results = []
        request_count = 0

        async with httpx.AsyncClient() as client:
            while time.time() < end_time:
                request_count += 1

                # Simulate different types of requests
                result = await PerformanceTester.measure_operation(
                    self._make_request,
                    client,
                    user_id,
                    request_count
                )
                results.append(result)

                # Add some variation in request timing
                await asyncio.sleep(0.1 + (user_id * 0.01))

        return results

    async def _make_request(self, client: httpx.AsyncClient, user_id: int, request_count: int):
        """Make a test request."""
        response = await client.get(f"{self.target_url}/health")
        response.raise_for_status()
        return response.json()