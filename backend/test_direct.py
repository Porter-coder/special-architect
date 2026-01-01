"""
Direct test of CodeGenerationService
"""

import asyncio
from src.services.code_generation_service import CodeGenerationService
from src.models.code_generation_request import CodeGenerationRequest

async def test_direct():
    """Test the code generation service directly."""
    print("Testing CodeGenerationService directly...")

    service = CodeGenerationService()
    request = CodeGenerationRequest(user_input="帮我写个贪吃蛇")

    print(f"Created request: {request.request_id}")

    try:
        events = []
        async for event in service.generate_code_stream(request):
            events.append(event)
            print(f"Event: {event}")
            if len(events) > 10:  # Limit to avoid infinite loop
                break

        print("Test completed successfully!")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct())
