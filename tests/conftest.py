"""
Pytest configuration and shared fixtures for movie generation platform tests.
"""
import asyncio
import os
import pytest
import logging
import time
from typing import Dict, Any, AsyncGenerator, Generator
from contextlib import asynccontextmanager
import websockets
import httpx
import docker
from unittest.mock import AsyncMock, MagicMock

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_CONFIG = {
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

# Test timeouts
TIMEOUTS = {
    "service_startup": 30,
    "websocket_connect": 10,
    "http_request": 5,
    "database_operation": 10,
    "embedding_generation": 15
}


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return TEST_CONFIG


@pytest.fixture(scope="session")
def timeouts():
    """Test timeout configuration."""
    return TIMEOUTS


@pytest.fixture
async def http_client():
    """HTTP client for making requests to services."""
    async with httpx.AsyncClient(timeout=TIMEOUTS["http_request"]) as client:
        yield client


@pytest.fixture
async def brain_service_websocket(test_config):
    """WebSocket connection to brain service."""
    uri = test_config["brain_service"]["websocket_url"]
    try:
        async with websockets.connect(
            uri,
            timeout=TIMEOUTS["websocket_connect"],
            ping_interval=None,
            ping_timeout=None
        ) as websocket:
            logger.info(f"Connected to brain service WebSocket: {uri}")
            yield websocket
    except Exception as e:
        logger.error(f"Failed to connect to brain service WebSocket {uri}: {e}")
        pytest.skip(f"Brain service WebSocket not available: {e}")


@pytest.fixture
def mock_neo4j_connection():
    """Mock Neo4j connection for testing."""
    mock_connection = AsyncMock()
    mock_connection.execute_query = AsyncMock()
    mock_connection.close = AsyncMock()
    return mock_connection


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service for testing."""
    mock_service = MagicMock()
    mock_service.generate_embedding = AsyncMock(return_value=[0.1] * 768)
    mock_service.calculate_similarity = MagicMock(return_value=0.85)
    return mock_service


@pytest.fixture
def sample_character_data():
    """Sample character data for testing."""
    return {
        "project_id": "test-project-001",
        "name": "Test Character",
        "personality_description": "A brave and loyal warrior with a strong sense of justice.",
        "appearance_description": "Tall, muscular build with dark hair and piercing blue eyes."
    }


@pytest.fixture
def sample_story_data():
    """Sample story data for testing."""
    return {
        "project_id": "test-project-001",
        "title": "Test Story",
        "genre": "fantasy",
        "premise": "A hero's journey to save the kingdom from darkness.",
        "characters": ["Test Character"]
    }


@pytest.fixture(scope="session")
async def docker_client():
    """Docker client for managing test containers."""
    try:
        client = docker.from_env()
        yield client
        client.close()
    except Exception as e:
        logger.warning(f"Docker not available: {e}")
        yield None


class ServiceHealthChecker:
    """Helper class for checking service health."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def wait_for_service(self, service_name: str, timeout: int = 30) -> bool:
        """Wait for a service to become healthy."""
        if service_name not in self.config:
            logger.error(f"Unknown service: {service_name}")
            return False

        service_config = self.config[service_name]
        health_url = f"{service_config['http_url']}/health"

        start_time = time.time()
        async with httpx.AsyncClient() as client:
            while time.time() - start_time < timeout:
                try:
                    response = await client.get(health_url, timeout=2)
                    if response.status_code == 200:
                        logger.info(f"{service_name} is healthy")
                        return True
                except Exception as e:
                    logger.debug(f"Health check failed for {service_name}: {e}")

                await asyncio.sleep(1)

        logger.error(f"{service_name} failed to become healthy within {timeout}s")
        return False

    async def check_all_services(self) -> Dict[str, bool]:
        """Check health of all configured services."""
        results = {}
        tasks = []

        for service_name in self.config.keys():
            task = asyncio.create_task(
                self.wait_for_service(service_name, TIMEOUTS["service_startup"])
            )
            tasks.append((service_name, task))

        for service_name, task in tasks:
            try:
                results[service_name] = await task
            except Exception as e:
                logger.error(f"Error checking {service_name}: {e}")
                results[service_name] = False

        return results


@pytest.fixture(scope="session")
async def service_health_checker(test_config):
    """Service health checker fixture."""
    return ServiceHealthChecker(test_config)


@pytest.fixture(scope="session")
async def services_ready(service_health_checker):
    """Ensure all services are ready before running tests."""
    logger.info("Checking service readiness...")
    results = await service_health_checker.check_all_services()

    # Log results
    for service, is_ready in results.items():
        status = "READY" if is_ready else "NOT READY"
        logger.info(f"{service}: {status}")

    return results


class TestMetrics:
    """Test metrics collector."""

    def __init__(self):
        self.metrics = {
            "start_time": time.time(),
            "test_results": [],
            "performance_data": {},
            "error_count": 0,
            "total_tests": 0
        }

    def record_test_result(self, test_name: str, passed: bool, duration: float, error: str = None):
        """Record test result."""
        self.metrics["test_results"].append({
            "name": test_name,
            "passed": passed,
            "duration": duration,
            "error": error,
            "timestamp": time.time()
        })
        self.metrics["total_tests"] += 1
        if not passed:
            self.metrics["error_count"] += 1

    def record_performance(self, operation: str, duration: float, metadata: Dict = None):
        """Record performance metric."""
        if operation not in self.metrics["performance_data"]:
            self.metrics["performance_data"][operation] = []

        self.metrics["performance_data"][operation].append({
            "duration": duration,
            "metadata": metadata or {},
            "timestamp": time.time()
        })

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary."""
        total_duration = time.time() - self.metrics["start_time"]
        passed_tests = sum(1 for result in self.metrics["test_results"] if result["passed"])

        return {
            "total_duration": total_duration,
            "total_tests": self.metrics["total_tests"],
            "passed_tests": passed_tests,
            "failed_tests": self.metrics["error_count"],
            "success_rate": (passed_tests / self.metrics["total_tests"]) * 100 if self.metrics["total_tests"] > 0 else 0,
            "performance_summary": self._get_performance_summary()
        }

    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        summary = {}
        for operation, measurements in self.metrics["performance_data"].items():
            durations = [m["duration"] for m in measurements]
            if durations:
                summary[operation] = {
                    "count": len(durations),
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations)
                }
        return summary


@pytest.fixture(scope="session")
def test_metrics():
    """Test metrics collector fixture."""
    return TestMetrics()


# Performance test helpers
class PerformanceTimer:
    """Context manager for timing operations."""

    def __init__(self, test_metrics: TestMetrics, operation: str, metadata: Dict = None):
        self.test_metrics = test_metrics
        self.operation = operation
        self.metadata = metadata or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.test_metrics.record_performance(self.operation, duration, self.metadata)


@pytest.fixture
def performance_timer(test_metrics):
    """Performance timer fixture."""
    def _timer(operation: str, metadata: Dict = None):
        return PerformanceTimer(test_metrics, operation, metadata)
    return _timer


# Test data generators
def generate_test_characters(count: int = 5) -> list:
    """Generate test character data."""
    characters = []
    for i in range(count):
        characters.append({
            "project_id": f"test-project-{i:03d}",
            "name": f"Character {i+1}",
            "personality_description": f"Personality description for character {i+1}",
            "appearance_description": f"Appearance description for character {i+1}"
        })
    return characters


def generate_test_stories(count: int = 3) -> list:
    """Generate test story data."""
    stories = []
    for i in range(count):
        stories.append({
            "project_id": f"test-project-{i:03d}",
            "title": f"Test Story {i+1}",
            "genre": ["fantasy", "sci-fi", "drama"][i % 3],
            "premise": f"Premise for test story {i+1}",
            "characters": [f"Character {j+1}" for j in range(i+1, i+3)]
        })
    return stories


@pytest.fixture
def test_data_generator():
    """Test data generator fixture."""
    return {
        "characters": generate_test_characters,
        "stories": generate_test_stories
    }


# Cleanup helpers
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """Cleanup test data after each test."""
    yield
    # Cleanup logic would go here
    # For now, we'll just log
    logger.debug("Test cleanup completed")


# Skip markers for optional services
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "brain_service: tests that require brain service"
    )
    config.addinivalue_line(
        "markers", "character_service: tests that require character service"
    )
    config.addinivalue_line(
        "markers", "story_service: tests that require story service"
    )
    config.addinivalue_line(
        "markers", "orchestrator: tests that require orchestrator service"
    )
    config.addinivalue_line(
        "markers", "performance: performance tests"
    )
    config.addinivalue_line(
        "markers", "integration: integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: end-to-end tests"
    )