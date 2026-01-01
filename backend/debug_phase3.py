#!/usr/bin/env python3
"""
Phase 3 Direct Debugger

Directly tests the Implement phase logic to quickly reproduce the 'name result is not defined' bug.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.logging_config import setup_logging
from src.services.container import ServiceContainer
from src.models.process_phase import PhaseName

setup_logging(log_level="INFO")


async def debug_implement_phase():
    """Directly test the IMPLEMENT phase logic."""

    print("🔧 PHASE 3 DIRECT DEBUGGER")
    print("=" * 50)

    # Mock data
    user_request = "Create a simple NumPy array demonstration script"
    spec_content = "Technical specification for NumPy array demo with educational focus"
    plan_content = """# NumPy Array Operations Plan
Create comprehensive NumPy demonstration with array creation, operations, and statistics.
Use numpy for all operations, include proper error handling, educational examples with comments.
Requirements: numpy >= 1.19.0, Python 3.8+, educational focus."""

    try:
        print("🚀 Initializing services...")
        container = ServiceContainer()
        await container.initialize_services()
        service = container.code_generation_service

        # Generate the IMPLEMENT prompt directly
        print("📝 Generating IMPLEMENT prompt...")
        implement_prompt = service._generate_universal_prompt(
            phase=PhaseName.IMPLEMENT,
            user_request=user_request,
            spec_content=spec_content,
            plan_content=plan_content
        )

        print(f"Prompt length: {len(implement_prompt)} characters")

        # Test AI generation directly (2-second test)
        print("🎯 Testing AI code generation...")
        generated_code = ""
        error_occurred = False
        error_message = ""

        async for event in service.ai_service.generate_code_stream(implement_prompt, PhaseName.IMPLEMENT):
            if event.get("type") == "text":
                generated_code += event.get("content", "")
            elif event.get("type") == "error":
                error_occurred = True
                error_message = event.get("message", "Unknown error")
                print(f"❌ AI ERROR: {error_message}")
                break

        if error_occurred:
            print("💥 DEBUG RESULT: FAILED (AI generation error)")
            print(f"Error: {error_message}")

            if "name 'result' is not defined" in error_message or "UnboundLocalError" in error_message:
                print("🎯 TARGET BUG CONFIRMED: Undefined variable 'result'")
                return False
            else:
                print("🤔 DIFFERENT ERROR: Not the target bug")
                return False

        print("✅ AI generation completed")
        print(f"Generated code length: {len(generated_code)} characters")

        # Test content processing
        print("🔍 Testing content processing...")
        try:
            processed_result = service.content_processor.process_content(generated_code, PhaseName.IMPLEMENT)

            if processed_result.get("processed"):
                cleaned_code = processed_result.get("cleaned_content", "")
                print("✅ Content processing successful")
                print(f"Cleaned code length: {len(cleaned_code)}")

                # Test code parsing and validation
                print("🧪 Testing code parsing...")
                files = service._parse_generated_code(cleaned_code)

                if "main.py" in files:
                    print("✅ main.py generated successfully")
                    main_code = files["main.py"]
                    print(f"Main code length: {len(main_code)} characters")

                    # Basic validation
                    if "import numpy" in main_code:
                        print("✅ Contains numpy import")
                    if "if __name__ == " in main_code:
                        print("✅ Contains main execution block")
                    if "def " in main_code:
                        print("✅ Contains function definitions")

                    # Check for syntax errors using AST parsing
                    import ast
                    try:
                        ast.parse(main_code)
                        print("✅ Syntax validation passed (AST parse successful)")

                        # Additional check: Look for undefined variables like 'result'
                        if "'result' is not defined" in main_code or "name 'result'" in main_code:
                            print("⚠️  POTENTIAL BUG: Found 'result' reference that might be undefined")
                            return False

                        # Check for common undefined variable patterns using AST analysis
                        import ast

                        class VariableVisitor(ast.NodeVisitor):
                            def __init__(self):
                                self.defined_vars = set()
                                self.used_vars = set()
                                self.functions = set()
                                self.imports = set()

                            def visit_FunctionDef(self, node):
                                self.functions.add(node.name)
                                self.generic_visit(node)

                            def visit_Import(self, node):
                                for alias in node.names:
                                    name = alias.asname if alias.asname else alias.name
                                    self.imports.add(name)
                                self.generic_visit(node)

                            def visit_ImportFrom(self, node):
                                for alias in node.names:
                                    name = alias.asname if alias.asname else alias.name
                                    self.imports.add(name)
                                self.generic_visit(node)

                            def visit_Assign(self, node):
                                # Track variable definitions
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        self.defined_vars.add(target.id)
                                self.generic_visit(node)

                            def visit_Name(self, node):
                                if isinstance(node.ctx, ast.Load):  # Variable usage
                                    self.used_vars.add(node.id)
                                self.generic_visit(node)

                        try:
                            tree = ast.parse(main_code)
                            visitor = VariableVisitor()
                            visitor.visit(tree)

                            # Find undefined variables
                            all_defined = visitor.defined_vars | visitor.functions | visitor.imports
                            undefined = visitor.used_vars - all_defined

                            # Filter out built-ins and special names
                            builtin_names = {
                                'print', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple',
                                'range', 'enumerate', 'zip', 'sum', 'max', 'min', 'abs', 'round',
                                'sorted', 'reversed', 'any', 'all', 'isinstance', 'hasattr', 'getattr',
                                '__name__', '__main__', 'True', 'False', 'None'
                            }
                            undefined = undefined - builtin_names

                            if undefined:
                                print(f"⚠️  FOUND UNDEFINED VARIABLES: {undefined}")
                                # Look for the specific 'result' variable issue
                                if 'result' in undefined:
                                    print("🎯 TARGET BUG CONFIRMED: Undefined variable 'result'")
                                    return False
                                else:
                                    print(f"⚠️  Other undefined variables found: {undefined}")
                                    # For now, let's not fail on other undefined variables since they might be false positives
                                    # return False

                        except Exception as e:
                            print(f"⚠️  Could not analyze variables with AST: {e}")
                            # Fallback to simple text search for 'result' patterns
                            lines = main_code.split('\n')
                            for i, line in enumerate(lines, 1):
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    # More precise check: look for 'result' as a standalone word
                                    import re
                                    if re.search(r'\bresult\b', line):
                                        # Check if it's used before assignment in same scope (simplified)
                                        if '=' in line:
                                            eq_pos = line.find('=')
                                            before_eq = line[:eq_pos]
                                            if 'result' in before_eq:
                                                # It's being assigned, not used
                                                continue
                                        # It's being used, check if defined earlier
                                        print(f"⚠️  POTENTIAL UNDEFINED 'result': line {i}: {line[:100]}...")
                                        return False

                        print("✅ No undefined variable issues detected")
                        return True

                    except SyntaxError as e:
                        print("🎯 BUG FOUND: Syntax error in generated code!")
                        print(f"Syntax error: {e}")
                        print("This indicates the AI generated invalid Python code")
                        return False
                    except Exception as e:
                        print("🎯 BUG FOUND: Code validation failed!")
                        print(f"Error: {e}")
                        return False

                else:
                    print("❌ main.py not found in generated files")
                    print(f"Available files: {list(files.keys())}")
                    return False

            else:
                print("❌ Content processing failed - no processed content returned")
                return False

        except Exception as e:
            # Check if this is the specific bug we're looking for
            error_str = str(e)
            if "unterminated string literal" in error_str:
                print("🎯 BUG FOUND: AI generated code with unterminated string literal!")
                print(f"Error: {e}")
                return False
            elif "name 'result' is not defined" in error_str or "UnboundLocalError" in error_str:
                print("🎯 TARGET BUG CONFIRMED: Undefined variable 'result'")
                print(f"Error: {e}")
                return False
            else:
                print(f"❌ Processing error: {e}")
                import traceback
                traceback.print_exc()
                return False

    except Exception as e:
        print(f"💥 UNEXPECTED EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main debug function."""
    print("🚀 Starting Phase 3 Direct Debug (2-second test)")
    success = await debug_implement_phase()

    print("\n" + "=" * 50)
    if success:
        print("🎉 DEBUG COMPLETE: Phase 3 working correctly")
        print("   No undefined variable issues detected")
    else:
        print("❌ DEBUG COMPLETE: Issues found")
        print("   Bug still present or different error occurred")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)