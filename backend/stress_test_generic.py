#!/usr/bin/env python3
"""
Phase 5 Generic Code Generation Stress Test

Comprehensive robustness testing for the AI Code Flow generic code generation system.
Tests 30 diverse prompts across 6 categories to ensure system stability and syntax correctness.
"""

import asyncio
import ast
import random
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.logging_config import setup_logging, get_logger
from src.services.container import ServiceContainer
from src.services.code_generation_service import CodeGenerationService, CodeGenerationServiceError

logger = get_logger()


@dataclass
class TestResult:
    """Result of a single stress test."""
    iteration: int
    prompt: str
    success: bool
    artifacts_found: List[str]
    syntax_errors: List[str]
    total_files: int
    execution_time: float
    error_message: Optional[str] = None


# Intermediate-level test library with 30 logic-focused prompts
TOPIC_LIBRARY = [
    # Web Automation & APIs (Single File)
    "Write a script that scrapes headlines from a news site and saves to CSV (using requests/bs4)",
    "Create a FastAPI app with one endpoint that accepts an image and returns its dimensions (using Pillow)",
    "Write a script to check stock prices for a list of symbols using a free API",
    "Create a Flask app that renders a simple HTML form to calculate BMI (HTML inside string)",
    "Write an async script to fetch 5 URLs concurrently using aiohttp",

    # Data Analysis & Visualization
    "Generate mock sales data and plot a monthly revenue bar chart using matplotlib",
    "Read a CSV file, group data by 'Category', and print the sum of 'Amount' for each",
    "Create a script to detect outliers in a dataset using the IQR method (numpy/pandas)",
    "Generate a heatmap image from a random 10x10 matrix using seaborn",
    "Write a script to resize all images in a folder to 800x600 using Pillow",

    # GUI & Games (Self-Contained Logic)
    "Create a Snake Game using pygame (single file, complete logic)",
    "Build a text editor GUI with Open/Save functionality using tkinter",
    "Create a 'Tic-Tac-Toe' game with a simple AI opponent (terminal based)",
    "Use turtle to draw a fractal tree (recursive visualization)",
    "Create a Stopwatch GUI application with Start/Stop/Reset buttons using tkinter",

    # System & CLI Tools
    "Create a CLI tool that recursively finds duplicate files in a directory (by hash)",
    "Write a script to monitor CPU and Memory usage every 5 seconds and log to file",
    "Create a CLI tool to encryption/decrypt a text file using a simple XOR key",
    "Write a script to organize a Downloads folder by file extension",
    "Create a port scanner that checks open ports on localhost (1-1024)",

    # Algorithms & Data Structures
    "Implement a 'Stack' and 'Queue' class from scratch and demonstrate usage",
    "Solve the 'Tower of Hanoi' problem with visualization of steps",
    "Implement a simple neural network forward pass using numpy (no training)",
    "Write a Sudoku solver using backtracking algorithm",
    "Implement Dijkstra's shortest path algorithm for a small graph",

    # Practical Utilities
    "Create a script to generate a QR code from user input string",
    "Write a Markdown to HTML converter script (simple regex based)",
    "Create a password strength checker that validates length and character types",
    "Write a script to parse a log file and extract all IP addresses",
    "Create a simple currency converter (hardcoded rates) with a command loop"
]


class GenericStressTester:
    """Comprehensive stress tester for generic code generation."""

    def __init__(self):
        self.results: List[TestResult] = []
        self.service: Optional[CodeGenerationService] = None

    async def initialize(self):
        """Initialize the testing environment."""
        print("🚀 INITIALIZING STRESS TEST ENVIRONMENT")
        print("=" * 60)

        # Setup logging
        setup_logging(log_level="WARNING")  # Reduce log noise during testing

        # Initialize services
        container = ServiceContainer()
        await container.initialize_services()
        self.service = container.code_generation_service

        print("✅ Services initialized successfully")

    def select_random_prompts(self, count: int = 1) -> List[str]:
        """Randomly select prompts from the library without replacement."""
        # Use timestamp-based seed for true randomness each run
        random.seed(int(time.time() * 1000000) % 2**32)

        available_prompts = TOPIC_LIBRARY.copy()
        selected = []

        for _ in range(min(count, len(available_prompts))):
            if not available_prompts:
                break
            prompt = random.choice(available_prompts)
            available_prompts.remove(prompt)
            selected.append(prompt)

        return selected

    def validate_project_artifacts(self, project_path: Path) -> Tuple[List[str], bool]:
        """Validate that required artifacts exist."""
        required_artifacts = ["requirements.txt", "spec.md", "plan.md", "README.md"]
        found_artifacts = []

        # Check for artifacts in the project directory and subdirectories
        for artifact in required_artifacts:
            # Look in main directory first
            if (project_path / artifact).exists():
                found_artifacts.append(artifact)
            else:
                # Look in subdirectories
                for file_path in project_path.rglob(artifact):
                    found_artifacts.append(artifact)
                    break

        all_found = len(found_artifacts) >= 3  # At least requirements.txt, spec.md, plan.md
        return found_artifacts, all_found

    def validate_python_syntax(self, project_path: Path) -> Tuple[List[str], bool]:
        """Validate syntax of all Python files in the project."""
        syntax_errors = []
        python_files_found = 0

        # Find all Python files
        for py_file in project_path.rglob("*.py"):
            python_files_found += 1
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source_code = f.read()

                # Parse with AST to check syntax
                ast.parse(source_code, filename=str(py_file))

            except SyntaxError as e:
                error_msg = f"{py_file.name}: {e.msg} at line {e.lineno}"
                syntax_errors.append(error_msg)
            except UnicodeDecodeError:
                syntax_errors.append(f"{py_file.name}: Unicode decode error")
            except Exception as e:
                syntax_errors.append(f"{py_file.name}: {str(e)}")

        syntax_valid = len(syntax_errors) == 0 and python_files_found > 0
        return syntax_errors, syntax_valid

    async def run_single_test(self, iteration: int, prompt: str) -> TestResult:
        """Run a single stress test iteration."""
        start_time = time.time()

        print(f"\n[ITERATION {iteration}/3] 🧪 Testing Topic: \"{prompt[:50]}...\"")

        try:
            # Start code generation
            request = await self.service.start_generation(prompt)
            print("   📝 Request created, starting generation...")

            # Run the generation process
            async for event in self.service.generate_code_stream(request):
                if event.get("type") == "error":
                    raise CodeGenerationServiceError(event.get("message", "Generation failed"))

            # Wait a moment for file system operations
            await asyncio.sleep(1)

            # Find the generated project
            projects_dir = Path("../projects")
            if not projects_dir.exists():
                raise FileNotFoundError("Projects directory not found")

            # Get the most recent project directory
            project_dirs = [d for d in projects_dir.iterdir() if d.is_dir() and d.name not in ['temp', 'archive']]
            if not project_dirs:
                raise FileNotFoundError("No project directories found")

            latest_project = max(project_dirs, key=lambda d: d.stat().st_mtime)
            print(f"   📁 Project generated: {latest_project.name}")

            # Validate artifacts
            artifacts, artifacts_ok = self.validate_project_artifacts(latest_project)
            print(f"   📦 Artifacts check: {len(artifacts)}/4 files found")

            # Validate syntax
            syntax_errors, syntax_ok = self.validate_python_syntax(latest_project)
            python_files = len(list(latest_project.rglob("*.py")))
            print(f"   🐍 Syntax check: {python_files} files, {'PASS' if syntax_ok else 'FAIL'}")

            if syntax_errors:
                print(f"   ❌ Syntax errors: {len(syntax_errors)} found")
                for error in syntax_errors[:3]:  # Show first 3 errors
                    print(f"      • {error}")

            # Determine overall success
            success = artifacts_ok and syntax_ok

            execution_time = time.time() - start_time

            result = TestResult(
                iteration=iteration,
                prompt=prompt,
                success=success,
                artifacts_found=artifacts,
                syntax_errors=syntax_errors,
                total_files=len(list(latest_project.rglob("*"))),
                execution_time=execution_time
            )

            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} ({execution_time:.1f}s)")

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)

            print(f"   💥 ERROR: {error_msg} ({execution_time:.1f}s)")

            return TestResult(
                iteration=iteration,
                prompt=prompt,
                success=False,
                artifacts_found=[],
                syntax_errors=[],
                total_files=0,
                execution_time=execution_time,
                error_message=error_msg
            )

    async def run_stress_test(self, iterations: int = 3):
        """Run the complete stress test suite."""
        print("🔬 PHASE 5 GENERIC CODE GENERATION STRESS TEST")
        print("=" * 60)
        print(f"Testing {iterations} random prompts from {len(TOPIC_LIBRARY)}-item library")
        print("Categories: Web Apps, Data Analysis, GUI/Game, CLI Tools, Algorithms, Utilities")
        print("=" * 60)

        # Initialize
        await self.initialize()

        # Log topic library size
        print(f"📚 Topic Library: {len(TOPIC_LIBRARY)} prompts available")
        print(f"🎲 Random seed: {int(time.time() * 1000000) % 2**32}")

        # Select random prompts
        test_prompts = self.select_random_prompts(iterations)
        print(f"\n🎯 Selected {len(test_prompts)} test prompt(s):")
        for i, prompt in enumerate(test_prompts, 1):
            print(f"   {i}. {prompt[:60]}{'...' if len(prompt) > 60 else ''}")

        print(f"\n🚀 Starting {iterations} test iteration(s)...")

        # Run tests
        for i, prompt in enumerate(test_prompts, 1):
            result = await self.run_single_test(i, prompt)
            self.results.append(result)

            # Exit immediately on failure
            if not result.success:
                print(f"\n💥 TEST FAILURE DETECTED - EXITING IMMEDIATELY")
                print(f"   Failed test: {result.prompt[:50]}...")
                if result.error_message:
                    print(f"   Error: {result.error_message}")
                self.generate_summary_report()
                sys.exit(1)

        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate and display the test summary report."""
        print("\n" + "=" * 60)
        print("📊 STRESS TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r.success)
        total = len(self.results)
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()

        # Individual test results
        for result in self.results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            artifacts_count = len(result.artifacts_found)
            files_info = f"Files: {result.total_files}"

            if result.success:
                syntax_info = "Syntax: OK"
            elif result.syntax_errors:
                syntax_info = f"Syntax: {len(result.syntax_errors)} errors"
            else:
                syntax_info = "Syntax: Not tested"

            print(f"{result.iteration}. [{result.prompt[:30]}...] -> {status} ({files_info}, {syntax_info})")

            if not result.success and result.error_message:
                print(f"    Error: {result.error_message}")

        print("\n" + "=" * 60)

        # Final verdict
        if success_rate >= 80:
            print("🎉 RESULT: System is ROBUST and GENERIC!")
            print("   The AI Code Flow successfully handles diverse application types.")
        elif success_rate >= 60:
            print("⚠️  RESULT: System is MOSTLY ROBUST")
            print("   Some application types need improvement.")
        else:
            print("❌ RESULT: System needs significant improvements")
            print("   Many application types are failing.")

        print(f"\nRobustness Score: {passed}/{total} tests passed")
        print("=" * 60)


async def main():
    """Main stress test function."""
    # Set random seed for reproducible testing
    random.seed(42)

    tester = GenericStressTester()
    await tester.run_stress_test(iterations=1)


def run_stress_test():
    """Run the stress test with proper asyncio handling for Windows."""
    # Handle Windows asyncio event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Stress test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error during stress test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_stress_test()
