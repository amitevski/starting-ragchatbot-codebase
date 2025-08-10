"""
Test runner utility for the RAG system tests
"""
import pytest
import sys
import os
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def run_all_tests():
    """Run all tests with coverage reporting"""
    pytest_args = [
        "-v",
        "--cov=backend",
        "--cov-report=term-missing",
        "--cov-report=html:backend/tests/htmlcov",
        "backend/tests/",
    ]
    return pytest.main(pytest_args)


def run_api_tests_only():
    """Run only API endpoint tests"""
    pytest_args = [
        "-v",
        "-m", "api",
        "backend/tests/test_api_endpoints.py",
    ]
    return pytest.main(pytest_args)


def run_unit_tests_only():
    """Run only unit tests"""
    pytest_args = [
        "-v",
        "-m", "unit",
        "backend/tests/test_unit_components.py",
    ]
    return pytest.main(pytest_args)


def run_with_markers():
    """Run tests by specific markers"""
    print("Available test markers:")
    print("  - unit: Run unit tests")
    print("  - integration: Run integration tests") 
    print("  - api: Run API endpoint tests")
    print("\nUsage: python -m pytest -m <marker> backend/tests/")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "api":
            exit_code = run_api_tests_only()
        elif command == "unit":
            exit_code = run_unit_tests_only()
        elif command == "help":
            run_with_markers()
            exit_code = 0
        else:
            print(f"Unknown command: {command}")
            print("Available commands: all, api, unit, help")
            exit_code = 1
    else:
        exit_code = run_all_tests()
    
    sys.exit(exit_code)