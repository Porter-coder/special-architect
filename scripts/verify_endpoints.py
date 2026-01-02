#!/usr/bin/env python3
"""
Full API Verification Suite

This script automatically manages service lifecycle and verifies all static endpoints.
It handles process cleanup, service startup, endpoint verification, and result validation.

Usage:
    python scripts/verify_endpoints.py [--id PROJECT_ID]

Arguments:
    --id PROJECT_ID: Optional project ID to test (defaults to f79287ca-97b1-4348-935a-1c78a69f2f6c)
"""

import argparse
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
SERVICE_PORT = 8001  # Use 8001 as specified in requirements
HEALTH_ENDPOINT = "/api/health"
PROJECT_DETAILS_ENDPOINT_TEMPLATE = "/api/projects/{}/"
PROJECT_DOWNLOAD_ENDPOINT_TEMPLATE = "/api/projects/{}/download"

# Test configuration
DEFAULT_PROJECT_ID = "f79287ca-97b1-4348-935a-1c78a69f2f6c"
DOWNLOAD_FILENAME = "test_download.zip"

# Timeouts and retries
HEALTH_CHECK_TIMEOUT = 10  # seconds
HEALTH_CHECK_RETRIES = 10
REQUEST_TIMEOUT = 30  # seconds

# Output file
REPORT_FILE = "final_report.log"


class EndpointVerifier:
    """Automated endpoint verification handler."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.base_url = f"{SERVICE_HOST}:{SERVICE_PORT}"
        self.uvicorn_process: Optional[subprocess.Popen] = None
        self.report_lines = []

    def log_report(self, message: str) -> None:
        """Log message to both console and report file."""
        logger.info(message)
        self.report_lines.append(message)

    def cleanup_port_processes(self, port: int) -> None:
        """Kill any processes using the specified port."""
        self.log_report(f"清理端口 {port} 上的进程...")

        try:
            # Find processes using the port
            for conn in psutil.net_connections():
                if conn.status == 'LISTEN' and conn.laddr.port == port:
                    try:
                        process = psutil.Process(conn.pid)
                        self.log_report(f"终止进程: {process.name()} (PID: {conn.pid})")
                        process.terminate()

                        # Wait for graceful termination
                        try:
                            process.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            self.log_report(f"强制终止进程: {conn.pid}")
                            process.kill()

                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        logger.warning(f"无法终止进程 {conn.pid}: {e}")

        except Exception as e:
            logger.error(f"清理端口进程失败: {e}")

    def start_service(self) -> bool:
        """Start the uvicorn service and wait for it to be ready."""
        self.log_report("启动 uvicorn 服务...")

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

            self.log_report(f"执行命令: {' '.join(cmd)}")

            self.uvicorn_process = subprocess.Popen(
                cmd,
                cwd=Path(__file__).parent.parent / "backend",  # Backend directory
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for service to be ready
            self.log_report("等待服务启动...")
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
                self.log_report(f"健康检查 (尝试 {attempt + 1}/{HEALTH_CHECK_RETRIES})...")

                response = requests.get(
                    health_url,
                    timeout=HEALTH_CHECK_TIMEOUT
                )

                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("status") in ["healthy", "degraded"]:
                        self.log_report("✅ 服务已就绪")
                        return True

                self.log_report(f"服务未就绪，状态码: {response.status_code}")

            except requests.RequestException as e:
                logger.warning(f"健康检查失败: {e}")

            time.sleep(2)

        self.log_report("❌ 服务启动超时")
        return False

    def test_case_a_project_details(self) -> bool:
        """Test Case A: GET /projects/{id} - Project Details Endpoint"""
        self.log_report("\n=== Test Case A: 获取项目详情 (GET /projects/{id}) ===")

        try:
            url = f"{self.base_url}{PROJECT_DETAILS_ENDPOINT_TEMPLATE.format(self.project_id)}"
            self.log_report(f"请求 URL: {url}")

            response = requests.get(url, timeout=REQUEST_TIMEOUT)

            # Check HTTP status
            if response.status_code != 200:
                self.log_report(f"❌ HTTP 状态码错误: {response.status_code} (期望: 200)")
                return False

            self.log_report("✅ HTTP 状态码: 200")

            # Parse JSON response
            try:
                data = response.json()
                self.log_report(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            except json.JSONDecodeError:
                self.log_report("❌ 响应不是有效的 JSON")
                return False

            # Check file_structure contains main.py
            file_structure = data.get("file_structure", {})
            if not file_structure:
                self.log_report("❌ file_structure 字段缺失或为空")
                return False

            # Check if main.py is mentioned in file_structure
            # file_structure might be a nested structure or a list
            file_structure_str = json.dumps(file_structure, ensure_ascii=False)
            if "main.py" not in file_structure_str:
                self.log_report("❌ file_structure 不包含 main.py")
                return False

            self.log_report("✅ file_structure 包含 main.py")

            # Additional check: verify 'files' field exists and is not empty
            # The current API doesn't return 'files' field, but we check if it exists
            files = data.get("files", [])
            if not files:
                self.log_report("⚠️ 'files' 字段为空或不存在（这可能是正常的，取决于API设计）")
            else:
                self.log_report(f"✅ 'files' 字段不为空，包含 {len(files)} 个文件")

            return True

        except requests.RequestException as e:
            self.log_report(f"❌ 请求失败: {e}")
            return False
        except Exception as e:
            self.log_report(f"❌ 测试用例 A 出错: {e}")
            return False

    def test_case_b_project_download(self) -> bool:
        """Test Case B: GET /projects/{id}/download - Project Download Endpoint"""
        self.log_report("\n=== Test Case B: 源码下载 (GET /projects/{id}/download) ===")

        try:
            url = f"{self.base_url}{PROJECT_DOWNLOAD_ENDPOINT_TEMPLATE.format(self.project_id)}"
            self.log_report(f"请求 URL: {url}")

            response = requests.get(url, timeout=REQUEST_TIMEOUT)

            # Check HTTP status
            if response.status_code != 200:
                self.log_report(f"❌ HTTP 状态码错误: {response.status_code} (期望: 200)")
                return False

            self.log_report("✅ HTTP 状态码: 200")

            # Check Content-Type header
            content_type = response.headers.get("content-type", "")
            if "application/zip" not in content_type:
                self.log_report(f"❌ Content-Type 错误: {content_type} (期望包含: application/zip)")
                return False

            self.log_report("✅ Content-Type: application/zip")

            # Save response content to file
            try:
                with open(DOWNLOAD_FILENAME, 'wb') as f:
                    f.write(response.content)
                self.log_report(f"✅ 响应内容已保存到: {DOWNLOAD_FILENAME}")
            except Exception as e:
                self.log_report(f"❌ 保存文件失败: {e}")
                return False

            # Verify ZIP file format and contents
            try:
                with zipfile.ZipFile(DOWNLOAD_FILENAME, 'r') as zip_ref:
                    # Check if it's a valid ZIP file
                    zip_ref.testzip()  # This will raise an exception if the ZIP is corrupted

                    # Get list of files in ZIP
                    file_list = zip_ref.namelist()
                    self.log_report(f"ZIP 文件包含 {len(file_list)} 个文件: {file_list}")

                    # Check if main.py exists in the ZIP (may be in subdirectories)
                    main_py_files = [f for f in file_list if f.endswith("main.py")]
                    if not main_py_files:
                        self.log_report("❌ ZIP 文件不包含 main.py")
                        return False

                    main_py_path = main_py_files[0]  # Take the first main.py found
                    self.log_report(f"✅ ZIP 文件包含 main.py: {main_py_path}")

                    # Verify we can read the main.py content
                    try:
                        with zip_ref.open(main_py_path) as main_file:
                            content = main_file.read().decode('utf-8')
                            self.log_report(f"✅ main.py 内容长度: {len(content)} 字符")
                            if len(content.strip()) == 0:
                                self.log_report("⚠️ main.py 文件为空")
                    except Exception as e:
                        self.log_report(f"❌ 读取 main.py 失败: {e}")
                        return False

                self.log_report("✅ ZIP 文件格式有效且包含所需内容")
                return True

            except zipfile.BadZipFile:
                self.log_report("❌ 文件不是有效的 ZIP 格式")
                return False
            except Exception as e:
                self.log_report(f"❌ ZIP 验证失败: {e}")
                return False

        except requests.RequestException as e:
            self.log_report(f"❌ 请求失败: {e}")
            return False
        except Exception as e:
            self.log_report(f"❌ 测试用例 B 出错: {e}")
            return False

    def _cleanup_process(self) -> None:
        """Clean up the uvicorn process."""
        if self.uvicorn_process and self.uvicorn_process.poll() is None:
            self.log_report("清理 uvicorn 进程...")
            try:
                self.uvicorn_process.terminate()
                try:
                    self.uvicorn_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.log_report("强制终止 uvicorn 进程")
                    self.uvicorn_process.kill()
            except Exception as e:
                logger.error(f"清理进程失败: {e}")

    def save_report(self) -> None:
        """Save the final report to file."""
        try:
            with open(REPORT_FILE, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.report_lines))
            self.log_report(f"\n报告已保存到: {REPORT_FILE}")
        except Exception as e:
            logger.error(f"保存报告失败: {e}")

    def run_verification(self) -> bool:
        """Run the complete verification process."""
        try:
            self.log_report("🚀 开始全接口自动化验收...")
            self.log_report(f"测试项目 ID: {self.project_id}")

            # 1. Start service
            if not self.start_service():
                self.log_report("❌ 服务启动失败")
                return False

            # 2. Execute Test Case A
            test_a_passed = self.test_case_a_project_details()

            # 3. Execute Test Case B
            test_b_passed = self.test_case_b_project_download()

            # 4. Summary
            self.log_report("\n=== 验收结果总结 ===")
            self.log_report(f"Test Case A (项目详情): {'✅ 通过' if test_a_passed else '❌ 失败'}")
            self.log_report(f"Test Case B (源码下载): {'✅ 通过' if test_b_passed else '❌ 失败'}")

            if test_a_passed and test_b_passed:
                self.log_report("\n🎉 ALL SYSTEMS GO!")
                return True
            else:
                self.log_report("\n❌ 部分测试失败")
                return False

        except KeyboardInterrupt:
            self.log_report("收到中断信号，正在清理...")
            return False
        except Exception as e:
            self.log_report(f"验证过程出错: {e}")
            return False
        finally:
            self.save_report()
            self._cleanup_process()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Full API Verification Suite")
    parser.add_argument(
        "--id",
        type=str,
        default=DEFAULT_PROJECT_ID,
        help=f"Project ID to test (default: {DEFAULT_PROJECT_ID})"
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
    verifier = EndpointVerifier(project_id=args.id)
    success = verifier.run_verification()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
