#!/usr/bin/env python3
"""
Comprehensive test runner for the Property Analysis System
"""

import sys
import os
import subprocess
import argparse

def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests based on specified type"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=vision", "--cov=rag", "--cov=agents", "--cov-report=html"])
    
    # Test selection
    if test_type == "all":
        cmd.append("Test/")
    elif test_type == "vision":
        cmd.extend(["Test/test_vision.py", "-m", "vision"])
    elif test_type == "rag":
        cmd.extend(["Test/test_rag.py", "-m", "rag"])
    elif test_type == "agents":
        cmd.extend(["Test/test_agents.py", "-m", "agents"])
    elif test_type == "integration":
        cmd.extend(["Test/test_integration.py", "-m", "integration"])
    elif test_type == "unit":
        cmd.extend(["Test/", "-m", "not integration"])
    else:
        cmd.append(f"Test/test_{test_type}.py")
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with return code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("pytest not found. Install with: pip install pytest pytest-cov")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run Property Analysis System tests")
    parser.add_argument(
        "--type", 
        choices=["all", "vision", "rag", "agents", "integration", "unit"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Property Analysis System Test Suite")
    print("=" * 60)
    
    success = run_tests(args.type, args.verbose, args.coverage)
    
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()