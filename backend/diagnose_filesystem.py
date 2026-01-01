#!/usr/bin/env python3
"""
Filesystem Diagnostic Script

Tests file writing operations to identify silent failures and filesystem issues.
This script comprehensively tests file I/O operations to ensure files are actually
being written to disk and can be read back correctly.
"""

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.logging_config import setup_logging, get_logger
from src.services.container import ServiceContainer
from src.config import get_config

logger = get_logger()


class FilesystemDiagnostic:
    """Comprehensive filesystem diagnostic tool."""

    def __init__(self):
        self.results = {
            "tests": [],
            "issues": [],
            "recommendations": []
        }

    def log_test_result(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log a test result."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": time.time()
        }
        self.results["tests"].append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        if error:
            print(f"   ERROR: {error}")

    def add_issue(self, issue: str):
        """Add an identified issue."""
        self.results["issues"].append(issue)

    def add_recommendation(self, recommendation: str):
        """Add a recommendation."""
        self.results["recommendations"].append(recommendation)

    async def test_basic_file_operations(self) -> bool:
        """Test basic file write/read operations."""
        print("🧪 Testing Basic File Operations")
        print("-" * 40)

        try:
            # Test 1: Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                test_content = "Test content for filesystem diagnostic"
                f.write(test_content)
                temp_path = Path(f.name)

            # Verify file exists and has correct content
            if not temp_path.exists():
                self.log_test_result("Temp file creation", False, error="File does not exist after creation")
                return False

            with open(temp_path, 'r') as f:
                read_content = f.read()

            if read_content != test_content:
                self.log_test_result("Temp file read/write", False,
                                   error=f"Content mismatch: expected '{test_content}', got '{read_content}'")
                return False

            # Clean up
            temp_path.unlink()
            self.log_test_result("Basic file operations", True, "Temp file write/read successful")
            return True

        except Exception as e:
            self.log_test_result("Basic file operations", False, error=str(e))
            return False

    async def test_directory_operations(self) -> bool:
        """Test directory creation and file operations within directories."""
        print("📁 Testing Directory Operations")
        print("-" * 40)

        try:
            # Create test directory
            test_dir = Path(tempfile.gettempdir()) / f"fs_diag_{int(time.time())}"
            test_dir.mkdir(exist_ok=True)

            # Test 2: Create nested directories
            nested_dir = test_dir / "nested" / "deep"
            nested_dir.mkdir(parents=True, exist_ok=True)

            if not nested_dir.exists():
                self.log_test_result("Nested directory creation", False, error="Nested directory not created")
                return False

            # Test 3: Write file in nested directory
            test_file = nested_dir / "test.txt"
            test_content = "File in nested directory"

            with open(test_file, 'w') as f:
                f.write(test_content)

            if not test_file.exists():
                self.log_test_result("File in nested directory", False, error="File not created in nested directory")
                return False

            with open(test_file, 'r') as f:
                if f.read() != test_content:
                    self.log_test_result("File in nested directory", False, error="Content mismatch in nested file")
                    return False

            # Clean up
            import shutil
            shutil.rmtree(test_dir)

            self.log_test_result("Directory operations", True, "Directory creation and nested file operations successful")
            return True

        except Exception as e:
            self.log_test_result("Directory operations", False, error=str(e))
            return False

    async def test_project_directory_structure(self) -> bool:
        """Test the actual project directory structure and configuration."""
        print("🏗️ Testing Project Directory Structure")
        print("-" * 40)

        try:
            config = get_config()
            projects_dir = Path(config.system.projects_dir)

            # Test 4: Check if configured projects directory exists
            if not projects_dir.exists():
                self.log_test_result("Projects directory existence", False,
                                   error=f"Configured projects directory does not exist: {projects_dir}")
                return False

            self.log_test_result("Projects directory existence", True, f"Directory exists: {projects_dir}")

            # Test 5: Check directory permissions
            if not os.access(projects_dir, os.W_OK):
                self.log_test_result("Projects directory permissions", False,
                                   error=f"No write permission for projects directory: {projects_dir}")
                return False

            self.log_test_result("Projects directory permissions", True, "Write permissions confirmed")

            # Test 6: Check for existing projects
            project_dirs = [d for d in projects_dir.iterdir() if d.is_dir() and d.name not in ['temp', 'archive']]
            self.log_test_result("Existing projects detection", True, f"Found {len(project_dirs)} project directories")

            # Test 7: Check backend/workspace directory
            workspace_dir = Path(__file__).parent / "workspace"
            if workspace_dir.exists():
                workspace_files = list(workspace_dir.iterdir())
                self.log_test_result("Backend workspace check", True,
                                   f"Workspace exists with {len(workspace_files)} files")
                for file_path in workspace_files[:5]:  # Show first 5 files
                    print(f"   📄 {file_path.name}")
            else:
                self.log_test_result("Backend workspace check", False, "backend/workspace directory does not exist")

            return True

        except Exception as e:
            self.log_test_result("Project directory structure", False, error=str(e))
            return False

    async def test_project_service_file_writing(self) -> bool:
        """Test the actual project service file writing operations."""
        print("💾 Testing Project Service File Writing")
        print("-" * 40)

        try:
            # Initialize services
            container = ServiceContainer()
            await container.initialize_services()
            project_service = container.project_service

            # Test 8: Create a test project using the service
            from uuid import uuid4
            test_project_id = str(uuid4())

            test_project_data = {
                "id": test_project_id,
                "request_id": test_project_id,
                "project_name": "filesystem_diagnostic_test",
                "main_file": "main.py",
                "created_at": time.strftime('%Y-%m-%d_%H-%M-%S'),
                "file_structure": {
                    "type": "directory",
                    "name": "filesystem_diagnostic_test",
                    "children": []
                },
                "dependencies": ["pytest"],
                "total_files": 1,
                "total_size_bytes": 100
            }

            test_file_contents = {
                "main.py": "# Test file for filesystem diagnostic\nprint('Hello from filesystem test!')\n"
            }

            # Save project using service
            saved_project = await project_service.save_project(test_project_data, test_file_contents)

            if not saved_project:
                self.log_test_result("Project service save operation", False, error="Project service returned None")
                return False

            # Test 9: Verify project was saved correctly
            project_dir = project_service._get_project_dir(saved_project.id)
            if not project_dir.exists():
                self.log_test_result("Project directory creation", False,
                                   error=f"Project directory not created: {project_dir}")
                return False

            # Check metadata file
            metadata_file = project_service._get_project_metadata_file(saved_project.id)
            if not metadata_file.exists():
                self.log_test_result("Project metadata file", False,
                                   error=f"Metadata file not created: {metadata_file}")
                return False

            # Check project files
            main_file = project_dir / "filesystem_diagnostic_test" / "main.py"
            if not main_file.exists():
                self.log_test_result("Project main file", False,
                                   error=f"Main file not created: {main_file}")
                return False

            # Verify file content
            with open(main_file, 'r') as f:
                content = f.read()
                expected = "# Test file for filesystem diagnostic\nprint('Hello from filesystem test!')\n"
                if content != expected:
                    self.log_test_result("Project file content", False,
                                       error=f"Content mismatch in {main_file}")
                    return False

            self.log_test_result("Project service file writing", True,
                               f"Successfully created project: {saved_project.project_name}")

            # Clean up test project
            import shutil
            shutil.rmtree(project_dir)

            return True

        except Exception as e:
            self.log_test_result("Project service file writing", False, error=str(e))
            return False

    async def test_file_encoding_and_permissions(self) -> bool:
        """Test file encoding and permission issues."""
        print("🔒 Testing File Encoding and Permissions")
        print("-" * 40)

        try:
            # Test 10: UTF-8 encoding test
            test_content = "测试中文内容\nTest English content\n🚀 Emoji test"
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
                f.write(test_content)
                utf8_path = Path(f.name)

            with open(utf8_path, 'r', encoding='utf-8') as f:
                read_content = f.read()

            if read_content != test_content:
                self.log_test_result("UTF-8 encoding", False, error="UTF-8 content mismatch")
                return False

            utf8_path.unlink()
            self.log_test_result("UTF-8 encoding", True, "UTF-8 encoding works correctly")

            # Test 11: File permission test
            test_file = Path(tempfile.gettempdir()) / f"perm_test_{int(time.time())}.txt"
            with open(test_file, 'w') as f:
                f.write("Permission test")

            # Check if file is readable/writable
            if not (os.access(test_file, os.R_OK) and os.access(test_file, os.W_OK)):
                self.log_test_result("File permissions", False, error="File permission issues detected")
                test_file.unlink()
                return False

            test_file.unlink()
            self.log_test_result("File permissions", True, "File permissions are correct")

            return True

        except Exception as e:
            self.log_test_result("File encoding and permissions", False, error=str(e))
            return False

    async def run_full_diagnostic(self) -> Dict:
        """Run the complete filesystem diagnostic suite."""
        print("🔍 FILESYSTEM DIAGNOSTIC SUITE")
        print("=" * 50)
        print("Testing file I/O operations to identify silent failures...")
        print()

        # Run all tests
        tests = [
            self.test_basic_file_operations(),
            self.test_directory_operations(),
            self.test_project_directory_structure(),
            self.test_project_service_file_writing(),
            self.test_file_encoding_and_permissions(),
        ]

        # Wait for all tests to complete
        results = await asyncio.gather(*tests, return_exceptions=True)

        # Analyze results
        passed = sum(1 for r in results if r is True)
        failed = sum(1 for r in results if r is False or isinstance(r, Exception))
        total = len(tests)

        print()
        print("📊 DIAGNOSTIC RESULTS SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(".1f")

        if failed > 0:
            print("\n⚠️ ISSUES DETECTED:")
            for issue in self.results["issues"]:
                print(f"   • {issue}")

        if self.results["recommendations"]:
            print("\n💡 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"   • {rec}")

        # Check for specific issues
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - Filesystem is working correctly!")
            self.add_recommendation("Filesystem is healthy - no issues detected")
        else:
            print("\n❌ ISSUES FOUND - Filesystem may have problems")

            # Add specific recommendations based on failures
            if any("permission" in str(t).lower() for t in self.results["tests"] if not t["success"]):
                self.add_issue("Permission issues detected")
                self.add_recommendation("Check file/directory permissions")
                self.add_recommendation("Run as administrator or check user permissions")

            if any("encoding" in str(t).lower() for t in self.results["tests"] if not t["success"]):
                self.add_issue("Encoding issues detected")
                self.add_recommendation("Ensure all file operations use UTF-8 encoding")

            if any("directory" in str(t).lower() for t in self.results["tests"] if not t["success"]):
                self.add_issue("Directory creation issues detected")
                self.add_recommendation("Check available disk space")
                self.add_recommendation("Verify directory paths are valid")

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed / total if total > 0 else 0,
            "issues": self.results["issues"],
            "recommendations": self.results["recommendations"],
            "test_details": self.results["tests"]
        }


async def main():
    """Main diagnostic function."""
    # Setup logging
    setup_logging(log_level="INFO")

    diagnostic = FilesystemDiagnostic()
    results = await diagnostic.run_full_diagnostic()

    # Save results to file
    results_file = Path(__file__).parent / "filesystem_diagnostic_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📄 Detailed results saved to: {results_file}")

    # Exit with appropriate code
    success = results["success_rate"] == 1.0
    sys.exit(0 if success else 1)


def run_diagnostic():
    """Run the diagnostic with proper asyncio handling for Windows."""
    # Handle Windows asyncio event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Diagnostic interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_diagnostic()
