#!/usr/bin/env python3
"""
Integration test runner for the movie generation platform.
Runs specific test suites and generates reports.
"""
import argparse
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Test suites configuration
TEST_SUITES = {
    "health": [
        "tests/integration/test_service_startup_and_initialization.py::TestServiceStartupAndInitialization::test_all_services_health_endpoints"
    ],
    "brain_service": [
        "tests/integration/test_brain_service_integration.py"
    ],
    "cross_service": [
        "tests/integration/test_cross_service_data_flow.py"
    ],
    "embedding": [
        "tests/integration/test_embedding_and_knowledge_graph.py"
    ],
    "performance": [
        "tests/performance/test_mcp_websocket_performance.py"
    ],
    "startup": [
        "tests/integration/test_service_startup_and_initialization.py"
    ],
    "all": [
        "tests/integration/",
        "tests/performance/"
    ],
    "fast": [
        "tests/integration/test_service_startup_and_initialization.py::TestServiceStartupAndInitialization::test_all_services_health_endpoints",
        "tests/integration/test_brain_service_integration.py::TestBrainServiceIntegration::test_brain_service_health",
        "tests/integration/test_brain_service_integration.py::TestBrainServiceIntegration::test_websocket_connectivity"
    ]
}


class TestRunner:
    """Integration test runner with reporting capabilities."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_dir = Path(__file__).parent
        self.project_dir = self.test_dir.parent

    def run_pytest(self, test_paths: List[str], additional_args: List[str] = None) -> int:
        """Run pytest with specified test paths."""
        cmd = ["python", "-m", "pytest"]

        # Add test paths
        cmd.extend(test_paths)

        # Add common arguments
        common_args = [
            "--tb=short",
            "-v" if self.verbose else "-q",
            "--color=yes"
        ]
        cmd.extend(common_args)

        # Add additional arguments
        if additional_args:
            cmd.extend(additional_args)

        print(f"Running: {' '.join(cmd)}")
        print("=" * 60)

        # Change to test directory
        result = subprocess.run(cmd, cwd=self.test_dir)
        return result.returncode

    def run_suite(self, suite_name: str, additional_args: List[str] = None) -> int:
        """Run a specific test suite."""
        if suite_name not in TEST_SUITES:
            print(f"Error: Unknown test suite '{suite_name}'")
            print(f"Available suites: {', '.join(TEST_SUITES.keys())}")
            return 1

        test_paths = TEST_SUITES[suite_name]
        print(f"Running test suite: {suite_name}")
        print(f"Test paths: {test_paths}")

        return self.run_pytest(test_paths, additional_args)

    def list_suites(self):
        """List available test suites."""
        print("Available test suites:")
        print("=" * 40)
        for suite_name, paths in TEST_SUITES.items():
            print(f"  {suite_name:15} - {len(paths)} test path(s)")
            if self.verbose:
                for path in paths:
                    print(f"    • {path}")
        print()

    def check_dependencies(self) -> bool:
        """Check if test dependencies are installed."""
        try:
            import pytest
            import httpx
            import websockets
            print("✓ Core test dependencies are available")
            return True
        except ImportError as e:
            print(f"✗ Missing test dependencies: {e}")
            print("Run: pip install -r tests/requirements.txt")
            return False

    def install_dependencies(self) -> int:
        """Install test dependencies."""
        requirements_file = self.test_dir / "requirements.txt"
        if not requirements_file.exists():
            print(f"Error: Requirements file not found: {requirements_file}")
            return 1

        print("Installing test dependencies...")
        cmd = ["pip", "install", "-r", str(requirements_file)]
        result = subprocess.run(cmd)
        return result.returncode

    async def generate_report(self) -> int:
        """Generate comprehensive test report."""
        print("Generating comprehensive test report...")
        print("=" * 50)

        try:
            # Import and run the report generator
            sys.path.append(str(self.test_dir))
            from generate_test_report import TestReportGenerator

            generator = TestReportGenerator()
            report = await generator.run_comprehensive_tests()
            generator.print_report(report)
            await generator.save_report(report)

            # Return appropriate exit code
            critical_issues = len(report["critical_issues"])
            failed_tests = report["summary"]["failed_tests"]

            if critical_issues > 0:
                return 2
            elif failed_tests > 0:
                return 1
            else:
                return 0

        except Exception as e:
            print(f"Error generating report: {e}")
            import traceback
            traceback.print_exc()
            return 3


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run integration tests for the movie generation platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --suite fast                    # Run fast health checks
  %(prog)s --suite brain_service          # Test brain service only
  %(prog)s --suite all                    # Run all tests
  %(prog)s --generate-report              # Generate comprehensive report
  %(prog)s --list-suites                  # Show available test suites
  %(prog)s --install-deps                 # Install test dependencies
  %(prog)s --check-deps                   # Check if dependencies are installed

Test Suites:
  health       - Basic service health checks
  brain_service - Brain service WebSocket tests
  cross_service - Cross-service integration tests
  embedding    - Embedding and knowledge graph tests
  performance  - Performance and load tests
  startup      - Service startup and initialization tests
  fast         - Quick health and connectivity tests
  all          - All integration tests
        """
    )

    parser.add_argument(
        "--suite", "-s",
        help="Test suite to run",
        choices=list(TEST_SUITES.keys())
    )

    parser.add_argument(
        "--generate-report", "-r",
        action="store_true",
        help="Generate comprehensive test report"
    )

    parser.add_argument(
        "--list-suites", "-l",
        action="store_true",
        help="List available test suites"
    )

    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies"
    )

    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check if test dependencies are installed"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--markers", "-m",
        help="Pytest markers to filter tests (e.g., 'not slow')"
    )

    parser.add_argument(
        "--html-report",
        help="Generate HTML report at specified path"
    )

    parser.add_argument(
        "--json-report",
        help="Generate JSON report at specified path"
    )

    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to pytest"
    )

    args = parser.parse_args()

    # Create test runner
    runner = TestRunner(verbose=args.verbose)

    # Handle different commands
    if args.check_deps:
        if runner.check_dependencies():
            print("All test dependencies are available")
            return 0
        else:
            return 1

    elif args.install_deps:
        return runner.install_dependencies()

    elif args.list_suites:
        runner.list_suites()
        return 0

    elif args.generate_report:
        return asyncio.run(runner.generate_report())

    elif args.suite:
        # Prepare additional pytest arguments
        additional_args = []

        if args.markers:
            additional_args.extend(["-m", args.markers])

        if args.html_report:
            additional_args.extend(["--html", args.html_report])

        if args.json_report:
            additional_args.extend(["--json-report", "--json-report-file", args.json_report])

        if args.pytest_args:
            # Remove the first element if it's '--'
            pytest_args = args.pytest_args
            if pytest_args and pytest_args[0] == '--':
                pytest_args = pytest_args[1:]
            additional_args.extend(pytest_args)

        return runner.run_suite(args.suite, additional_args)

    else:
        # Default: check dependencies and show available options
        print("Movie Generation Platform - Integration Test Runner")
        print("=" * 50)

        if not runner.check_dependencies():
            print("\nTo install dependencies:")
            print("  python tests/run_integration_tests.py --install-deps")
            return 1

        print("\nUsage examples:")
        print("  python tests/run_integration_tests.py --suite fast")
        print("  python tests/run_integration_tests.py --generate-report")
        print("  python tests/run_integration_tests.py --list-suites")
        print("\nFor more options:")
        print("  python tests/run_integration_tests.py --help")

        return 0


if __name__ == "__main__":
    sys.exit(main())