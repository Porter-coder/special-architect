"""
Backend SSE Test Script for Snake Game Generation

This script tests the complete backend flow:
1. POST /generate - Start code generation
2. GET /generate/{id}/stream - Stream progress updates
3. GET /generate/{id}/files - Retrieve generated files

Usage:
    python verify_snake_backend.py

Requirements:
    pip install httpx
"""

import httpx
import asyncio
import json
import sys
from typing import Optional

BASE_URL = "http://127.0.0.1:8000/api"


async def main():
    """Main test function."""
    print("🐍 Snake Backend SSE Test Script")
    print("=" * 50)

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            # 1. Start Generation
            print("\n🚀 Step 1: Starting code generation...")
            print("Sending request: '帮我写个贪吃蛇'...")

            resp = await client.post(
                f"{BASE_URL}/generate",
                json={"user_input": "帮我写个贪吃蛇"}
            )

            if resp.status_code != 200:  # 200 OK for synchronous response
                print(f"❌ Error starting generation: {resp.status_code}")
                print(f"Response: {resp.text}")
                return

            response_data = resp.json()
            req_id = response_data["request_id"]
            print(f"✅ Generation started! Request ID: {req_id}")
            print(f"Message: {response_data.get('message', 'No message')}")

            # 2. Listen to Stream
            print("\n🎧 Step 2: Listening to SSE stream...")
            print("Waiting for phase updates and code generation...")

            phases_received = []
            thinking_content = []
            text_content = []

            try:
                async with client.stream("GET", f"{BASE_URL}/generate/{req_id}/stream") as response:
                    if response.status_code != 200:
                        print(f"❌ Stream connection failed: {response.status_code}")
                        print(f"Response: {response.text}")
                        return

                    print("📡 Connected to stream, waiting for events...")

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if not data_str:
                                continue

                            try:
                                data = json.loads(data_str)

                                # Handle different event types
                                if data.get("event") == "connected":
                                    print("🔗 Connected to generation stream")

                                elif data.get("event") == "phase":
                                    phase_data = data.get("data", {})
                                    phase = phase_data.get("phase")
                                    message = phase_data.get("message", "")
                                    phases_received.append(phase)
                                    print(f"\n📦 PHASE: {phase.upper()} - {message}")

                                elif data.get("event") == "thinking":
                                    thinking = data.get("data", "")
                                    thinking_content.append(thinking)
                                    print(f"🤔 Thinking: {thinking[:100]}{'...' if len(thinking) > 100 else ''}")

                                elif data.get("event") == "complete":
                                    complete_data = data.get("data", {})
                                    project_id = complete_data.get("project_id")
                                    main_file = complete_data.get("main_file")
                                    files_count = complete_data.get("files_count", 0)
                                    print("\n✅ GENERATION COMPLETE!")
                                    print(f"   Project ID: {project_id}")
                                    print(f"   Main File: {main_file}")
                                    print(f"   Files Generated: {files_count}")
                                    break

                                elif data.get("event") == "error":
                                    error_msg = data.get("data", "Unknown error")
                                    print(f"❌ Error during generation: {error_msg}")
                                    break

                                # Handle direct event types (alternative format)
                                elif "phase" in data:
                                    phases_received.append(data["phase"])
                                    print(f"\n📦 PHASE: {data['phase'].upper()} - {data.get('message', '')}")

                                elif "type" in data:
                                    if data["type"] == "thinking":
                                        content = data.get("content", "")
                                        thinking_content.append(content)
                                        print(f"🤔 {content[:100]}{'...' if len(content) > 100 else ''}")
                                    elif data["type"] == "text":
                                        content = data.get("content", "")
                                        text_content.append(content)
                                        print(f"📝 {content[:100]}{'...' if len(content) > 100 else ''}")

                            except json.JSONDecodeError:
                                # Handle non-JSON SSE messages (plain text)
                                if data_str.startswith("已连接到请求"):
                                    print("🔗 Connected to generation stream")
                                elif "PHASE:" in data_str or "阶段" in data_str:
                                    print(f"📦 {data_str}")
                                    # Extract phase name if possible
                                    if "specify" in data_str.lower():
                                        phases_received.append("specify")
                                    elif "plan" in data_str.lower():
                                        phases_received.append("plan")
                                    elif "implement" in data_str.lower():
                                        phases_received.append("implement")
                                elif data_str.startswith("✅") or "完成" in data_str:
                                    print(f"✅ {data_str}")
                                    break
                                elif data_str.startswith("❌") or "错误" in data_str:
                                    print(f"❌ {data_str}")
                                    break
                                else:
                                    # Print other text messages
                                    print(f"📝 {data_str[:100]}{'...' if len(data_str) > 100 else ''}")
                                continue
                            except Exception as e:
                                print(f"⚠️  Error processing SSE data: {e}")
                                continue

            except Exception as e:
                print(f"❌ Stream connection error: {e}")
                return

            print(f"\n📊 Stream Summary:")
            print(f"   Phases received: {phases_received}")
            print(f"   Thinking content: {len(thinking_content)} chunks")
            print(f"   Text content: {len(text_content)} chunks")

            # 3. Check Files
            print("\n📂 Step 3: Retrieving generated files...")

            # Small delay to ensure file processing is complete
            await asyncio.sleep(1)

            resp = await client.get(f"{BASE_URL}/generate/{req_id}/files")

            if resp.status_code == 200:
                files_data = resp.json()
                print("✅ Files retrieved successfully!")

                project_name = files_data.get("project_name")
                main_file = files_data.get("main_file")
                files = files_data.get("files", [])

                print(f"📁 Project: {project_name}")
                print(f"🎯 Main File: {main_file}")
                print(f"📄 Total Files: {len(files)}")

                # Show file list
                print("\n📋 Generated Files:")
                for i, file_info in enumerate(files, 1):
                    path = file_info.get("path", "unknown")
                    encoding = file_info.get("encoding", "unknown")
                    content_preview = file_info.get("content", "")[:100]
                    print(f"   {i}. {path} ({encoding})")
                    if content_preview:
                        print(f"      Preview: {content_preview}{'...' if len(file_info.get('content', '')) > 100 else ''}")

                # Basic validation
                print("\n🔍 Validation:")
                has_main_py = any(f.get("path") == "main.py" for f in files)
                has_requirements = any("requirements" in f.get("path", "") for f in files)
                has_readme = any("readme" in f.get("path", "").lower() for f in files)

                print(f"   ✅ main.py present: {has_main_py}")
                print(f"   ✅ requirements.txt present: {has_requirements}")
                print(f"   ✅ README present: {has_readme}")

                if has_main_py and has_requirements:
                    print("\n🎉 TEST PASSED: Snake game generation successful!")
                    print("   The backend can generate working Snake game code.")
                else:
                    print("\n⚠️  TEST INCOMPLETE: Missing expected files")

            elif resp.status_code == 425:  # Too Early
                print("⏳ Files still processing, please wait...")
            else:
                print(f"❌ Failed to retrieve files: {resp.status_code}")
                print(f"Response: {resp.text}")

        except httpx.TimeoutException:
            print("❌ Request timed out. Is the backend server running?")
            print("   Make sure to start the server with: python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        except httpx.ConnectError:
            print("❌ Cannot connect to backend server.")
            print("   Make sure the server is running on http://127.0.0.1:8000")
            print("   Start with: python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("🐍 Starting Snake Backend Verification...")
    asyncio.run(main())
