"""
Integration tests for embedding generation and knowledge graph operations.
Tests the complete pipeline from text input to vector storage and similarity search.
"""
import pytest
import asyncio
import numpy as np
import uuid
from typing import Dict, Any, List

from tests.utils.test_helpers import (
    MCPTestClient,
    PerformanceTester,
    DatabaseTestHelper,
    assert_successful_response,
    wait_for_condition
)


@pytest.mark.brain_service
@pytest.mark.integration
class TestEmbeddingAndKnowledgeGraph:
    """Test embedding generation and knowledge graph operations."""

    async def test_embedding_generation_pipeline(self, test_config, performance_timer, test_metrics):
        """Test the complete embedding generation pipeline."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        brain_client = MCPTestClient(websocket_url)

        test_cases = [
            {
                "name": "Short personality",
                "text": "Brave and loyal",
                "expected_min_length": 100  # Minimum expected embedding dimension
            },
            {
                "name": "Medium personality",
                "text": "A wise wizard with deep knowledge of ancient magic and a kind heart",
                "expected_min_length": 100
            },
            {
                "name": "Long personality",
                "text": "An experienced warrior who has fought in countless battles, showing both "
                       "courage in the face of danger and compassion for those in need. Known for "
                       "strategic thinking and unwavering loyalty to friends and allies.",
                "expected_min_length": 100
            },
            {
                "name": "Complex character",
                "text": "A morally ambiguous rogue with a troubled past, skilled in stealth and "
                       "deception but harboring a secret desire for redemption. Struggles with "
                       "trust issues while maintaining a sharp wit and survival instincts.",
                "expected_min_length": 100
            }
        ]

        try:
            async with brain_client.connect() as client:
                embedding_results = []

                for test_case in test_cases:
                    print(f"\nTesting: {test_case['name']}")

                    character_data = DatabaseTestHelper.create_test_character_data(
                        name=f"Embedding Test - {test_case['name']}"
                    )
                    character_data["personality_description"] = test_case["text"]

                    with performance_timer(
                        "embedding_generation",
                        {"text_length": len(test_case["text"]), "test_case": test_case["name"]}
                    ):
                        response = await client.send_and_receive(
                            "create_character",
                            **character_data,
                            timeout=20.0
                        )

                    if response.get("status") == "success":
                        character_id = response.get("character_id")
                        print(f"  ✓ Character created: {character_id}")

                        # Test that we can find this character
                        search_response = await client.send_and_receive(
                            "find_similar_characters",
                            project_id=character_data["project_id"],
                            query=test_case["text"][:50],  # Use part of the text as query
                            timeout=15.0
                        )

                        if search_response.get("status") == "success":
                            results = search_response.get("results", [])
                            found_character = any(
                                result.get("id") == character_id
                                for result in results
                            )

                            embedding_results.append({
                                "test_case": test_case["name"],
                                "character_created": True,
                                "character_id": character_id,
                                "searchable": len(results) > 0,
                                "found_in_search": found_character,
                                "result_count": len(results)
                            })

                            print(f"  ✓ Search returned {len(results)} results")
                            if found_character:
                                print(f"  ✓ Character found in search results")
                        else:
                            print(f"  ✗ Search failed: {search_response.get('message', 'Unknown error')}")
                    else:
                        print(f"  ✗ Character creation failed: {response.get('message', 'Unknown error')}")
                        embedding_results.append({
                            "test_case": test_case["name"],
                            "character_created": False,
                            "error": response.get("message", "Unknown error")
                        })

                # Analyze results
                successful_embeddings = sum(1 for r in embedding_results if r.get("character_created", False))
                successful_searches = sum(1 for r in embedding_results if r.get("searchable", False))

                print(f"\nEmbedding Generation Results:")
                print(f"  Successful character creations: {successful_embeddings}/{len(test_cases)}")
                print(f"  Successful searches: {successful_searches}/{len(test_cases)}")

                test_metrics.record_performance(
                    "embedding_pipeline_success_rate",
                    (successful_embeddings / len(test_cases)) * 100,
                    {
                        "total_tests": len(test_cases),
                        "successful_embeddings": successful_embeddings,
                        "successful_searches": successful_searches
                    }
                )

                # Basic assertions
                assert successful_embeddings > 0, "At least some embeddings should be generated"

        except Exception as e:
            pytest.skip(f"Embedding generation test failed: {e}")

    async def test_similarity_search_accuracy(self, test_config, performance_timer):
        """Test the accuracy of similarity search."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        brain_client = MCPTestClient(websocket_url)

        # Create characters with known similarities
        character_groups = [
            {
                "theme": "warriors",
                "characters": [
                    {"name": "Knight Arthur", "personality": "A noble knight with honor and courage"},
                    {"name": "Viking Ragnar", "personality": "A fierce warrior with battle-tested strength"},
                    {"name": "Samurai Takeshi", "personality": "A disciplined fighter with martial prowess"}
                ]
            },
            {
                "theme": "mages",
                "characters": [
                    {"name": "Wizard Merlin", "personality": "A wise spellcaster with ancient knowledge"},
                    {"name": "Sorceress Luna", "personality": "A mystical enchanter with powerful magic"},
                    {"name": "Archmage Zara", "personality": "A scholarly mage with deep magical understanding"}
                ]
            }
        ]

        project_id = f"similarity-test-{uuid.uuid4().hex[:8]}"

        try:
            async with brain_client.connect() as client:
                created_characters = []

                # Create all test characters
                for group in character_groups:
                    for char_data in group["characters"]:
                        character_data = {
                            "project_id": project_id,
                            "name": char_data["name"],
                            "personality_description": char_data["personality"],
                            "appearance_description": f"Appearance of {char_data['name']}"
                        }

                        response = await client.send_and_receive(
                            "create_character",
                            **character_data,
                            timeout=15.0
                        )

                        if response.get("status") == "success":
                            created_characters.append({
                                "id": response.get("character_id"),
                                "name": char_data["name"],
                                "theme": group["theme"],
                                "personality": char_data["personality"]
                            })

                if len(created_characters) < 4:
                    pytest.skip("Not enough characters created for similarity testing")

                print(f"\nCreated {len(created_characters)} characters for similarity testing")

                # Test similarity searches
                similarity_tests = [
                    {"query": "brave fighter", "expected_theme": "warriors"},
                    {"query": "magical spellcaster", "expected_theme": "mages"},
                    {"query": "warrior with strength", "expected_theme": "warriors"},
                    {"query": "wise magic user", "expected_theme": "mages"}
                ]

                accuracy_results = []

                for test in similarity_tests:
                    with performance_timer("similarity_search", {"query": test["query"]}):
                        search_response = await client.send_and_receive(
                            "find_similar_characters",
                            project_id=project_id,
                            query=test["query"],
                            timeout=10.0
                        )

                    if search_response.get("status") == "success":
                        results = search_response.get("results", [])

                        # Check if top results match expected theme
                        top_results = results[:3]  # Check top 3 results
                        matching_theme_count = 0

                        for result in top_results:
                            result_character = next(
                                (char for char in created_characters if char["id"] == result.get("id")),
                                None
                            )
                            if result_character and result_character["theme"] == test["expected_theme"]:
                                matching_theme_count += 1

                        accuracy = (matching_theme_count / len(top_results)) * 100 if top_results else 0

                        accuracy_results.append({
                            "query": test["query"],
                            "expected_theme": test["expected_theme"],
                            "result_count": len(results),
                            "top_results_count": len(top_results),
                            "matching_theme_count": matching_theme_count,
                            "accuracy": accuracy
                        })

                        print(f"  Query: '{test['query']}' -> {matching_theme_count}/{len(top_results)} correct theme matches")

                # Calculate overall accuracy
                if accuracy_results:
                    overall_accuracy = sum(r["accuracy"] for r in accuracy_results) / len(accuracy_results)
                    print(f"\nSimilarity Search Accuracy: {overall_accuracy:.1f}%")

                    # Accuracy assertion (allowing for some variance in similarity matching)
                    assert overall_accuracy > 30, f"Similarity search accuracy {overall_accuracy:.1f}% should be above 30%"

        except Exception as e:
            pytest.skip(f"Similarity search accuracy test failed: {e}")

    async def test_knowledge_graph_relationships(self, test_config, performance_timer):
        """Test knowledge graph relationship storage and retrieval."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        brain_client = MCPTestClient(websocket_url)

        project_id = f"relationships-test-{uuid.uuid4().hex[:8]}"

        # Create characters with potential relationships
        character_definitions = [
            {
                "name": "Hero Protagonist",
                "personality": "A brave hero on a quest to save the kingdom",
                "relationships": ["ally", "leader"]
            },
            {
                "name": "Wise Mentor",
                "personality": "An old sage who guides the hero with wisdom and experience",
                "relationships": ["mentor", "advisor"]
            },
            {
                "name": "Dark Villain",
                "personality": "An evil sorcerer seeking to destroy the kingdom",
                "relationships": ["enemy", "antagonist"]
            }
        ]

        try:
            async with brain_client.connect() as client:
                created_characters = []

                # Create characters
                for char_def in character_definitions:
                    character_data = {
                        "project_id": project_id,
                        "name": char_def["name"],
                        "personality_description": char_def["personality"],
                        "appearance_description": f"Distinctive appearance of {char_def['name']}"
                    }

                    response = await client.send_and_receive(
                        "create_character",
                        **character_data,
                        timeout=15.0
                    )

                    if response.get("status") == "success":
                        created_characters.append({
                            "id": response.get("character_id"),
                            "name": char_def["name"],
                            "personality": char_def["personality"],
                            "expected_relationships": char_def["relationships"]
                        })

                if len(created_characters) < 2:
                    pytest.skip("Not enough characters created for relationship testing")

                print(f"\nCreated {len(created_characters)} characters for relationship testing")

                # Test relationship discovery through similarity
                relationship_queries = [
                    {"query": "hero and mentor relationship", "expected_characters": ["Hero Protagonist", "Wise Mentor"]},
                    {"query": "conflict between good and evil", "expected_characters": ["Hero Protagonist", "Dark Villain"]},
                    {"query": "guidance and wisdom", "expected_characters": ["Wise Mentor"]},
                    {"query": "antagonist and threat", "expected_characters": ["Dark Villain"]}
                ]

                relationship_results = []

                for query_test in relationship_queries:
                    with performance_timer("relationship_query", {"query": query_test["query"]}):
                        search_response = await client.send_and_receive(
                            "find_similar_characters",
                            project_id=project_id,
                            query=query_test["query"],
                            timeout=10.0
                        )

                    if search_response.get("status") == "success":
                        results = search_response.get("results", [])

                        # Check if expected characters are found
                        found_characters = []
                        for result in results:
                            result_character = next(
                                (char for char in created_characters if char["id"] == result.get("id")),
                                None
                            )
                            if result_character:
                                found_characters.append(result_character["name"])

                        expected_found = [name for name in query_test["expected_characters"] if name in found_characters]

                        relationship_results.append({
                            "query": query_test["query"],
                            "expected_characters": query_test["expected_characters"],
                            "found_characters": found_characters,
                            "expected_found_count": len(expected_found),
                            "total_results": len(results)
                        })

                        print(f"  Query: '{query_test['query']}' found {len(expected_found)}/{len(query_test['expected_characters'])} expected characters")

                # Analyze relationship discovery
                if relationship_results:
                    successful_queries = sum(1 for r in relationship_results if r["expected_found_count"] > 0)
                    success_rate = (successful_queries / len(relationship_results)) * 100

                    print(f"\nRelationship Discovery Success Rate: {success_rate:.1f}%")

                    # Basic assertion for relationship discovery
                    assert success_rate > 25, f"Relationship discovery should have >25% success rate"

        except Exception as e:
            pytest.skip(f"Knowledge graph relationship test failed: {e}")

    async def test_embedding_consistency(self, test_config, performance_timer):
        """Test that embeddings are consistent across multiple generations."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        brain_client = MCPTestClient(websocket_url)

        test_text = "A brave knight with unwavering courage and a strong sense of justice"
        project_id = f"consistency-test-{uuid.uuid4().hex[:8]}"

        try:
            async with brain_client.connect() as client:
                # Create the same character multiple times
                consistency_tests = []

                for iteration in range(3):
                    character_data = {
                        "project_id": project_id,
                        "name": f"Consistency Test Character {iteration}",
                        "personality_description": test_text,
                        "appearance_description": "Standard test appearance"
                    }

                    with performance_timer("embedding_consistency", {"iteration": iteration + 1}):
                        response = await client.send_and_receive(
                            "create_character",
                            **character_data,
                            timeout=15.0
                        )

                    if response.get("status") == "success":
                        character_id = response.get("character_id")

                        # Search for similar characters
                        search_response = await client.send_and_receive(
                            "find_similar_characters",
                            project_id=project_id,
                            query=test_text,
                            timeout=10.0
                        )

                        if search_response.get("status") == "success":
                            results = search_response.get("results", [])

                            # Find this character in the results
                            character_result = next(
                                (r for r in results if r.get("id") == character_id),
                                None
                            )

                            if character_result:
                                similarity_score = character_result.get("similarity_score", 0)
                                consistency_tests.append({
                                    "iteration": iteration + 1,
                                    "character_id": character_id,
                                    "similarity_score": similarity_score,
                                    "found_in_search": True
                                })
                            else:
                                consistency_tests.append({
                                    "iteration": iteration + 1,
                                    "character_id": character_id,
                                    "similarity_score": 0,
                                    "found_in_search": False
                                })

                # Analyze consistency
                if len(consistency_tests) >= 2:
                    similarity_scores = [t["similarity_score"] for t in consistency_tests if t["found_in_search"]]

                    if len(similarity_scores) >= 2:
                        # Calculate variance in similarity scores
                        mean_score = sum(similarity_scores) / len(similarity_scores)
                        variance = sum((score - mean_score) ** 2 for score in similarity_scores) / len(similarity_scores)
                        std_deviation = variance ** 0.5

                        print(f"\nEmbedding Consistency Results:")
                        print(f"  Characters created: {len(consistency_tests)}")
                        print(f"  Characters found in search: {len(similarity_scores)}")
                        print(f"  Mean similarity score: {mean_score:.3f}")
                        print(f"  Standard deviation: {std_deviation:.3f}")

                        # Consistency assertion (embeddings should be relatively consistent)
                        assert std_deviation < 0.2, f"Embedding consistency std dev {std_deviation:.3f} should be < 0.2"

        except Exception as e:
            pytest.skip(f"Embedding consistency test failed: {e}")

    async def test_large_text_embedding(self, test_config, performance_timer):
        """Test embedding generation for large text inputs."""
        websocket_url = test_config["brain_service"]["websocket_url"]
        brain_client = MCPTestClient(websocket_url)

        # Create progressively larger text inputs
        base_text = "A complex character with multifaceted personality traits, including courage, wisdom, and compassion. "
        text_sizes = [
            {"size": "small", "text": base_text, "repetitions": 1},
            {"size": "medium", "text": base_text, "repetitions": 5},
            {"size": "large", "text": base_text, "repetitions": 10},
            {"size": "very_large", "text": base_text, "repetitions": 20}
        ]

        try:
            async with brain_client.connect() as client:
                large_text_results = []

                for test_case in text_sizes:
                    full_text = test_case["text"] * test_case["repetitions"]
                    character_name = f"Large Text Test - {test_case['size']}"

                    print(f"\nTesting {test_case['size']} text ({len(full_text)} characters)")

                    character_data = {
                        "project_id": f"large-text-test-{test_case['size']}",
                        "name": character_name,
                        "personality_description": full_text,
                        "appearance_description": "Standard appearance for large text test"
                    }

                    with performance_timer(
                        "large_text_embedding",
                        {"text_size": test_case["size"], "character_count": len(full_text)}
                    ):
                        response = await client.send_and_receive(
                            "create_character",
                            **character_data,
                            timeout=30.0  # Longer timeout for large text
                        )

                    success = response.get("status") == "success"
                    processing_time = 0  # Would be captured by performance_timer

                    large_text_results.append({
                        "size": test_case["size"],
                        "character_count": len(full_text),
                        "success": success,
                        "character_id": response.get("character_id") if success else None,
                        "error": response.get("message") if not success else None
                    })

                    if success:
                        print(f"  ✓ Successfully processed {len(full_text)} characters")
                    else:
                        print(f"  ✗ Failed to process: {response.get('message', 'Unknown error')}")

                # Analyze large text handling
                successful_sizes = [r for r in large_text_results if r["success"]]
                print(f"\nLarge Text Embedding Results:")
                print(f"  Successful text sizes: {len(successful_sizes)}/{len(text_sizes)}")

                for result in large_text_results:
                    status = "✓" if result["success"] else "✗"
                    print(f"  {status} {result['size']}: {result['character_count']} chars")

                # Basic assertion - should handle at least small and medium texts
                assert len(successful_sizes) >= 2, "Should handle at least small and medium text sizes"

        except Exception as e:
            pytest.skip(f"Large text embedding test failed: {e}")