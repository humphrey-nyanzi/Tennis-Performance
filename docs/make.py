"""
Makefile-style commands for the Tennis Performance Analysis project.
Usage: Run tasks using 'make <task>' or python make.py <task>
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command."""
    if description:
        print(f"\n{'=' * 60}")
        print(f" {description}")
        print(f"{'=' * 60}\n")

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        sys.exit(1)


def install_dependencies():
    """Install project dependencies."""
    run_command("pip install -r requirements.txt", "Installing Dependencies")


def run_dashboard():
    """Run the Streamlit dashboard."""
    run_command(
        "streamlit run dashboard/app.py", "Starting Tennis Performance Dashboard"
    )


def run_tests():
    """Run all tests."""
    run_command("pytest tests/ -v", "Running Tests")


def run_tests_coverage():
    """Run tests with coverage report."""
    run_command(
        "pytest tests/ -v --cov=src --cov-report=html", "Running Tests with Coverage"
    )


def format_code():
    """Format code with black."""
    run_command("black src/ dashboard/ tests/", "Formatting Code with Black")


def lint_code():
    """Lint code with flake8."""
    run_command("flake8 src/ dashboard/ tests/", "Linting Code with Flake8")


def type_check():
    """Type check with mypy."""
    run_command("mypy src/", "Type Checking with MyPy")


def clean():
    """Clean up cache and build files."""
    run_command(
        "find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null; find . -type d -name .pytest_cache -exec rm -r {} + 2>/dev/null",
        "Cleaning Cache and Build Files",
    )


def docs():
    """Generate documentation."""
    run_command(
        "pdoc --html --output-dir docs src/ dashboard/", "Generating Documentation"
    )


def all_checks():
    """Run all quality checks."""
    print("\n" + "=" * 60)
    print(" Running All Quality Checks")
    print("=" * 60)

    run_tests()
    lint_code()
    format_code()
    print("\n✓ All checks completed!")


TASKS = {
    "install": install_dependencies,
    "run": run_dashboard,
    "test": run_tests,
    "test-cov": run_tests_coverage,
    "format": format_code,
    "lint": lint_code,
    "type-check": type_check,
    "clean": clean,
    "docs": docs,
    "check-all": all_checks,
}


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Available tasks:")
        for task, func in TASKS.items():
            print(f"  {task:15} - {func.__doc__}")
        sys.exit(0)

    task = sys.argv[1]

    if task not in TASKS:
        print(f"Unknown task: {task}")
        print("Available tasks:", ", ".join(TASKS.keys()))
        sys.exit(1)

    TASKS[task]()


if __name__ == "__main__":
    main()
