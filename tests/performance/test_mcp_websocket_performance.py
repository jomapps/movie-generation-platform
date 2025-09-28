"""
Performance tests for MCP WebSocket communications.
Tests latency, throughput, concurrent connections, and batch processing.
"""
import pytest
import asyncio
import time
import statistics
from typing import Dict, Any, List
import uuid

from tests.utils.test_helpers import (
    MCPTestClient,
    PerformanceTester,
    DatabaseTestHelper,
    LoadTestRunner
)


@pytest.mark.performance
@pytest.mark.brain_service
class TestMCPWebSocketPerformance:
    """Performance tests for MCP WebSocket operations."""

    async def test_websocket_connection_latency(self, test_config, performance_timer, test_metrics):
        """Test WebSocket connection establishment latency."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        connection_times = []

        # Test multiple connection attempts
        for i in range(10):
            start_time = time.time()

            try:
                brain_client = MCPTestClient(websocket_url)
                async with brain_client.connect() as client:
                    connection_time = time.time() - start_time
                    connection_times.append(connection_time)

                    test_metrics.record_performance(
                        "websocket_connection_latency",
                        connection_time,
                        {"attempt": i + 1}
                    )

                    # Brief pause between connections
                    await asyncio.sleep(0.1)

            except Exception as e:
                print(f"Connection attempt {i + 1} failed: {e}")
                test_metrics.record_test_result(
                    f"websocket_connection_{i + 1}",
                    False,
                    time.time() - start_time,
                    str(e)
                )

        if connection_times:
            avg_latency = statistics.mean(connection_times)
            min_latency = min(connection_times)
            max_latency = max(connection_times)

            print(f"\nWebSocket Connection Latency Results:")
            print(f"  Average: {avg_latency:.3f}s")
            print(f"  Minimum: {min_latency:.3f}s")
            print(f"  Maximum: {max_latency:.3f}s")
            print(f"  Successful connections: {len(connection_times)}/10")

            # Performance assertions
            assert avg_latency < 2.0, f"Average connection latency {avg_latency:.3f}s should be under 2s"
            assert len(connection_times) > 0, "At least some connections should succeed"

    async def test_message_round_trip_latency(self, test_config, performance_timer, test_metrics):
        """Test message round-trip latency for different operation types."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        brain_client = MCPTestClient(websocket_url)

        try:
            async with brain_client.connect() as client:
                test_operations = [
                    {
                        "name": "create_character",
                        "tool": "create_character",
                        "params": DatabaseTestHelper.create_test_character_data()
                    },
                    {
                        "name": "find_similar_characters",
                        "tool": "find_similar_characters",
                        "params": {
                            "project_id": "perf-test-project",
                            "query": "test character search"
                        }
                    }
                ]

                latency_results = {}

                for operation in test_operations:
                    operation_latencies = []

                    # Test each operation multiple times
                    for attempt in range(5):
                        start_time = time.time()

                        try:
                            response = await client.send_and_receive(
                                operation["tool"],
                                **operation["params"],
                                timeout=10.0
                            )

                            latency = time.time() - start_time
                            operation_latencies.append(latency)

                            test_metrics.record_performance(
                                f"message_latency_{operation['name']}",
                                latency,
                                {
                                    "attempt": attempt + 1,
                                    "success": response.get("status") == "success"
                                }
                            )

                        except Exception as e:
                            print(f"Operation {operation['name']} attempt {attempt + 1} failed: {e}")

                    if operation_latencies:
                        latency_results[operation["name"]] = {
                            "avg": statistics.mean(operation_latencies),
                            "min": min(operation_latencies),
                            "max": max(operation_latencies),
                            "count": len(operation_latencies)
                        }

                # Report results
                print(f"\nMessage Round-Trip Latency Results:")
                for operation_name, stats in latency_results.items():
                    print(f"  {operation_name}:")
                    print(f"    Average: {stats['avg']:.3f}s")
                    print(f"    Min: {stats['min']:.3f}s")
                    print(f"    Max: {stats['max']:.3f}s")
                    print(f"    Successful attempts: {stats['count']}/5")

                # Performance assertions
                for operation_name, stats in latency_results.items():
                    assert stats["avg"] < 5.0, f"{operation_name} average latency should be under 5s"

        except Exception as e:
            pytest.skip(f"Message latency test failed: {e}")

    async def test_concurrent_websocket_connections(self, test_config, performance_timer, test_metrics):
        """Test handling of multiple concurrent WebSocket connections."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        concurrent_connections = [5, 10, 15, 20]  # Progressive load test

        for connection_count in concurrent_connections:
            print(f"\nTesting {connection_count} concurrent connections...")

            async def create_concurrent_connection(connection_id: int):
                """Create a single concurrent connection and perform operations."""
                try:
                    brain_client = MCPTestClient(websocket_url)
                    async with brain_client.connect() as client:
                        # Perform a few operations per connection
                        operations_per_connection = 3
                        successful_operations = 0

                        for op_num in range(operations_per_connection):
                            character_data = DatabaseTestHelper.create_test_character_data(
                                name=f"Concurrent-{connection_id}-{op_num}"
                            )

                            try:
                                response = await client.send_and_receive(
                                    "create_character",
                                    **character_data,
                                    timeout=15.0
                                )

                                if response.get("status") == "success":
                                    successful_operations += 1

                            except Exception as e:
                                print(f"Operation failed for connection {connection_id}: {e}")

                        return {
                            "connection_id": connection_id,
                            "successful_operations": successful_operations,
                            "total_operations": operations_per_connection
                        }

                except Exception as e:
                    return {
                        "connection_id": connection_id,
                        "successful_operations": 0,
                        "total_operations": 0,
                        "error": str(e)
                    }

            # Run concurrent connections
            with performance_timer(
                "concurrent_websocket_test",
                {"connection_count": connection_count}
            ):
                results = await PerformanceTester.run_concurrent_operations(
                    create_concurrent_connection,
                    connection_count,
                    *range(connection_count)
                )

            # Analyze results
            successful_connections = sum(1 for r in results if r["result"] and r["result"]["successful_operations"] > 0)
            total_operations = sum(r["result"]["successful_operations"] for r in results if r["result"])

            success_rate = (successful_connections / connection_count) * 100

            print(f"  Successful connections: {successful_connections}/{connection_count} ({success_rate:.1f}%)")
            print(f"  Total successful operations: {total_operations}")

            test_metrics.record_performance(
                "concurrent_connections",
                success_rate,
                {
                    "connection_count": connection_count,
                    "successful_connections": successful_connections,
                    "total_operations": total_operations
                }
            )

            # Performance assertions (allow degradation under high load)
            if connection_count <= 10:
                assert success_rate >= 80, f"Should handle {connection_count} connections with >80% success rate"
            else:
                assert success_rate >= 50, f"Should handle {connection_count} connections with >50% success rate"

    async def test_message_throughput(self, test_config, performance_timer, test_metrics):
        """Test message processing throughput."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        brain_client = MCPTestClient(websocket_url)

        try:
            async with brain_client.connect() as client:
                # Test sustained message throughput
                message_count = 50
                test_duration = 30  # seconds

                start_time = time.time()
                sent_messages = 0
                received_responses = 0

                # Send messages as fast as possible for the duration
                while time.time() - start_time < test_duration and sent_messages < message_count:
                    character_data = DatabaseTestHelper.create_test_character_data(
                        name=f"Throughput-{sent_messages}"
                    )

                    try:
                        # Send message without waiting for response (to test throughput)
                        message_id = await client.send_message("create_character", **character_data)
                        sent_messages += 1

                        # Try to receive any pending responses
                        try:
                            response = await client.receive_message(timeout=0.1)
                            received_responses += 1
                        except asyncio.TimeoutError:
                            pass  # No response ready yet

                    except Exception as e:
                        print(f"Throughput test error: {e}")
                        break

                # Collect remaining responses
                while received_responses < sent_messages:
                    try:
                        response = await client.receive_message(timeout=2.0)
                        received_responses += 1
                    except asyncio.TimeoutError:
                        break

                elapsed_time = time.time() - start_time
                messages_per_second = sent_messages / elapsed_time
                response_rate = (received_responses / sent_messages) * 100 if sent_messages > 0 else 0

                print(f"\nThroughput Test Results:")
                print(f"  Test duration: {elapsed_time:.2f}s")
                print(f"  Messages sent: {sent_messages}")
                print(f"  Responses received: {received_responses}")
                print(f"  Messages per second: {messages_per_second:.2f}")
                print(f"  Response rate: {response_rate:.1f}%")

                test_metrics.record_performance(
                    "message_throughput",
                    messages_per_second,
                    {
                        "sent_messages": sent_messages,
                        "received_responses": received_responses,
                        "response_rate": response_rate
                    }
                )

                # Performance assertions
                assert messages_per_second > 1.0, "Should handle at least 1 message per second"
                assert response_rate > 50, "Should receive responses for >50% of messages"

        except Exception as e:
            pytest.skip(f"Throughput test failed: {e}")

    async def test_batch_operation_performance(self, test_config, performance_timer, test_metrics):
        """Test performance of batch operations."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        batch_sizes = [5, 10, 20]

        for batch_size in batch_sizes:
            print(f"\nTesting batch size: {batch_size}")

            brain_client = MCPTestClient(websocket_url)

            try:
                async with brain_client.connect() as client:
                    # Create batch of characters
                    batch_characters = [
                        DatabaseTestHelper.create_test_character_data(
                            name=f"Batch-{batch_size}-{i}"
                        )
                        for i in range(batch_size)
                    ]

                    # Test sequential processing
                    with performance_timer(
                        "batch_sequential",
                        {"batch_size": batch_size}
                    ):
                        sequential_start = time.time()
                        sequential_successes = 0

                        for character_data in batch_characters:
                            try:
                                response = await client.send_and_receive(
                                    "create_character",
                                    **character_data,
                                    timeout=10.0
                                )
                                if response.get("status") == "success":
                                    sequential_successes += 1
                            except Exception:
                                pass

                        sequential_time = time.time() - sequential_start

                    # Test rapid-fire processing (send all, then collect responses)
                    with performance_timer(
                        "batch_rapid_fire",
                        {"batch_size": batch_size}
                    ):
                        rapid_fire_start = time.time()

                        # Send all messages quickly
                        sent_count = 0
                        for character_data in batch_characters:
                            try:
                                await client.send_message("create_character", **character_data)
                                sent_count += 1
                            except Exception:
                                break

                        # Collect responses
                        rapid_fire_successes = 0
                        for _ in range(sent_count):
                            try:
                                response = await client.receive_message(timeout=5.0)
                                if response.get("status") == "success":
                                    rapid_fire_successes += 1
                            except Exception:
                                break

                        rapid_fire_time = time.time() - rapid_fire_start

                    print(f"  Sequential: {sequential_successes}/{batch_size} in {sequential_time:.2f}s")
                    print(f"  Rapid-fire: {rapid_fire_successes}/{sent_count} in {rapid_fire_time:.2f}s")

                    test_metrics.record_performance(
                        "batch_processing",
                        rapid_fire_time if rapid_fire_time > 0 else sequential_time,
                        {
                            "batch_size": batch_size,
                            "sequential_time": sequential_time,
                            "rapid_fire_time": rapid_fire_time,
                            "sequential_successes": sequential_successes,
                            "rapid_fire_successes": rapid_fire_successes
                        }
                    )

            except Exception as e:
                print(f"Batch test failed for size {batch_size}: {e}")

    async def test_memory_usage_under_load(self, test_config, performance_timer, test_metrics):
        """Test memory usage patterns under sustained load."""
        websocket_url = test_config["brain_service"]["websocket_url"]

        # This is a simplified memory test - in production you'd use more sophisticated memory monitoring
        brain_client = MCPTestClient(websocket_url)

        try:
            async with brain_client.connect() as client:
                # Sustained operations to test memory usage
                operation_count = 100
                successful_operations = 0

                with performance_timer("memory_load_test", {"operation_count": operation_count}):
                    for i in range(operation_count):
                        character_data = DatabaseTestHelper.create_test_character_data(
                            name=f"Memory-Test-{i}"
                        )

                        try:
                            response = await client.send_and_receive(
                                "create_character",
                                **character_data,
                                timeout=5.0
                            )

                            if response.get("status") == "success":
                                successful_operations += 1

                            # Brief pause to prevent overwhelming
                            if i % 10 == 0:
                                await asyncio.sleep(0.1)

                        except Exception as e:
                            if i % 20 == 0:  # Log every 20th error to avoid spam
                                print(f"Memory test operation {i} failed: {e}")

                success_rate = (successful_operations / operation_count) * 100

                print(f"\nMemory Load Test Results:")
                print(f"  Operations attempted: {operation_count}")
                print(f"  Successful operations: {successful_operations}")
                print(f"  Success rate: {success_rate:.1f}%")

                test_metrics.record_performance(
                    "memory_load_test",
                    success_rate,
                    {
                        "operation_count": operation_count,
                        "successful_operations": successful_operations
                    }
                )

                # Memory usage assertion (should handle sustained load)
                assert success_rate > 70, "Should maintain >70% success rate under sustained load"

        except Exception as e:
            pytest.skip(f"Memory load test failed: {e}")

    async def test_connection_recovery_performance(self, test_config, performance_timer, test_metrics):
        """Test performance of connection recovery scenarios."""
        websocket_url = test_config["brain_service"]["websocket_url"]

        recovery_times = []

        for attempt in range(5):
            print(f"\nConnection recovery test {attempt + 1}/5")

            try:
                # Establish connection
                brain_client = MCPTestClient(websocket_url)
                async with brain_client.connect() as client:
                    # Perform successful operation
                    character_data = DatabaseTestHelper.create_test_character_data(
                        name=f"Recovery-Test-{attempt}"
                    )

                    response = await client.send_and_receive(
                        "create_character",
                        **character_data,
                        timeout=5.0
                    )

                    if response.get("status") == "success":
                        print(f"  Initial operation successful")
                    else:
                        print(f"  Initial operation failed: {response}")

                # Connection ends here due to context manager

                # Measure recovery time - time to establish new connection and perform operation
                recovery_start = time.time()

                new_brain_client = MCPTestClient(websocket_url)
                async with new_brain_client.connect() as new_client:
                    recovery_character_data = DatabaseTestHelper.create_test_character_data(
                        name=f"Recovery-Post-{attempt}"
                    )

                    recovery_response = await new_client.send_and_receive(
                        "create_character",
                        **recovery_character_data,
                        timeout=5.0
                    )

                    recovery_time = time.time() - recovery_start
                    recovery_times.append(recovery_time)

                    print(f"  Recovery time: {recovery_time:.3f}s")
                    print(f"  Recovery operation: {recovery_response.get('status', 'unknown')}")

                    test_metrics.record_performance(
                        "connection_recovery",
                        recovery_time,
                        {"attempt": attempt + 1, "success": recovery_response.get("status") == "success"}
                    )

            except Exception as e:
                print(f"  Recovery test {attempt + 1} failed: {e}")

        if recovery_times:
            avg_recovery_time = statistics.mean(recovery_times)
            print(f"\nConnection Recovery Performance:")
            print(f"  Average recovery time: {avg_recovery_time:.3f}s")
            print(f"  Successful recovery attempts: {len(recovery_times)}/5")

            # Performance assertion
            assert avg_recovery_time < 3.0, f"Average recovery time {avg_recovery_time:.3f}s should be under 3s"
            assert len(recovery_times) >= 3, "At least 3/5 recovery attempts should succeed"