#!/usr/bin/env python3
"""
IP Address Extractor - A tool to parse log files and extract IP addresses.

This module provides functionality to extract both IPv4 and IPv6 addresses 
from log files using regular expressions. It supports various output modes
including unique IP extraction and frequency counting.
"""

import re
import argparse
import sys
from collections import Counter

class IPExtractor:
    """A class to extract IP addresses from log files."""

    # IPv4 pattern: matches 4 groups of 0-255 separated by dots
    IPV4_PATTERN = re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    )

    # IPv6 pattern: simplified version matching 8 groups of hex digits
    IPV6_PATTERN = re.compile(
        r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
    )

    def __init__(self, file_path):
        """Initialize the IP extractor with a file path.

        Args:
            file_path (str): Path to the log file to parse.
        """
        self.file_path = file_path
        self.ips = []

    def extract_ips(self, unique=False, count=False):
        """Extract IP addresses from the log file.

        Args:
            unique (bool): If True, return unique IPs only.
            count (bool): If True, return IP counts instead of list.

        Returns:
            list or dict: List of IPs if count is False, dict of counts if True.
        """
        self.ips = []

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    try:
                        # Find IPv4 addresses
                        ipv4_matches = self.IPV4_PATTERN.findall(line)
                        # Find IPv6 addresses
                        ipv6_matches = self.IPV6_PATTERN.findall(line)

                        # Add matches to list
                        self.ips.extend(ipv4_matches)
                        self.ips.extend(ipv6_matches)

                    except Exception as e:
                        print(f"Warning: Error processing line {line_num}: {e}", file=sys.stderr)

        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found.", file=sys.stderr)
            sys.exit(1)
        except PermissionError:
            print(f"Error: Permission denied to read '{self.file_path}'.", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)

        if count:
            return Counter(self.ips)
        elif unique:
            # Remove duplicates while preserving order
            seen = set()
            unique_ips = []
            for ip in self.ips:
                if ip not in seen:
                    seen.add(ip)
                    unique_ips.append(ip)
            return unique_ips
        else:
            return self.ips

class CLIInterface:
    """A class to handle command-line interface operations."""

    @staticmethod
    def parse_arguments():
        """Parse and return command-line arguments.

        Returns:
            argparse.Namespace: Parsed command-line arguments.
        """
        parser = argparse.ArgumentParser(
            description='Extract IP addresses from log files.',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  Extract IPs from a log file:
    python main.py access.log

  Extract unique IPs only:
    python main.py access.log --unique

  Show IP frequency counts:
    python main.py access.log --count
            """
        )

        parser.add_argument('file_path', help='Path to the log file')
        parser.add_argument('--unique', action='store_true', 
                           help='Extract unique IPs only')
        parser.add_argument('--count', action='store_true',
                           help='Show IP frequency counts')
        parser.add_argument('--verbose', '-v', action='store_true',
                           help='Enable verbose output')

        return parser.parse_args()

    @staticmethod
    def display_results(ips, args):
        """Display the extracted IP addresses.

        Args:
            ips (list or dict): Extracted IP addresses or counts.
            args (argparse.Namespace): Command-line arguments.
        """
        if isinstance(ips, dict):
            # Display IP counts
            print(f"\nFound {len(ips)} unique IP addresses:")
            print("-" * 50)
            for ip, count in sorted(ips.items(), key=lambda x: x[1], reverse=True):
                print(f"{ip:20} {count:5} occurrences")
        else:
            # Display IP list
            if args.unique:
                print(f"\nFound {len(ips)} unique IP addresses:")
            else:
                print(f"\nFound {len(ips)} IP addresses:")

            print("-" * 50)
            for ip in ips:
                print(ip)

def main():
    """Main function to run the IP extractor."""
    print("=" * 50)
    print("IP Address Extractor")
    print("=" * 50)

    # Parse command-line arguments
    args = CLIInterface.parse_arguments()

    # Create extractor and process file
    extractor = IPExtractor(args.file_path)
    ips = extractor.extract_ips(unique=args.unique, count=args.count)

    # Display results
    CLIInterface.display_results(ips, args)

    # Additional info if verbose mode
    if args.verbose:
        print(f"\nFile processed: {args.file_path}")
        print(f"Options: unique={args.unique}, count={args.count}")

if __name__ == "__main__":
    # Demonstrate usage with a concrete scenario
    print("=== IP Address Extractor Demo ===")
    print("Processing sample log file...")

    # Create a sample log file for demonstration
    sample_log_content = """192.168.1.1 - - [10/Oct/2023:13:55:36] "GET /api/users HTTP/1.1" 200 2326
10.0.0.1 - - [10/Oct/2023:13:55:38] "POST /api/login HTTP/1.1" 200 1234
192.168.1.1 - - [10/Oct/2023:13:56:01] "GET /api/products HTTP/1.1" 200 5432
172.16.0.100 - - [10/Oct/2023:13:57:15] "DELETE /api/users/123 HTTP/1.1" 204 0
192.168.1.1 - - [10/Oct/2023:13:58:22] "PUT /api/users/123 HTTP/1.1" 200 456
2001:0db8:85a3:0000:0000:8a2e:0370:7334 - - [10/Oct/2023:13:59:10] "GET /api/data HTTP/1.1" 200 789
10.0.0.2 - - [10/Oct/2023:14:00:05] "GET /api/status HTTP/1.1" 200 111
"""

    # Write sample log file
    sample_file_path = "sample_access.log"
    try:
        with open(sample_file_path, 'w') as f:
            f.write(sample_log_content)

        print(f"Created sample log file: {sample_file_path}")
        print("\nSample log content:")
        print("-" * 40)
        print(sample_log_content)

        # Process the sample file
        extractor = IPExtractor(sample_file_path)

        print("\n--- Extracting all IPs ---")
        all_ips = extractor.extract_ips(unique=False)
        print(f"Found {len(all_ips)} IP addresses:")
        for ip in all_ips:
            print(f"  {ip}")

        print("\n--- Extracting unique IPs ---")
        unique_ips = extractor.extract_ips(unique=True)
        print(f"Found {len(unique_ips)} unique IP addresses:")
        for ip in unique_ips:
            print(f"  {ip}")

        print("\n--- IP frequency counts ---")
        ip_counts = extractor.extract_ips(unique=True, count=True)
        for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ip}: {count} occurrences")

        # Clean up sample file
        import os
        os.remove(sample_file_path)
        print(f"\nCleaned up sample file: {sample_file_path}")

        print("\n" + "=" * 50)
        print("To use with your own log file, run:")
        print("python main.py <log_file_path> [--unique] [--count]")
        print("=" * 50)

    except Exception as e:
        print(f"Error during demo: {e}")
        sys.exit(1)