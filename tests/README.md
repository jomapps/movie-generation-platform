# Movie Generation Platform - Integration Test Suite

Comprehensive integration testing framework for the movie generation platform architecture, focusing on MCP WebSocket communications, service interactions, and end-to-end workflows.

## 📋 Overview

This test suite validates:
- **Service Health & Connectivity** - All services are running and responsive
- **MCP WebSocket Communications** - Brain service WebSocket protocol functionality
- **Cross-Service Integration** - Data flow between all platform services
- **Embedding & Knowledge Graph** - AI embedding generation and similarity search
- **Performance & Scalability** - System performance under load
- **Error Handling & Recovery** - Graceful error handling and recovery mechanisms

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install test dependencies
python tests/run_integration_tests.py --install-deps

# Or manually:
pip install -r tests/requirements.txt
```

### 2. Check Service Health

```bash
# Quick health check of all services
python tests/run_integration_tests.py --suite fast
```

### 3. Generate Comprehensive Report

```bash
# Run all tests and generate detailed report
python tests/run_integration_tests.py --generate-report
```

## 🧪 Test Suites

| Suite | Description | Duration | Purpose |
|-------|-------------|----------|---------|
| `fast` | Quick health and connectivity checks | 30s | CI/CD pipeline validation |
| `health` | Service health endpoint validation | 1min | Infrastructure monitoring |
| `brain_service` | MCP WebSocket functionality | 2min | Core functionality validation |
| `cross_service` | Inter-service communication | 3min | Integration validation |
| `embedding` | AI embedding and similarity search | 5min | AI functionality validation |
| `performance` | Load testing and performance metrics | 10min | Performance validation |
| `startup` | Service initialization and configuration | 2min | Deployment validation |
| `all` | Complete test suite | 15min | Full system validation |

### Running Specific Test Suites

```bash
# Fast health checks (recommended for CI)
python tests/run_integration_tests.py --suite fast

# Brain service MCP WebSocket tests
python tests/run_integration_tests.py --suite brain_service

# Performance testing
python tests/run_integration_tests.py --suite performance

# All integration tests
python tests/run_integration_tests.py --suite all
```

## 📊 Test Reports

### Comprehensive Report Generation

The test suite includes an automated report generator that provides:

- **Executive Summary** - Overall system health and test results
- **Service Status Matrix** - Individual service health and response times
- **Performance Metrics** - Latency, throughput, and concurrency measurements
- **Critical Issues** - Immediate attention items
- **Recommendations** - Actionable improvement suggestions

```bash
# Generate detailed report
python tests/run_integration_tests.py --generate-report

# With HTML output
python tests/run_integration_tests.py --suite all --html-report report.html

# With JSON output for CI/CD
python tests/run_integration_tests.py --suite all --json-report report.json
```

### Report Output Locations

- Console output with colored status indicators
- JSON reports saved to `tests/reports/integration_test_report_YYYYMMDD_HHMMSS.json`
- HTML reports (optional) for web viewing
- Structured logs for debugging

## 🔧 Configuration

### Service Endpoints

Default test configuration (modify in `conftest.py` or test files):

```python
TEST_CONFIG = {
    "brain_service": {
        "websocket_url": "ws://localhost:8002/",
        "http_url": "http://localhost:8002"
    },
    "character_service": {
        "http_url": "http://localhost:8011"
    },
    "story_service": {
        "http_url": "http://localhost:8012"
    },
    "orchestrator": {
        "http_url": "http://localhost:8001"
    },
    "celery_redis": {
        "http_url": "http://localhost:8010"
    }
}
```

### Environment Variables

Set these environment variables to customize test behavior:

```bash
# Test timeouts
export TEST_TIMEOUT_SERVICE_STARTUP=30
export TEST_TIMEOUT_WEBSOCKET_CONNECT=10
export TEST_TIMEOUT_HTTP_REQUEST=5

# Test data
export TEST_PROJECT_PREFIX="integration-test"
export TEST_CHARACTER_COUNT=5

# Performance testing
export TEST_CONCURRENT_CONNECTIONS=10
export TEST_LOAD_DURATION=60
```

## 📁 Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and shared fixtures
├── requirements.txt               # Test dependencies
├── pytest.ini                     # Pytest settings
├── run_integration_tests.py       # Test runner script
├── generate_test_report.py        # Comprehensive report generator
├── README.md                      # This file
│
├── utils/
│   └── test_helpers.py           # Test utility functions and classes
│
├── integration/
│   ├── test_brain_service_integration.py          # Brain service WebSocket tests
│   ├── test_cross_service_data_flow.py           # Cross-service integration
│   ├── test_embedding_and_knowledge_graph.py     # AI functionality tests
│   └── test_service_startup_and_initialization.py # Service startup tests
│
├── performance/
│   └── test_mcp_websocket_performance.py         # Performance and load tests
│
└── reports/                       # Generated test reports
    └── integration_test_report_*.json
```

## 🎯 Test Categories

### Integration Tests (`@pytest.mark.integration`)

- Service-to-service communication
- Data flow validation
- API contract verification
- Cross-system workflows

### Performance Tests (`@pytest.mark.performance`)

- WebSocket connection latency
- Message throughput
- Concurrent connection handling
- Memory usage under load
- Batch processing performance

### Service-Specific Tests

- `@pytest.mark.brain_service` - Brain service MCP functionality
- `@pytest.mark.character_service` - Character management
- `@pytest.mark.story_service` - Story generation
- `@pytest.mark.orchestrator` - Task orchestration
- `@pytest.mark.celery_redis` - Background task processing

## 🔍 Key Test Scenarios

### 1. MCP WebSocket Communication
- Connection establishment and maintenance
- Message serialization/deserialization
- Tool call execution (create_character, find_similar_characters)
- Error handling and recovery
- Concurrent connection support

### 2. Embedding Pipeline
- Text-to-vector conversion
- Vector storage and retrieval
- Similarity search accuracy
- Large text handling
- Embedding consistency

### 3. Knowledge Graph Operations
- Character relationship modeling
- Cross-character similarity
- Project-based data isolation
- Query performance optimization

### 4. Cross-Service Integration
- Character creation workflow
- Task orchestration flow
- Service dependency validation
- Data consistency verification

## 🚨 Troubleshooting

### Common Issues

**Services Not Available**
```bash
# Check if services are running
docker ps
# Or check individual service logs
docker logs <service-container>
```

**WebSocket Connection Failures**
```bash
# Test WebSocket connectivity manually
wscat -c ws://localhost:8002/
```

**Test Dependencies Missing**
```bash
# Reinstall test dependencies
python tests/run_integration_tests.py --install-deps
```

**Performance Test Failures**
```bash
# Run with verbose output
python tests/run_integration_tests.py --suite performance -v
```

### Debug Mode

Run tests with detailed debugging:

```bash
# Verbose output with debugging
python -m pytest tests/integration/ -v --tb=long --log-cli-level=DEBUG

# Single test with pdb
python -m pytest tests/integration/test_brain_service_integration.py::TestBrainServiceIntegration::test_websocket_connectivity -v --pdb
```

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests
on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python tests/run_integration_tests.py --install-deps

      - name: Start services
        run: |
          docker-compose up -d
          sleep 30  # Wait for services to start

      - name: Run fast tests
        run: |
          python tests/run_integration_tests.py --suite fast

      - name: Generate comprehensive report
        if: always()
        run: |
          python tests/run_integration_tests.py --generate-report

      - name: Upload test reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: tests/reports/
```

### Docker Integration

```dockerfile
# Test runner container
FROM python:3.11-slim

WORKDIR /app
COPY tests/ ./tests/
RUN pip install -r tests/requirements.txt

CMD ["python", "tests/run_integration_tests.py", "--generate-report"]
```

## 🏆 Best Practices

### Writing Tests

1. **Use Descriptive Names** - Test names should clearly indicate what is being tested
2. **Independent Tests** - Each test should be able to run independently
3. **Proper Cleanup** - Use fixtures for setup/teardown
4. **Realistic Data** - Use representative test data
5. **Performance Awareness** - Include timing and resource usage validation

### Running Tests

1. **Start with Fast Suite** - Use `--suite fast` for quick validation
2. **Check Dependencies First** - Run `--check-deps` before test execution
3. **Use Appropriate Timeouts** - Allow sufficient time for service startup
4. **Monitor Resources** - Watch CPU/memory usage during performance tests
5. **Review Reports** - Always check generated reports for recommendations

### Debugging

1. **Verbose Output** - Use `-v` flag for detailed test output
2. **Single Test Execution** - Run individual tests for focused debugging
3. **Log Analysis** - Check service logs when tests fail
4. **Network Connectivity** - Verify service endpoints are accessible
5. **Service Dependencies** - Ensure all required services are healthy

## 📞 Support

For test framework issues or questions:

1. Check service logs: `docker logs <service-name>`
2. Verify service health: `python tests/run_integration_tests.py --suite health`
3. Generate diagnostic report: `python tests/run_integration_tests.py --generate-report`
4. Review test documentation in individual test files
5. Check GitHub issues for known problems

## 🔄 Continuous Improvement

The test suite is designed to evolve with the platform:

- **Test Coverage** - Add new tests as features are developed
- **Performance Baselines** - Update performance expectations as system optimizes
- **Error Scenarios** - Expand error handling tests based on production issues
- **Integration Patterns** - Add new cross-service test scenarios
- **Monitoring Integration** - Connect test results to monitoring systems

---

*Last Updated: 2024-09-28*