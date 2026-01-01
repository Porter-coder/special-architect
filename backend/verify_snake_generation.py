#!/usr/bin/env python3
"""
Snake Game Generation Verification Script

Automated test to verify the core code generation pipeline works end-to-end.
Tests real API calls, three-phase workflow, and file generation.

Usage: python verify_snake_generation.py
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Ensure we can import from src
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_config
from src.logging_config import setup_logging
from src.services.container import container


async def main():
    """Main verification function."""
    print("🐍 Snake Game Generation Verification")
    print("=" * 50)

    # Setup logging
    setup_logging(log_level="INFO")

    try:
        # 1. Environment Integration
        print("📋 Step 1: Environment Integration")
        config = get_config()
        print(f"✅ Config loaded: MiniMax API key present: {'Yes' if config.minimax.api_key else 'No'}")

        # Initialize services
        await container.initialize_services()
        print("✅ Services initialized")

        # 2. Execute Code Generation
        print("\n🚀 Step 2: Code Generation Execution")
        print("Prompt: 'Create a simple Snake Game using Python and Pygame. Single file implementation.'")

        # Create test request
        code_gen_service = container.code_generation_service

        # Debug: Check if we have any generated content from previous runs
        print("🔍 Checking for existing projects...")
        projects_dir = Path(__file__).parent.parent / "projects"
        if projects_dir.exists():
            project_dirs = [d for d in projects_dir.iterdir() if d.is_dir() and d.name not in ['temp', 'archive']]
            print(f"Found {len(project_dirs)} existing projects")

        # First create the request object
        request = await code_gen_service.start_generation("Create a simple Snake Game using Python and Pygame. Single file implementation.")
        print(f"✅ Request created: {request.request_id}")

        start_time = time.time()
        current_phase = None
        events_received = []

        # Stream the generation process
        print("\n📊 Generation Progress:")
        print("-" * 30)

        try:
            async for event in code_gen_service.generate_code_stream(request):
                events_received.append(event)

                # Track phase changes
                if event.get("type") == "phase_start":
                    new_phase = event.get("phase")
                    if new_phase != current_phase:
                        current_phase = new_phase
                        print(f"🔄 Phase: {current_phase}")

                elif event.get("type") == "phase_complete":
                    print(f"✅ Phase {event.get('phase')} completed")
                    # Debug: show content length
                    content_length = event.get('content_length', 0)
                    print(f"   📏 Content length: {content_length} chars")

                elif event.get("type") == "content_chunk":
                        # Print progress indicator for content chunks
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        # Debug: show chunk type and content preview
                        chunk_type = event.get("content_type", "unknown")
                        content_preview = event.get("content", "")[:50] if event.get("content") else ""
                        if content_preview:
                            print(f"\n   📄 {chunk_type}: {content_preview}...")
                            # Debug: collect content for analysis
                            if not hasattr(verify_snake_generation, 'collected_content'):
                                verify_snake_generation.collected_content = []
                            verify_snake_generation.collected_content.append(event.get("content", ""))

                elif event.get("type") == "workflow_complete":
                    print(f"\n✅ Workflow completed: {event.get('message', '')}")
                    break

                elif event.get("type") == "workflow_failed":
                    print(f"\n❌ Workflow failed: {event.get('message', '')}")
                    return False

        except Exception as e:
            print(f"\n❌ Generation failed: {e}")
            return False

        generation_time = time.time() - start_time
        print(".4f")

        # 3. Result Verification
        print("\n🔍 Step 3: Result Verification")

        # Check if project was created
        workspace_dir = Path(__file__).parent / "workspace"
        workspace_dir.mkdir(exist_ok=True)

        # Find the most recent project
        projects_dir = Path(__file__).parent.parent / "projects"
        if not projects_dir.exists():
            print("❌ Projects directory not found")
            return False

        # Look for the most recent project directory
        project_dirs = [d for d in projects_dir.iterdir() if d.is_dir() and d.name not in ['temp', 'archive']]
        if not project_dirs:
            print("❌ No project directories found")
            return False

        # Get the most recent project
        latest_project = max(project_dirs, key=lambda d: d.stat().st_mtime)
        print(f"📁 Found project: {latest_project.name}")

        # Check for Python files
        python_files = list(latest_project.glob("**/*.py"))
        if not python_files:
            print("❌ No Python files found in project")
            return False

        print(f"🐍 Found Python files: {[f.name for f in python_files]}")

        # Copy main file to workspace for verification
        main_file = None
        for py_file in python_files:
            if py_file.name in ['main.py', 'snake_game.py', 'game.py'] or 'snake' in py_file.name.lower():
                main_file = py_file
                break

        if not main_file:
            main_file = python_files[0]  # Use first Python file

        # Copy to workspace
        workspace_file = workspace_dir / main_file.name
        workspace_file.write_text(main_file.read_text(encoding='utf-8'), encoding='utf-8')

        print(f"📋 File copied to workspace: {workspace_file}")

        # Verify file is not empty and contains expected content
        content = workspace_file.read_text(encoding='utf-8')
        if not content.strip():
            print("❌ Generated file is empty")
            return False

        # Basic content checks
        content_checks = [
            ('import pygame' in content, "Contains pygame import"),
            ('class' in content, "Contains class definition"),
            ('def main' in content or 'def run' in content, "Contains main/run function"),
            ('while True:' in content, "Contains game loop"),
        ]

        print("🔎 Content validation:")
        for check, description in content_checks:
            status = "✅" if check else "❌"
            print(f"  {status} {description}")

        # Check if all critical checks pass
        critical_checks = [check for check, desc in content_checks if 'pygame' in desc or 'class' in desc]
        if not all(critical_checks):
            print("❌ Critical content checks failed")
            return False

        # 4. Final Result
        print("\n🎉 VERIFICATION COMPLETE")
        print("✅ TEST PASSED: Snake Game Generated Successfully")
        print(f"📊 Stats: {len(content.splitlines())} lines, {len(python_files)} Python files")
        print(f"⏱️  Total time: {generation_time:.1f}s")
        print(f"📁 Output: {workspace_file}")

        return True

    except Exception as e:
        print(f"\n💥 VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_verification():
    """Run the verification with proper asyncio handling for Windows."""
    # Handle Windows asyncio event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        # Run the async main function
        success = asyncio.run(main())

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_verification()
