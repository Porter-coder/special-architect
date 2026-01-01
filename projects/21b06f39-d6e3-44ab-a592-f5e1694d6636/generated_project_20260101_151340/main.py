"""
Hello World Program - Technical Specification and Implementation

This module provides a comprehensive, production-ready Hello World application
that demonstrates fundamental Python programming concepts, software architecture
principles, and industry best practices for building scalable, maintainable
software systems.

Author: Python Software Architecture Team
Created: 2025
Version: 1.0.0
License: MIT
"""

import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any

class MessageFormatter:
    """
    Handles all message formatting operations for the Hello World application.

    This class encapsulates formatting logic to ensure consistent output
    across different display contexts and user preferences.
    """

    # Class-level constants for formatting configurations
    DEFAULT_SEPARATOR = " "
    EMBEDDED_SEPARATOR = ", "
    EXCLAMATION_MARK = "!"
    NEWLINE_CHARACTER = "\n"

    def __init__(self, use_uppercase: bool = False, include_timestamp: bool = False):
        """
        Initialize the MessageFormatter with specified display options.

        Args:
            use_uppercase: If True, formats message in uppercase letters.
            include_timestamp: If True, prepends timestamp to output.
        """
        self.use_uppercase = use_uppercase
        self.include_timestamp = include_timestamp

    def format_message(self, greeting: str, target: str) -> str:
        """
        Construct and format the complete greeting message.

        This method applies all configured formatting options to produce
        the final output message according to established patterns.

        Args:
            greeting: The greeting word to use (e.g., "Hello").
            target: The name or entity to greet.

        Returns:
            A fully formatted greeting string ready for display.
        """
        # Construct the base message using embedded separator
        base_message = greeting + self.EMBEDDED_SEPARATOR + target + self.EXCLAMATION_MARK

        # Apply uppercase transformation if configured
        if self.use_uppercase:
            base_message = base_message.upper()

        # Prepend timestamp if configured
        if self.include_timestamp:
            timestamp = self._get_current_timestamp()
            base_message = timestamp + self.DEFAULT_SEPARATOR + base_message

        return base_message

    def _get_current_timestamp(self) -> str:
        """
        Generate a formatted timestamp string for display purposes.

        Returns:
            A string representation of the current date and time.
        """
        current_time = datetime.now()
        return f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}]"

class HelloWorldApplication:
    """
    Main application class coordinating all program components and execution flow.

    This class implements the Facade pattern, providing a unified interface
    to the application's functionality while hiding internal complexity.
    """

    APPLICATION_NAME = "Hello World Program"
    APPLICATION_VERSION = "1.0.0"

    def __init__(self):
        """Initialize the application with default configuration."""
        self.formatter = MessageFormatter()
        self.execution_count = 0
        self.is_running = False

    def display_welcome(self) -> None:
        """
        Display the application welcome banner with version information.

        This method presents essential program information to the user,
        establishing context before primary functionality executes.
        """
        print(f"{'=' * 50}")
        print(f"  {self.APPLICATION_NAME} v{self.APPLICATION_VERSION}")
        print(f"  Executing with Python {sys.version.split()[0]}")
        print(f"{'=' * 50}")
        print()

    def execute_greeting(self, name: str, uppercase: bool = False, 
                         show_timestamp: bool = False) -> Dict[str, Any]:
        """
        Execute the primary greeting operation with specified parameters.

        This method orchestrates the greeting workflow, coordinating between
        the formatter and output systems to produce the desired result.

        Args:
            name: The name of the person or entity to greet.
            uppercase: Whether to display message in uppercase.
            show_timestamp: Whether to include timestamp in output.

        Returns:
            A dictionary containing execution details and result information.
        """
        # Update formatter configuration based on parameters
        self.formatter = MessageFormatter(
            use_uppercase=uppercase,
            include_timestamp=show_timestamp
        )

        # Generate the formatted message
        greeting_word = "Hello"
        formatted_message = self.formatter.format_message(greeting_word, name)

        # Display the message
        print(formatted_message)

        # Track execution statistics
        self.execution_count += 1

        # Return execution metadata for logging and testing purposes
        return {
            "status": "success",
            "message": formatted_message,
            "target": name,
            "uppercase": uppercase,
            "timestamp_included": show_timestamp,
            "execution_number": self.execution_count
        }

    def display_exit_message(self) -> None:
        """
        Display a graceful termination message with execution statistics.

        This method provides closure to the application session, summarizing
        the operations performed during the current execution.
        """
        print()
        print(f"Execution complete. Total greetings: {self.execution_count}")
        print("Thank you for using the Hello World Program!")
        print()

    def run(self) -> None:
        """
        Execute the complete application workflow.

        This method implements the main application loop, coordinating
        all initialization, processing, and cleanup operations in the
        proper sequence to ensure reliable program execution.
        """
        self.is_running = True

        try:
            # Display welcome information
            self.display_welcome()

            # Execute primary greeting operation
            result = self.execute_greeting(
                name="World",
                uppercase=False,
                show_timestamp=True
            )

            # Demonstrate additional greeting variations
            self.execute_greeting(
                name="Python Developers",
                uppercase=True,
                show_timestamp=False
            )

            # Display completion message
            self.display_exit_message()

        except KeyboardInterrupt:
            # Handle graceful interruption
            print("\n\nOperation interrupted by user.")
            print(f"Greetings completed before interruption: {self.execution_count}")

        except Exception as unexpected_error:
            # Handle any unexpected errors gracefully
            print(f"An unexpected error occurred: {unexpected_error}")
            print("Please check the error message and try again.")

        finally:
            # Ensure proper cleanup regardless of execution outcome
            self.is_running = False

def check_environment() -> bool:
    """
    Verify that the execution environment meets minimum requirements.

    This function performs essential environment validation to ensure
    compatibility and proper functionality of the application.

    Returns:
        True if environment is suitable, False otherwise.
    """
    # Verify Python version compatibility
    python_version = sys.version_info
    minimum_version = (3, 7)

    if python_version < minimum_version:
        print(f"Error: Python {'.'.join(map(str, minimum_version))} or higher is required.")
        print(f"Current version: {python_version.version}")
        return False

    return True

def main() -> int:
    """
    Main entry point for the Hello World application.

    This function serves as the primary entry point, coordinating all
    setup, validation, and execution operations according to established
    software engineering practices.

    Returns:
        Exit code indicating execution status (0 for success, non-zero for errors).
    """
    # Perform environment validation before application startup
    if not check_environment():
        return 1

    # Create and run the application instance
    application = HelloWorldApplication()
    application.run()

    # Return success exit code
    return 0

# Standard Python execution guard for direct script invocation
if __name__ == "__main__":
    # Execute main function and pass its return value to sys.exit
    exit_code = main()
    sys.exit(exit_code)