#!/usr/bin/env python3
"""
Robustness Enhancement Test

Tests the enhanced delivery robustness features:
1. Self-containment validation (detects missing local files)
2. Dependency mapping (correct PyPI package names)
3. Import resolution (no ImportError on standard libraries)
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.logging_config import setup_logging, get_logger
from src.services.container import ServiceContainer
from src.services.code_generation_service import CodeGenerationService

logger = get_logger()


async def test_dependency_mapping():
    """Test that dependency analyzer correctly maps imports to packages."""
    print("🧪 Testing Dependency Mapping...")

    container = ServiceContainer()
    await container.initialize_services()
    analyzer = container.dependency_analyzer

    # Test cases: (import_name, expected_package)
    test_cases = [
        ("PIL", "pillow"),
        ("cv2", "opencv-python"),
        ("sklearn", "scikit-learn"),
        ("yaml", "pyyaml"),
        ("fastapi", "fastapi"),
        ("pygame", "pygame"),
        ("matplotlib", "matplotlib"),
    ]

    success_count = 0
    for import_name, expected_package in test_cases:
        package = analyzer._resolve_import(import_name)
        if package == expected_package:
            print(f"  ✅ {import_name} -> {package}")
            success_count += 1
        else:
            print(f"  ❌ {import_name} -> {package} (expected {expected_package})")

    print(f"Dependency mapping: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)


async def test_self_containment_detection():
    """Test that missing local files are detected."""
    print("\n🧪 Testing Self-Containment Detection...")

    container = ServiceContainer()
    await container.initialize_services()
    analyzer = container.dependency_analyzer

    # Simulate code with local imports but missing files
    code_files = {
        "main.py": """
from database import get_db
from models import User
import config
import utils

def main():
    pass
""",
        "utils.py": "def helper(): pass"
    }

    missing_files = analyzer._validate_self_containment(code_files)

    expected_missing = ["database.py", "models.py", "config.py"]
    found_expected = all(missing in missing_files for missing in expected_missing)

    print(f"  Detected missing files: {missing_files}")
    print(f"  Expected: {expected_missing}")
    print(f"  Self-containment detection: {'✅ PASS' if found_expected else '❌ FAIL'}")

    return found_expected


async def test_import_resolution():
    """Test that built-in modules are detected but don't appear in requirements.txt."""
    print("\n🧪 Testing Import Resolution...")

    container = ServiceContainer()
    await container.initialize_services()
    analyzer = container.dependency_analyzer

    # Code with built-in imports that should not require packages
    code = """
import os
import sys
import json
import datetime
import random
import math

def test():
    return os.path.join(sys.path[0], 'file.json')
"""

    dependencies, requirements_txt = analyzer.analyze_project_dependencies({"main.py": code})

    # Built-in modules should be detected as dependencies
    built_in_deps = [dep for dep in dependencies if dep.name in ['os', 'sys', 'json', 'datetime', 'random', 'math']]

    # But they should NOT appear in requirements.txt (only pip packages)
    pip_deps_in_requirements = [line.strip() for line in requirements_txt.split('\n')
                               if line.strip() and not line.startswith('#') and
                               any(dep in line for dep in ['os', 'sys', 'json', 'datetime', 'random', 'math'])]

    built_ins_detected = len(built_in_deps) == 6  # Should detect all 6
    built_ins_not_in_requirements = len(pip_deps_in_requirements) == 0  # Should not be in requirements

    print(f"  Built-in dependencies detected: {[dep.name for dep in built_in_deps]}")
    print(f"  Built-ins in requirements.txt: {pip_deps_in_requirements}")
    print(f"  Import resolution: {'✅ PASS' if built_ins_detected and built_ins_not_in_requirements else '❌ FAIL'}")

    return built_ins_detected and built_ins_not_in_requirements


async def test_pypi_package_mapping():
    """Test that PyPI package names are correctly resolved."""
    print("\n🧪 Testing PyPI Package Mapping...")

    container = ServiceContainer()
    await container.initialize_services()
    analyzer = container.dependency_analyzer

    # Test various import patterns
    test_imports = [
        ("PIL", "pillow"),
        ("cv2", "opencv-python"),
        ("sklearn", "scikit-learn"),
        ("yaml", "pyyaml"),
        ("plotly", "plotly"),
        ("seaborn", "seaborn"),
    ]

    success_count = 0
    for import_name, expected_package in test_imports:
        resolved = analyzer._resolve_import(import_name)
        if resolved == expected_package:
            print(f"  ✅ {import_name} -> {resolved}")
            success_count += 1
        else:
            print(f"  ❌ {import_name} -> {resolved} (expected {expected_package})")

    print(f"PyPI mapping: {success_count}/{len(test_imports)} passed")
    return success_count == len(test_imports)


async def main():
    """Run all robustness tests."""
    print("🔧 ROBUSTNESS ENHANCEMENT VALIDATION")
    print("=" * 50)

    setup_logging(log_level="WARNING")

    tests = [
        ("Dependency Mapping", test_dependency_mapping),
        ("Self-Containment Detection", test_self_containment_detection),
        ("Import Resolution", test_import_resolution),
        ("PyPI Package Mapping", test_pypi_package_mapping),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"  💥 Test '{test_name}' failed with error: {e}")

    print("\n" + "=" * 50)
    print("📊 ROBUSTNESS TEST RESULTS")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    if passed == total:
        print("🎉 All robustness enhancements are working correctly!")
        return 0
    else:
        print("⚠️ Some robustness tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
