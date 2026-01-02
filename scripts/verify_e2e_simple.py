#!/usr/bin/env python3
"""
Simple E2E Verification Script - Brute Force

This script performs a complete end-to-end test of the code generation system:
Start generation -> Wait blindly (retry on errors) -> Download ZIP.

The script handles server blocking during generation by continuing to wait
when connection errors occur.

Usage:
    python scripts/verify_e2e_simple.py

Dependencies: requests, psutil
"""

import json
import logging
import signal
import subprocess
import sys
import time
import zipfile
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
SERVICE_PORT = 8001
BASE_URL = f"{SERVICE_HOST}:{SERVICE_PORT}"
GENERATE_ENDPOINT = "/api/generate-code"
DOWNLOAD_ENDPOINT_TEMPLATE = "/api/projects/{}/download"

# Test configuration
COMPLEX_PROMPT = "Create a Python GUI Calculator with tkinter. Include addition, subtraction, multiplication, and division operations. Add proper error handling for division by zero. Make the interface user-friendly with clear buttons and display."
DOWNLOAD_FILENAME = "final.zip"

# Timing configuration
MAX_WAIT_TIME = 300  # 5 minutes total
RETRY_INTERVAL = 10  # 10 seconds between attempts
STARTUP_TIMEOUT = 30  # 30 seconds for initial startup

# Process management
uvicorn_process: Optional[subprocess.Popen] = None


class E2ETester:
    """Simple E2E tester that handles blocking I/O gracefully."""

    def __init__(self):
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
        """Start the uvicorn service."""
        logger.info("启动 uvicorn 服务...")

        # Clean up any existing processes
        self.cleanup_port_processes(8001)

        try:
            # Get the backend directory path - make it robust against different working directories
            script_dir = Path(__file__).resolve().parent
            project_root = script_dir.parent
            backend_dir = project_root / "backend"
            venv_python = backend_dir / "backend" / "venv" / "Scripts" / "python.exe"

            if not venv_python.exists():
                logger.error(f"虚拟环境 Python 不存在: {venv_python}")
                logger.error(f"当前工作目录: {Path.cwd()}")
                logger.error(f"脚本目录: {Path(__file__).parent}")
                return False

            # Start uvicorn process
            cmd = [
                str(venv_python),  # Convert to string for subprocess
                "-m", "uvicorn",
                "src.main:app",
                "--host", "0.0.0.0",
                "--port", str(SERVICE_PORT),
                "--log-level", "error"  # Reduce log noise
            ]

            logger.info(f"执行命令: {' '.join(cmd)}")

            self.uvicorn_process = subprocess.Popen(
                cmd,
                cwd=str(backend_dir),
                stdout=subprocess.DEVNULL,  # Suppress stdout
                stderr=subprocess.DEVNULL,  # Suppress stderr
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )

            # Wait for service to be ready
            logger.info("等待服务启动...")
            return self._wait_for_service_ready()

        except Exception as e:
            logger.error(f"启动服务失败: {e}")
            self._cleanup_process()
            return False

    def _wait_for_service_ready(self) -> bool:
        """Wait for service to respond to health check."""
        health_url = f"{BASE_URL}/api/health"
        start_time = time.time()

        while time.time() - start_time < STARTUP_TIMEOUT:
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    logger.info("✅ 服务已就绪")
                    return True
            except requests.RequestException:
                pass

            time.sleep(1)

        logger.error("❌ 服务启动超时")
        return False

    def start_generation(self) -> Optional[str]:
        """Start code generation and return request_id."""
        generate_url = f"{BASE_URL}{GENERATE_ENDPOINT}"

        try:
            logger.info("🚀 启动代码生成...")

            payload = {
                "user_input": COMPLEX_PROMPT
            }

            logger.info(f"发送生成请求: {COMPLEX_PROMPT[:50]}...")
            response = requests.post(generate_url, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                if request_id:
                    logger.info(f"✅ 生成请求已启动，ID: {request_id}")
                    return request_id
                else:
                    logger.error("❌ 响应中缺少 request_id")
            else:
                logger.error(f"❌ 生成请求失败: {response.status_code} - {response.text}")

        except requests.RequestException as e:
            logger.error(f"❌ 生成请求网络错误: {e}")

        return None

    def wait_and_download(self, request_id: str) -> bool:
        """Wait for generation to complete and download the result."""
        download_url = f"{BASE_URL}{DOWNLOAD_ENDPOINT_TEMPLATE.format(request_id)}"

        logger.info("⏳ 开始等待生成完成...")
        logger.info(f"最长等待时间: {MAX_WAIT_TIME} 秒")
        logger.info(f"重试间隔: {RETRY_INTERVAL} 秒")

        start_time = time.time()
        attempt = 0

        while time.time() - start_time < MAX_WAIT_TIME:
            attempt += 1
            elapsed = int(time.time() - start_time)

            try:
                logger.info(f"尝试 #{attempt} (已等待 {elapsed}s/{MAX_WAIT_TIME}s)...")

                response = requests.get(download_url, timeout=10)

                if response.status_code == 200:
                    logger.info("✅ 生成完成！开始下载...")
                    return self._save_and_verify_zip(response.content)

                elif response.status_code == 404:
                    logger.info("⏳ 生成中... (服务器响应但项目未完成)")
                    time.sleep(RETRY_INTERVAL)
                    continue

                else:
                    logger.warning(f"⚠️ 意外状态码: {response.status_code} - {response.text}")
                    time.sleep(RETRY_INTERVAL)
                    continue

            except requests.exceptions.Timeout:
                logger.warning("⚠️ 请求超时 - 服务器可能忙碌，继续等待...")
                time.sleep(RETRY_INTERVAL)
                continue

            except requests.exceptions.ConnectionError:
                logger.warning("⚠️ 连接错误 - 服务器阻塞中，继续等待...")
                time.sleep(RETRY_INTERVAL)
                continue

            except Exception as e:
                logger.warning(f"⚠️ 未知错误: {e} - 继续等待...")
                time.sleep(RETRY_INTERVAL)
                continue

        logger.error(f"❌ 等待超时 ({MAX_WAIT_TIME} 秒)")
        return False

    def _save_and_verify_zip(self, content: bytes) -> bool:
        """Save ZIP content and verify it's valid with main.py."""
        try:
            logger.info(f"保存 ZIP 到: {DOWNLOAD_FILENAME}")

            # Save the ZIP file
            with open(DOWNLOAD_FILENAME, 'wb') as f:
                f.write(content)

            # Verify ZIP format
            with zipfile.ZipFile(DOWNLOAD_FILENAME, 'r') as zip_ref:
                # Check if it's a valid ZIP
                bad_file = zip_ref.testzip()
                if bad_file:
                    logger.error(f"❌ ZIP 文件损坏: {bad_file}")
                    return False

                # Get file list
                file_list = zip_ref.namelist()
                logger.info(f"✅ ZIP 有效，包含 {len(file_list)} 个文件")

                # Check for main.py (anywhere in the structure)
                main_py_files = [f for f in file_list if f.endswith('main.py')]
                if not main_py_files:
                    logger.error("❌ ZIP 不包含 main.py 文件")
                    return False

                main_py_path = main_py_files[0]
                logger.info(f"✅ 找到 main.py: {main_py_path}")

                # Try to read main.py content
                try:
                    with zip_ref.open(main_py_path) as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        logger.info(f"✅ main.py 内容长度: {len(content)} 字符")
                except Exception as e:
                    logger.warning(f"⚠️ 无法读取 main.py 内容: {e}")

                return True

        except zipfile.BadZipFile:
            logger.error("❌ 无效的 ZIP 文件格式")
            return False
        except Exception as e:
            logger.error(f"❌ ZIP 验证失败: {e}")
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

    def run_e2e_test(self) -> bool:
        """Run the complete E2E test."""
        try:
            logger.info("🎯 开始简易版全链路验收测试...")
            logger.info(f"测试提示: {COMPLEX_PROMPT[:50]}...")

            # 1. Start service
            if not self.start_service():
                logger.error("❌ 服务启动失败")
                return False

            # 2. Start generation
            request_id = self.start_generation()
            if not request_id:
                logger.error("❌ 生成启动失败")
                return False

            # 3. Wait and download
            if not self.wait_and_download(request_id):
                logger.error("❌ 下载验证失败")
                return False

            logger.info("🏆 SUCCESS - 全链路测试通过！")
            return True

        except KeyboardInterrupt:
            logger.info("收到中断信号，正在清理...")
            return False
        except Exception as e:
            logger.error(f"测试过程出错: {e}")
            return False
        finally:
            self._cleanup_process()


def main():
    """Main entry point."""
    # Check dependencies
    try:
        import psutil
        import requests
    except ImportError as e:
        logger.error(f"❌ 缺少依赖: {e}")
        logger.error("请运行: pip install psutil requests")
        sys.exit(1)

    # Run the test
    tester = E2ETester()
    success = tester.run_e2e_test()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
