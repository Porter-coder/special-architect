import asyncio
from src.services.code_generation_service import CodeGenerationService
from src.models.code_generation_request import CodeGenerationRequest

async def test():
    service = CodeGenerationService()
    request = CodeGenerationRequest(user_input='帮我写个贪吃蛇')

    print('Testing phase transitions...')
    count = 0
    async for event in service.generate_code_stream(request):
        print(f'Event {count}: {event.get("type")} - phase: {event.get("phase", "no phase")}')
        count += 1
        if count > 10:  # Limit output
            break

if __name__ == "__main__":
    asyncio.run(test())
