#!/usr/bin/env python3
"""Quick test of universal prompt system."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.logging_config import setup_logging
from src.services.container import ServiceContainer

setup_logging(log_level="WARNING")


async def quick_test():
    """Quick test to verify universal prompt works."""
    print("🧪 Quick Universal Prompt Test")

    try:
        container = ServiceContainer()
        await container.initialize_services()
        service = container.code_generation_service

        request = await service.start_generation("Create a simple numpy array demo")
        print("✅ Request created successfully")

        count = 0
        start_time = asyncio.get_event_loop().time()

        async for event in service.generate_code_stream(request):
            elapsed = asyncio.get_event_loop().time() - start_time
            event_type = event.get('type', 'unknown')

            if event_type == 'phase_start':
                print(f"[{elapsed:.1f}s] 📍 PHASE START: {event.get('phase', 'unknown')} - {event.get('message', '')[:50]}...")
            elif event_type == 'phase_complete':
                print(f"[{elapsed:.1f}s] ✅ PHASE COMPLETE: {event.get('phase', 'unknown')}")
            elif event_type == 'ai_thinking':
                thinking_count = len(event.get('data', []))
                print(f"[{elapsed:.1f}s] 🧠 AI THINKING: {thinking_count} packets")
            elif event_type == 'educational_message':
                msg = event.get('message', '')[:30]
                print(f"[{elapsed:.1f}s] 📚 EDUCATIONAL: {msg}...")
            elif event_type == 'text':
                count += 1
                content_preview = event.get('content', '')[:30].replace('\n', ' ')
                print(f"[{elapsed:.1f}s] 📝 TEXT CHUNK {count}: {content_preview}...")
            elif event_type == 'completion':
                print(f"[{elapsed:.1f}s] ✅ GENERATION COMPLETED with {count} text chunks")
                return True
            elif event_type == 'error':
                print(f"[{elapsed:.1f}s] ❌ ERROR: {event.get('message', 'unknown error')}")
                return False
            else:
                print(f"[{elapsed:.1f}s] ❓ UNKNOWN EVENT: {event_type} - {str(event)[:100]}...")

    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

    return False


if __name__ == "__main__":
    result = asyncio.run(quick_test())
    print(f"Result: {'PASS' if result else 'FAIL'}")
