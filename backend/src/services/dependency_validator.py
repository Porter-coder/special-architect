"""
Dependency Validator Service

Validates Python package dependencies by checking against PyPI mirrors.
Supports asynchronous concurrent validation using Tsinghua PyPI mirror.
"""

import asyncio
import re
from typing import Dict, List, Set, Tuple, Optional
from urllib.parse import urljoin

import httpx

from ..logging_config import get_logger

logger = get_logger()


class DependencyValidationError(Exception):
    """Base exception for dependency validation errors."""
    pass


class PackageNotFoundError(DependencyValidationError):
    """Exception for packages that don't exist on PyPI."""
    pass


class DependencyValidator:
    """
    Service for validating Python package dependencies against PyPI mirrors.

    Features:
    - Asynchronous concurrent package checking
    - Tsinghua PyPI mirror support for faster Chinese access
    - Intelligent package name normalization
    - Comprehensive error handling and retry logic
    """

    def __init__(self, mirror_url: str = "https://pypi.tuna.tsinghua.edu.cn/simple/"):
        """
        Initialize dependency validator.

        Args:
            mirror_url: PyPI mirror URL (defaults to Tsinghua mirror)
        """
        # Ensure mirror URL ends with /simple/
        if not mirror_url.endswith('/simple/'):
            if mirror_url.endswith('/simple'):
                mirror_url += '/'
            elif mirror_url.endswith('/'):
                mirror_url += 'simple/'
            else:
                mirror_url += '/simple/'

        self.mirror_url = mirror_url
        self.client: Optional[httpx.AsyncClient] = None
        self._semaphore = asyncio.Semaphore(3)  # Limit concurrent requests to prevent overwhelming

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

    async def initialize(self):
        """Initialize HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0),
                follow_redirects=True,
                headers={
                    'User-Agent': 'AI-Code-Flow-Dependency-Validator/1.0'
                }
            )
        logger.info(f"Dependency validator initialized with mirror: {self.mirror_url}")

    async def cleanup(self):
        """Cleanup HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    def _normalize_package_name(self, package_name: str) -> str:
        """
        Normalize package name for PyPI URL format.

        Args:
            package_name: Raw package name from requirements.txt

        Returns:
            Normalized package name
        """
        # Remove version specifiers and extras
        package_name = re.split(r'[>=<~!]', package_name)[0].strip()

        # Convert to lowercase and replace underscores with hyphens
        # (PyPI normalizes underscores to hyphens)
        return package_name.lower().replace('_', '-')

    async def _check_package_exists(self, package_name: str) -> Tuple[str, bool, Optional[str]]:
        """
        Check if a package exists on PyPI mirror.

        Args:
            package_name: Package name to check

        Returns:
            Tuple of (package_name, exists, error_message)
        """
        async with self._semaphore:
            try:
                normalized_name = self._normalize_package_name(package_name)
                # Ensure proper URL construction: mirror_url + normalized_name + '/'
                url = f"{self.mirror_url.rstrip('/')}/{normalized_name}/"

                logger.info(f"🔍 Checking package: {package_name} -> {url}")

                # Set timeout for individual request
                timeout = httpx.Timeout(3.0, connect=2.0)
                response = await self.client.head(url, follow_redirects=True, timeout=timeout)

                logger.info(f"📡 Package {package_name}: HTTP {response.status_code}")

                if response.status_code == 200:
                    logger.debug(f"✅ Package exists: {package_name}")
                    return package_name, True, None
                elif response.status_code == 404:
                    logger.warning(f"❌ Package not found: {package_name}")
                    return package_name, False, "Package not found (404)"
                else:
                    logger.warning(f"⚠️ Unexpected status for {package_name}: {response.status_code}")
                    # For any other status, we keep the package (policy: Error -> Keep)
                    return package_name, True, f"Unexpected status: {response.status_code}"

            except httpx.TimeoutException:
                logger.warning(f"⏰ Timeout checking package: {package_name}")
                return package_name, True, "Timeout (keeping package)"
            except httpx.ConnectError:
                logger.error(f"🔌 Connection error checking package: {package_name}")
                return package_name, True, "Connection error (keeping package)"
            except Exception as e:
                logger.error(f"💥 Error checking package {package_name}: {e}")
                return package_name, True, f"Error: {str(e)} (keeping package)"

    async def validate_requirements_async(self, requirements_content: str) -> Dict[str, any]:
        """
        Validate all packages in requirements.txt content asynchronously.

        Args:
            requirements_content: Content of requirements.txt

        Returns:
            Validation results dictionary
        """
        if self.client is None:
            await self.initialize()

        # Extract package names from requirements.txt
        packages = self._extract_packages_from_requirements(requirements_content)

        if not packages:
            return {
                "valid": True,
                "total_packages": 0,
                "valid_packages": 0,
                "invalid_packages": 0,
                "results": [],
                "summary": "No packages found in requirements.txt"
            }

        logger.info(f"Validating {len(packages)} packages against PyPI mirror...")

        # Check all packages concurrently
        tasks = [self._check_package_exists(pkg) for pkg in packages]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        valid_packages = []
        invalid_packages = []

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task failed with exception: {result}")
                continue

            package_name, exists, error_msg = result
            if exists:
                valid_packages.append(package_name)
            else:
                invalid_packages.append({
                    "name": package_name,
                    "reason": error_msg
                })

        # Create filtered requirements.txt content (remove invalid packages)
        filtered_requirements = self._create_filtered_requirements(
            requirements_content, invalid_packages
        )

        validation_results = {
            "valid": len(invalid_packages) == 0,
            "total_packages": len(packages),
            "valid_packages": len(valid_packages),
            "invalid_packages": len(invalid_packages),
            "valid_package_list": valid_packages,
            "invalid_package_list": invalid_packages,
            "original_requirements": requirements_content,
            "filtered_requirements": filtered_requirements,
            "summary": f"Validated {len(packages)} packages: {len(valid_packages)} valid, {len(invalid_packages)} invalid"
        }

        logger.info(validation_results["summary"])

        if invalid_packages:
            logger.warning("Invalid packages found:")
            for pkg in invalid_packages:
                logger.warning(f"  - {pkg['name']}: {pkg['reason']}")

        return validation_results

    def validate_requirements_sync(self, requirements_content: str) -> Dict[str, any]:
        """
        Synchronous wrapper for validate_requirements_async.
        Use this for simple synchronous validation.
        """
        try:
            # Create event loop if none exists
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is already running, we need to use run_until_complete
                    import nest_asyncio
                    nest_asyncio.apply()
                    return loop.run_until_complete(self.validate_requirements_async(requirements_content))
                else:
                    return loop.run_until_complete(self.validate_requirements_async(requirements_content))
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(self.validate_requirements_async(requirements_content))
        except Exception as e:
            logger.error(f"Error in synchronous validation: {e}")
            return {
                "valid": False,
                "error": str(e),
                "summary": f"Validation failed: {str(e)}"
            }

    def _extract_packages_from_requirements(self, requirements_content: str) -> List[str]:
        """
        Extract package names from requirements.txt content.

        Args:
            requirements_content: Raw requirements.txt content

        Returns:
            List of package names
        """
        packages = []

        for line in requirements_content.split('\n'):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Extract package name (remove version specifiers and extras)
            package_name = re.split(r'[>=<~!]', line)[0].strip()
            if package_name:
                packages.append(package_name)

        return packages

    def _create_filtered_requirements(self, original_content: str, invalid_packages: List[Dict]) -> str:
        """
        Create filtered requirements.txt content by removing invalid packages.

        Args:
            original_content: Original requirements.txt content
            invalid_packages: List of invalid package info

        Returns:
            Filtered requirements.txt content
        """
        invalid_names = {pkg["name"] for pkg in invalid_packages}
        filtered_lines = []

        for line in original_content.split('\n'):
            line = line.strip()

            # Keep comments and empty lines
            if not line or line.startswith('#'):
                filtered_lines.append(line)
                continue

            # Check if this line contains an invalid package
            package_name = re.split(r'[>=<~!]', line)[0].strip()
            if package_name not in invalid_names:
                filtered_lines.append(line)

        # Add warning comments for removed packages
        if invalid_packages:
            filtered_lines.append("")
            filtered_lines.append("# WARNING: Following packages were removed due to validation failures:")
            for pkg in invalid_packages:
                filtered_lines.append(f"# - {pkg['name']}: {pkg['reason']}")

        return '\n'.join(filtered_lines)

    async def validate_single_package(self, package_name: str) -> bool:
        """
        Validate a single package name.

        Args:
            package_name: Package name to validate

        Returns:
            True if package exists, False otherwise
        """
        if self.client is None:
            await self.initialize()

        _, exists, _ = await self._check_package_exists(package_name)
        return exists
