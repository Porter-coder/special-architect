#!/usr/bin/env python3
"""
Test Dynamic Import Validation

Tests that the dynamic import validation correctly identifies:
1. Standard library modules (allowed)
2. Declared third-party packages (allowed)
3. Undeclared local imports (blocked)
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.logging_config import setup_logging
from src.services.container import ServiceContainer
from src.services.code_generation_service import CodeGenerationService

setup_logging(log_level="WARNING")


async def test_dynamic_validation():
    """Test dynamic import validation logic."""
    print("🧪 Testing Dynamic Import Validation...")

    container = ServiceContainer()
    await container.initialize_services()
    service = container.code_generation_service

    # Test case 1: Code with only standard library imports (should pass)
    print("\n1. Testing standard library imports...")
    stdlib_code = """
import os
import sys
import json
import math
from pathlib import Path
from datetime import datetime

def main():
    print("Hello from stdlib only")
"""

    requirements_txt = "# AI Code Flow Generated Requirements\n# Auto-generated dependency list\n"
    result1 = service._validate_single_file_delivery({"main.py": stdlib_code}, requirements_txt)
    print(f"   Stdlib validation: {'✅ PASS' if result1['compliant'] else '❌ FAIL'}")
    if not result1['compliant']:
        print(f"   Violations: {result1['violations']}")

    # Test case 2: Code with declared third-party package (should pass)
    print("\n2. Testing declared third-party imports...")
    third_party_code = """
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def main():
    arr = np.array([1, 2, 3])
    print("Third-party packages work")
"""

    requirements_with_deps = """# AI Code Flow Generated Requirements
# Auto-generated dependency list

numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
"""

    result2 = service._validate_single_file_delivery({"main.py": third_party_code}, requirements_with_deps)
    print(f"   Third-party validation: {'✅ PASS' if result2['compliant'] else '❌ FAIL'}")
    if not result2['compliant']:
        print(f"   Violations: {result2['violations']}")

    # Test case 3: Code with undeclared local import (should fail)
    print("\n3. Testing undeclared local imports...")
    local_import_code = """
import os
from my_custom_module import helper
import undeclared_package

def main():
    helper()
    print("Local imports detected")
"""

    result3 = service._validate_single_file_delivery({"main.py": local_import_code}, requirements_txt)
    print(f"   Local import validation: {'✅ PASS (correctly blocked)' if not result3['compliant'] else '❌ FAIL (should have blocked)'}")
    if not result3['compliant']:
        print(f"   Detected violations: {result3['violations']}")

    # Summary
    all_correct = result1['compliant'] and result2['compliant'] and not result3['compliant']
    print(f"\n📊 Dynamic Validation Test: {'✅ ALL CORRECT' if all_correct else '❌ ISSUES FOUND'}")

    return all_correct


async def main():
    """Main test function."""
    success = await test_dynamic_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
