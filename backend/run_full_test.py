#!/usr/bin/env python3
"""
Automated Test & Fix Loop for Snake Backend

This script implements the automated verification and repair cycle:
1. Start backend service in background
2. Run verification script
3. Analyze results and apply fixes
4. Repeat until TEST PASSED or max retries reached
"""

import subprocess
import sys
import time
import signal
import os
import re
from pathlib import Path
from typing import Optional, Tuple

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

class BackendTestRunner:
    """Manages automated backend testing with service lifecycle."""

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.backend_process: Optional[subprocess.Popen] = None
        self.backend_dir = Path(__file__).parent
        self.project_root = self.backend_dir.parent

    def start_backend(self) -> bool:
        """Start uvicorn backend service in background."""
        print("🚀 Starting backend service...")

        try:
            # Set environment variables for backend
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.backend_dir)

            self.backend_process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "src.main:app",
                    "--host", "127.0.0.1",
                    "--port", "8000",
                    "--log-level", "info"
                ],
                cwd=self.backend_dir,
                env=os.environ.copy(),  # Explicitly inherit current environment
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for service to be ready
            print("⏳ Waiting for backend to start...")
            time.sleep(5)

            # Check if process is still running
            if self.backend_process.poll() is not None:
                stdout, stderr = self.backend_process.communicate()
                print(f"❌ Backend failed to start:")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False

            print("✅ Backend service started successfully")
            return True

        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False

    def stop_backend(self):
        """Stop the backend service."""
        if self.backend_process:
            print("🛑 Stopping backend service...")
            try:
                if sys.platform == "win32":
                    self.backend_process.terminate()
                    time.sleep(2)
                    if self.backend_process.poll() is None:
                        self.backend_process.kill()
                else:
                    self.backend_process.terminate()
                    try:
                        self.backend_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.backend_process.kill()

                print("✅ Backend service stopped")
            except Exception as e:
                print(f"⚠️ Warning: Could not cleanly stop backend: {e}")

    def run_verification(self) -> Tuple[bool, str]:
        """Run the verification script and capture results."""
        print("🧪 Running verification script...")

        try:
            result = subprocess.run(
                [sys.executable, "verify_snake_backend.py"],
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            if success and "TEST PASSED" in output:
                print("✅ Verification PASSED")
                return True, output
            else:
                print("❌ Verification FAILED")
                return False, output

        except subprocess.TimeoutExpired:
            print("⏰ Verification timed out")
            return False, "TIMEOUT: Verification script took too long"
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False, str(e)

    def analyze_failure(self, output: str) -> str:
        """Analyze verification failure and suggest fix."""
        print("🔍 Analyzing failure...")

        # Check for common failure patterns
        if "OPENAI_API_KEY environment variable is required" in output:
            return "API_KEY_MISSING"

        if "Connection refused" in output or "connection error" in output.lower():
            return "CONNECTION_FAILED"

        if "```python" in output or "```" in output:
            return "MARKDOWN_IN_CODE"

        if "<think>" in output:
            return "THINK_TAGS_PRESENT"

        if "incomplete" in output.lower() or "truncated" in output.lower():
            return "INCOMPLETE_CODE"

        if "syntax" in output.lower() or "indentation" in output.lower():
            return "SYNTAX_ERROR"

        return "UNKNOWN_ERROR"

    def apply_fix(self, error_type: str) -> bool:
        """Apply automatic fix based on error analysis."""
        print(f"🔧 Applying fix for: {error_type}")

        if error_type == "API_KEY_MISSING":
            print("💡 Fix: Set OPENAI_API_KEY environment variable")
            print("   Example: export OPENAI_API_KEY='your-key-here'")
            return False  # Can't auto-fix API key

        elif error_type == "CONNECTION_FAILED":
            print("💡 Fix: Check if backend service is running on port 8000")
            return False  # Need manual intervention

        elif error_type == "MARKDOWN_IN_CODE":
            print("💡 Fix: Improve markdown parsing regex")
            # Could implement auto-fix here
            return False

        elif error_type == "THINK_TAGS_PRESENT":
            print("💡 Fix: Check reasoning_split parameter in ai_service.py")
            return False

        elif error_type == "INCOMPLETE_CODE":
            print("💡 Fix: Increase max_tokens in ai_service.py")
            # Could implement auto-fix here
            return False

        return False

    def run_test_loop(self):
        """Main test and fix loop."""
        print("🔄 Starting Automated Test & Fix Loop")
        print("=" * 50)

        for attempt in range(1, self.max_retries + 1):
            print(f"\n📊 Attempt {attempt}/{self.max_retries}")
            print("-" * 30)

            # Start backend
            if not self.start_backend():
                print("❌ Cannot proceed without backend service")
                break

            try:
                # Run verification
                success, output = self.run_verification()

                if success:
                    print("🎉 TEST PASSED! Loop complete.")
                    return True

                # Analyze and fix
                error_type = self.analyze_failure(output)
                print(f"📋 Error Type: {error_type}")

                if not self.apply_fix(error_type):
                    print("⚠️ Cannot auto-fix this issue")

                print(f"📄 Full output:\n{output}")

            finally:
                # Always stop backend
                self.stop_backend()

            # Don't retry if this was the last attempt
            if attempt == self.max_retries:
                print(f"❌ Max retries ({self.max_retries}) reached. Manual intervention required.")
                break

            print("⏳ Waiting before retry...")
            time.sleep(3)

        return False


def main():
    """Main entry point."""
    print("🐍 AI Code Flow - Automated Backend Testing")
    print("=" * 50)

    # Load environment variables from .env file
    if HAS_DOTENV:
        env_file_path = Path(__file__).parent / '.env'
        if env_file_path.exists():
            print(f"📄 Loading environment from: {env_file_path}")
            load_dotenv(env_file_path)
        else:
            print("⚠️  No .env file found, using system environment variables")
    else:
        print("⚠️  python-dotenv not available, using system environment variables")

    # Check for API key before starting
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-minimax-api-key-here':
        print("⚠️  WARNING: OPENAI_API_KEY not set or using placeholder value")
        print("   Real MiniMax API credentials required for testing")
        print("   Set OPENAI_API_KEY in .env file or environment")
        print("   Continuing anyway to demonstrate the test framework...\n")

    runner = BackendTestRunner(max_retries=2)
    success = runner.run_test_loop()

    if success:
        print("\n🎉 SUCCESS: All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Tests did not pass within retry limit")
        sys.exit(1)


if __name__ == "__main__":
    main()
