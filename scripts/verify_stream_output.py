#!/usr/bin/env python3
"""
Automated Stream Verification Script

This script automatically manages service lifecycle and captures stream output for verification.
It handles process cleanup, service startup, stream capture, and result validation.

Usage:
    python scripts/verify_stream_output.py [--id REQUEST_ID]

Arguments:
    --id REQUEST_ID: Optional existing request ID to reuse for streaming
"""

import argparse
import json
import logging
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import psutil
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SERVICE_HOST = "http://localhost"
SERVICE_PORT = 8001  # Use 8001 as specified in requirements
HEALTH_ENDPOINT = "/api/health"
GENERATE_ENDPOINT = "/api/generate-code"
STREAM_ENDPOINT_TEMPLATE = "/api/generate-code/{}/stream"

# Timeouts and retries
HEALTH_CHECK_TIMEOUT = 10  # seconds
HEALTH_CHECK_RETRIES = 10
STREAM_TIMEOUT = 60  # seconds

# Output file
RESULT_FILE = "verify_stream_result.txt"


class StreamVerifier:
    """Automated stream verification handler."""

    def __init__(self, request_id: Optional[str] = None):
        self.request_id = request_id
        self.base_url = f"{SERVICE_HOST}:{SERVICE_PORT}"
        self.uvicorn_process: Optional[subprocess.Popen] = None

    def cleanup_port_processes(self, port: int) -> None:
        """Kill any processes using the specified port."""
        logger.info(f"清理端口 {port} 上的进程...")

        try:
            # Find processes using the port
            for conn in psutil.net_connections():
                if conn.status == 'LISTEN' and conn.laddr.port == port:
                    try:
                        process = psutil.Process(conn.pid)
                        logger.info(f"终止进程: {process.name()} (PID: {conn.pid})")
                        process.terminate()

                        # Wait for graceful termination
                        try:
                            process.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            logger.warning(f"强制终止进程: {conn.pid}")
                            process.kill()

                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        logger.warning(f"无法终止进程 {conn.pid}: {e}")

        except Exception as e:
            logger.error(f"清理端口进程失败: {e}")

    def start_service(self) -> bool:
        """Start the uvicorn service and wait for it to be ready."""
        logger.info("启动 uvicorn 服务...")

        # Clean up any existing processes on the ports
        self.cleanup_port_processes(8000)
        self.cleanup_port_processes(8001)

        try:
            # Start uvicorn process
            cmd = [
                sys.executable, "-m", "uvicorn",
                "src.main:app",
                "--host", "0.0.0.0",
                "--port", str(SERVICE_PORT),
                "--log-level", "info"
            ]

            logger.info(f"执行命令: {' '.join(cmd)}")

            self.uvicorn_process = subprocess.Popen(
                cmd,
                cwd=Path(__file__).parent.parent / "backend",  # Backend directory
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for service to be ready
            logger.info("等待服务启动...")
            return self._wait_for_service_ready()

        except Exception as e:
            logger.error(f"启动服务失败: {e}")
            self._cleanup_process()
            return False

    def _wait_for_service_ready(self) -> bool:
        """Poll the health endpoint until service is ready."""
        health_url = f"{self.base_url}{HEALTH_ENDPOINT}"

        for attempt in range(HEALTH_CHECK_RETRIES):
            try:
                logger.info(f"健康检查 (尝试 {attempt + 1}/{HEALTH_CHECK_RETRIES})...")

                response = requests.get(
                    health_url,
                    timeout=HEALTH_CHECK_TIMEOUT
                )

                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("status") in ["healthy", "degraded"]:
                        logger.info("✅ 服务已就绪")
                        return True

                logger.warning(f"服务未就绪，状态码: {response.status_code}")

            except requests.RequestException as e:
                logger.warning(f"健康检查失败: {e}")

            time.sleep(2)

        logger.error("❌ 服务启动超时")
        return False

    def create_generation_request(self) -> Optional[str]:
        """Create a new code generation request."""
        generate_url = f"{self.base_url}{GENERATE_ENDPOINT}"

        try:
            logger.info("创建新的代码生成请求...")

            payload = {
                "user_input": "Create a simple Python hello world program"
            }

            response = requests.post(
                generate_url,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                logger.info(f"✅ 请求创建成功: {request_id}")
                return request_id
            else:
                logger.error(f"❌ 创建请求失败: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            logger.error(f"创建请求失败: {e}")

        return None

    def capture_stream_output(self, request_id: str) -> bool:
        """Capture stream output to file."""
        stream_url = f"{self.base_url}{STREAM_ENDPOINT_TEMPLATE.format(request_id)}"

        logger.info(f"连接流式接口: {stream_url}")
        logger.info(f"输出将保存到: {RESULT_FILE}")

        try:
            # Clear result file
            with open(RESULT_FILE, 'w', encoding='utf-8') as f:
                f.write("")

            # Connect to stream with timeout
            response = requests.get(
                stream_url,
                stream=True,
                timeout=STREAM_TIMEOUT
            )

            if response.status_code != 200:
                logger.error(f"❌ 流式连接失败: {response.status_code}")
                logger.error(f"响应内容: {response.text[:500]}...")
                return False

            logger.info("✅ 流式连接成功，开始捕获数据...")

            # Capture SSE events
            captured_data = []
            start_time = time.time()
            current_event = {}
            content_buffer = ""

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()

                    # Parse SSE format
                    if line_str.startswith('event: '):
                        # Save previous event if exists
                        if current_event and 'data' in current_event:
                            try:
                                json_data = json.loads(current_event['data'])
                                captured_data.append(json_data)

                                # Write to file immediately
                                with open(RESULT_FILE, 'a', encoding='utf-8') as f:
                                    f.write(f"{json.dumps(json_data, ensure_ascii=False)}\n")

                                logger.info(f"收到事件 {current_event.get('event', 'unknown')}: {current_event['data'][:100]}...")

                            except json.JSONDecodeError as e:
                                logger.warning(f"JSON解析失败: {e}, 数据: {current_event['data'][:200]}...")

                        # Start new event
                        current_event = {'event': line_str[7:]}  # Remove 'event: '

                    elif line_str.startswith('data: '):
                        # Accumulate data lines
                        data_content = line_str[6:]  # Remove 'data: '
                        if 'data' not in current_event:
                            current_event['data'] = data_content
                        else:
                            current_event['data'] += data_content

                    elif line_str == '':
                        # Empty line indicates end of event
                        if current_event and 'data' in current_event:
                            try:
                                json_data = json.loads(current_event['data'])
                                captured_data.append(json_data)

                                # Write to file immediately
                                with open(RESULT_FILE, 'a', encoding='utf-8') as f:
                                    f.write(f"{json.dumps(json_data, ensure_ascii=False)}\n")

                                logger.info(f"收到事件 {current_event.get('event', 'unknown')}: {current_event['data'][:100]}...")

                            except json.JSONDecodeError as e:
                                logger.warning(f"JSON解析失败: {e}, 数据: {current_event['data'][:200]}...")

                        current_event = {}

                # Check for timeout
                if time.time() - start_time > STREAM_TIMEOUT:
                    logger.warning(f"流式输出超时 ({STREAM_TIMEOUT}s)")
                    break

            # Handle any remaining event
            if current_event and 'data' in current_event:
                try:
                    json_data = json.loads(current_event['data'])
                    captured_data.append(json_data)

                    with open(RESULT_FILE, 'a', encoding='utf-8') as f:
                        f.write(f"{json.dumps(json_data, ensure_ascii=False)}\n")

                    logger.info(f"收到最终事件 {current_event.get('event', 'unknown')}: {current_event['data'][:100]}...")

                except json.JSONDecodeError as e:
                    logger.warning(f"最终事件JSON解析失败: {e}")

            logger.info(f"流式捕获完成，共收到 {len(captured_data)} 个数据块")

            # Check if we got any meaningful data
            return len(captured_data) > 0

        except requests.RequestException as e:
            logger.error(f"流式连接错误: {e}")
            return False

    def verify_results(self) -> bool:
        """Verify that the captured results contain expected content."""
        logger.info("验证结果文件...")

        try:
            with open(RESULT_FILE, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                logger.error("❌ 结果文件为空")
                return False

            # Check for expected JSON fields
            checks = [
                '"phase":' in content,
                '"content":' in content,
                '"implement"' in content or '"phase"' in content
            ]

            passed_checks = sum(checks)
            total_checks = len(checks)

            logger.info(f"验证结果: {passed_checks}/{total_checks} 通过")

            if all(checks):
                logger.info("✅ 验证通过 - 找到关键字段")
                return True
            else:
                logger.warning("❌ 验证失败 - 缺少关键字段")
                logger.info(f"文件内容预览: {content[:500]}...")
                return False

        except FileNotFoundError:
            logger.error("❌ 结果文件不存在")
            return False
        except Exception as e:
            logger.error(f"验证失败: {e}")
            return False

    def _cleanup_process(self) -> None:
        """Clean up the uvicorn process."""
        if self.uvicorn_process and self.uvicorn_process.poll() is None:
            logger.info("清理 uvicorn 进程...")
            try:
                self.uvicorn_process.terminate()
                try:
                    self.uvicorn_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("强制终止 uvicorn 进程")
                    self.uvicorn_process.kill()
            except Exception as e:
                logger.error(f"清理进程失败: {e}")

    def run_verification(self) -> bool:
        """Run the complete verification process."""
        try:
            logger.info("🚀 开始自动化流式验证...")

            # 1. Start service
            if not self.start_service():
                logger.error("❌ 服务启动失败")
                return False

            # 2. Get or create request ID
            if self.request_id:
                logger.info(f"使用提供的请求ID: {self.request_id}")
                request_id = self.request_id
            else:
                logger.info("创建新的代码生成请求...")
                request_id = self.create_generation_request()
                if not request_id:
                    logger.error("❌ 创建请求失败")
                    return False

            # 3. Capture stream output
            if not self.capture_stream_output(request_id):
                logger.error("❌ 流式输出捕获失败")
                return False

            # 4. Verify results
            if not self.verify_results():
                logger.error("❌ 结果验证失败")
                return False

            logger.info("🎉 验证成功完成！")
            return True

        except KeyboardInterrupt:
            logger.info("收到中断信号，正在清理...")
            return False
        except Exception as e:
            logger.error(f"验证过程出错: {e}")
            return False
        finally:
            self._cleanup_process()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Automated Stream Verification Script")
    parser.add_argument(
        "--id",
        type=str,
        help="Optional existing request ID to reuse for streaming"
    )

    args = parser.parse_args()

    # Check if psutil is available
    try:
        import psutil
    except ImportError:
        logger.error("❌ 需要安装 psutil: pip install psutil")
        sys.exit(1)

    # Check if requests is available
    try:
        import requests
    except ImportError:
        logger.error("❌ 需要安装 requests: pip install requests")
        sys.exit(1)

    # Run verification
    verifier = StreamVerifier(request_id=args.id)
    success = verifier.run_verification()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
