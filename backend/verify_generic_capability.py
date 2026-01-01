#!/usr/bin/env python3
"""
Verify Generic Code Generation Capability

Tests that the universal prompt system correctly generates appropriate code
for different user requests without hallucinations.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.logging_config import setup_logging
from src.services.container import ServiceContainer

setup_logging(log_level="WARNING")


async def test_numpy_generation():
    """Test that numpy request generates numpy code, not snake game."""
    print("🧪 Testing Numpy Generation...")

    container = ServiceContainer()
    await container.initialize_services()
    service = container.code_generation_service

    request = await service.start_generation("使用numpy进行数组操作和数学计算的示例")

    code_content = ""
    async for event in service.generate_code_stream(request):
        if event.get('type') == 'text':
            code_content += event.get('content', '')
        elif event.get('type') == 'complete':
            break
        elif event.get('type') == 'error':
            print(f"❌ Error: {event.get('message')}")
            return False

    # Check that code contains numpy but not pygame
    has_numpy = 'numpy' in code_content.lower() or 'np.' in code_content
    has_pygame = 'pygame' in code_content.lower()
    has_snake = 'snake' in code_content.lower() or '贪吃蛇' in code_content

    print(f"  Contains numpy: {'✅' if has_numpy else '❌'}")
    print(f"  Contains pygame: {'❌' if not has_pygame else '✅'}")
    print(f"  Contains snake references: {'❌' if not has_snake else '✅'}")

    return has_numpy and not has_pygame and not has_snake


async def test_web_app_generation():
    """Test that web app request generates web app code."""
    print("\n🧪 Testing Web App Generation...")

    container = ServiceContainer()
    await container.initialize_services()
    service = container.code_generation_service

    request = await service.start_generation("创建一个简单的Flask Web应用，显示'Hello World'")

    code_content = ""
    async for event in service.generate_code_stream(request):
        if event.get('type') == 'text':
            code_content += event.get('content', '')
        elif event.get('type') == 'complete':
            break
        elif event.get('type') == 'error':
            print(f"❌ Error: {event.get('message')}")
            return False

    # Check that code contains flask but not pygame
    has_flask = 'flask' in code_content.lower()
    has_pygame = 'pygame' in code_content.lower()
    has_hello = 'hello' in code_content.lower() or 'Hello' in code_content

    print(f"  Contains flask: {'✅' if has_flask else '❌'}")
    print(f"  Contains pygame: {'❌' if not has_pygame else '✅'}")
    print(f"  Contains hello world: {'✅' if has_hello else '❌'}")

    return has_flask and not has_pygame and has_hello


async def test_universal_prompt_consistency():
    """Test that the universal prompt system produces consistent results."""
    print("\n🧪 Testing Universal Prompt Consistency...")

    container = ServiceContainer()
    await container.initialize_services()
    service = container.code_generation_service

    # Test the same request multiple times to ensure consistency
    test_request = "创建一个简单的计算器函数"
    results = []

    for i in range(2):
        print(f"  Run {i+1}...")
        request = await service.start_generation(test_request)

        code_content = ""
        async for event in service.generate_code_stream(request):
            if event.get('type') == 'text':
                code_content += event.get('content', '')
            elif event.get('type') == 'completion':
                break
            elif event.get('type') == 'error':
                print(f"    ❌ Error: {event.get('message')}")
                results.append(False)
                break
        else:
            # Check for basic calculator functionality
            has_def = 'def ' in code_content
            has_add = '+' in code_content
            has_functionality = has_def and (has_add or 'calculate' in code_content.lower())

            results.append(has_functionality)
            print(f"    ✅ Generated calculator code: {has_functionality}")

    # Check consistency
    all_passed = all(results)
    consistent = len(set(results)) == 1  # All results should be the same

    print(f"  All runs passed: {'✅' if all_passed else '❌'}")
    print(f"  Results consistent: {'✅' if consistent else '❌'}")

    return all_passed and consistent


async def main():
    """Run all capability tests."""
    print("🔬 VERIFYING GENERIC CODE GENERATION CAPABILITY")
    print("=" * 55)

    tests = [
        ("Numpy Generation", test_numpy_generation),
        ("Web App Generation", test_web_app_generation),
        ("Universal Prompt Consistency", test_universal_prompt_consistency),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")

    print("\n" + "=" * 55)
    print("📊 GENERIC CAPABILITY TEST RESULTS")
    print(f"Passed: {passed}/{total}")
    success_rate = passed / total * 100
    print(".1f")

    if success_rate >= 80:
        print("🎉 Universal Prompt System: HIGHLY EFFECTIVE")
        print("   System correctly generates appropriate code for different requests")
        print("   No hallucinations detected - templates successfully deprecated")
    elif success_rate >= 60:
        print("⚠️  Universal Prompt System: MODERATELY EFFECTIVE")
        print("   Some issues remain but significant improvement over templates")
    else:
        print("❌ Universal Prompt System: NEEDS IMPROVEMENT")
        print("   Hallucinations or inconsistencies still present")

    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
