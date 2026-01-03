"""
Simple Todo List Application
============================
A command-line based todo list application with task management features.
Supports creating, viewing, updating, and deleting tasks with priorities,
due dates, tags, and completion tracking.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# File to store todo data
DATA_FILE = "todos.json"


class TodoTask:
    """Represents a single todo task."""

    def __init__(self, task_id: int, title: str, description: str = "",
                 priority: str = "medium", due_date: str = "",
                 tags: List[str] = None, completed: bool = False):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.tags = tags if tags else []
        self.completed = completed
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict:
        """Convert task to dictionary for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "tags": self.tags,
            "completed": self.completed,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'TodoTask':
        """Create task from dictionary."""
        task = cls(
            task_id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "medium"),
            due_date=data.get("due_date", ""),
            tags=data.get("tags", []),
            completed=data.get("completed", False)
        )
        task.created_at = data.get("created_at", "")
        return task

    def __str__(self) -> str:
        status = "[X]" if self.completed else "[ ]"
        priority_display = {"high": "!!!", "medium": "!!", "low": "!"}.get(self.priority, "!")
        tags_display = f" [{', '.join(self.tags)}]" if self.tags else ""
        due_display = f" (Due: {self.due_date})" if self.due_date else ""
        return f"{status} {self.id:3d}. {priority_display} {self.title}{tags_display}{due_display}"


class TodoList:
    """Manages a collection of todo tasks."""

    def __init__(self):
        self.tasks: List[TodoTask] = []
        self.load_tasks()

    def load_tasks(self) -> None:
        """Load tasks from JSON file."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [TodoTask.from_dict(t) for t in data]
            except (json.JSONDecodeError, IOError):
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self) -> None:
        """Save tasks to JSON file."""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2, ensure_ascii=False)

    def add_task(self, title: str, description: str = "",
                 priority: str = "medium", due_date: str = "",
                 tags: str = "") -> int:
        """Add a new task. Returns the new task ID."""
        new_id = 1
        if self.tasks:
            new_id = max(t.id for t in self.tasks) + 1

        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        task = TodoTask(new_id, title, description, priority, due_date, tag_list)
        self.tasks.append(task)
        self.save_tasks()
        return new_id

    def get_all_tasks(self) -> List[TodoTask]:
        """Return all tasks."""
        return self.tasks

    def get_task_by_id(self, task_id: int) -> Optional[TodoTask]:
        """Find a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed."""
        task = self.get_task_by_id(task_id)
        if task:
            task.completed = True
            self.save_tasks()
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            return True
        return False

    def update_task(self, task_id: int, title: str = None,
                    description: str = None, priority: str = None,
                    due_date: str = None, tags: str = None) -> bool:
        """Update task properties."""
        task = self.get_task_by_id(task_id)
        if task:
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = priority
            if due_date is not None:
                task.due_date = due_date
            if tags is not None:
                task.tags = [t.strip() for t in tags.split(",") if t.strip()]
            self.save_tasks()
            return True
        return False

    def search_tasks(self, keyword: str) -> List[TodoTask]:
        """Search tasks by keyword in title or description."""
        keyword = keyword.lower()
        return [t for t in self.tasks
                if keyword in t.title.lower() or keyword in t.description.lower()]

    def filter_by_status(self, completed: bool = None) -> List[TodoTask]:
        """Filter tasks by completion status."""
        if completed is None:
            return self.tasks
        return [t for t in self.tasks if t.completed == completed]

    def filter_by_priority(self, priority: str) -> List[TodoTask]:
        """Filter tasks by priority level."""
        return [t for t in self.tasks if t.priority == priority]

    def sort_tasks(self, sort_by: str = "id") -> List[TodoTask]:
        """Sort tasks by specified criteria."""
        sorted_tasks = self.tasks.copy()
        if sort_by == "priority":
            priority_order = {"high": 0, "medium": 1, "low": 2}
            sorted_tasks.sort(key=lambda t: (priority_order.get(t.priority, 3), t.id))
        elif sort_by == "due_date":
            sorted_tasks.sort(key=lambda t: (t.due_date, t.id))
        elif sort_by == "created":
            sorted_tasks.sort(key=lambda t: (t.created_at, t.id))
        else:
            sorted_tasks.sort(key=lambda t: t.id)
        return sorted_tasks

    def get_next_id(self) -> int:
        """Get the next available task ID."""
        if not self.tasks:
            return 1
        return max(t.id for t in self.tasks) + 1


def print_menu():
    """Display the main menu."""
    print("\n" + "=" * 40)
    print("         TODO LIST APPLICATION")
    print("=" * 40)
    print("1. View all tasks")
    print("2. Add new task")
    print("3. Complete a task")
    print("4. Delete a task")
    print("5. Update a task")
    print("6. Search tasks")
    print("7. Filter by status")
    print("8. Sort tasks")
    print("0. Exit")
    print("=" * 40)


def print_task_details(task: TodoTask) -> None:
    """Print detailed information about a task."""
    print(f"\n--- Task #{task.id} ---")
    print(f"Title: {task.title}")
    print(f"Description: {task.description if task.description else '(No description)'}")
    print(f"Priority: {task.priority.capitalize()}")
    print(f"Due Date: {task.due_date if task.due_date else '(Not set)'}")
    print(f"Tags: {', '.join(task.tags) if task.tags else '(No tags)'}")
    print(f"Status: {'Completed' if task.completed else 'Not Completed'}")
    print(f"Created: {task.created_at}")
    print("-" * 25)


def get_priority_input() -> str:
    """Get valid priority input from user."""
    while True:
        print("Priority options: high, medium, low")
        priority = input("Enter priority (default: medium): ").strip().lower()
        if priority in ["high", "medium", "low"]:
            return priority
        elif priority == "":
            return "medium"
        else:
            print("Invalid priority. Please enter high, medium, or low.")


def get_valid_id(todo_list: TodoList) -> int:
    """Get a valid task ID from user."""
    while True:
        try:
            task_id = int(input("Enter task ID: "))
            if todo_list.get_task_by_id(task_id):
                return task_id
            else:
                print(f"No task found with ID {task_id}. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def demo_mode(todo_list: TodoList):
    """Run a demonstration of the todo application."""
    print("\n" + "=" * 50)
    print("         DEMONSTRATION MODE")
    print("=" * 50)
    print("\nAdding sample tasks...")

    # Add sample tasks
    todo_list.add_task("Learn Python",
                       "Complete the Python tutorial exercises",
                       "high", "2024-12-31", "programming,learning")

    todo_list.add_task("Buy groceries",
                       "Milk, eggs, bread, vegetables",
                       "medium", "2024-12-15", "shopping")

    todo_list.add_task("Clean room",
                       "Organize desk and vacuum floor",
                       "low", "2024-12-20", "home")

    todo_list.add_task("Call mom",
                       "Wish her happy birthday",
                       "high", "2024-12-25", "personal")

    print("Sample tasks have been added!\n")

    # Show all tasks
    print("All tasks (sorted by ID):")
    print("-" * 40)
    for task in todo_list.sort_tasks("id"):
        print(task)
    print()

    # Demonstrate search
    print("Searching for 'Python':")
    results = todo_list.search_tasks("Python")
    for task in results:
        print(f"  {task}")

    # Demonstrate filtering by priority
    print("\nHigh priority tasks:")
    high_tasks = todo_list.filter_by_priority("high")
    for task in high_tasks:
        print(f"  {task}")

    # Demonstrate detail view
    print("\nDetailed view of task #1:")
    task1 = todo_list.get_task_by_id(1)
    if task1:
        print_task_details(task1)

    print("Demo completed! Entering interactive mode...")


def main():
    """Main application loop."""
    todo_list = TodoList()

    # Check if this is first run (no tasks)
    is_first_run = len(todo_list.get_all_tasks()) == 0

    print("\n" + "=" * 50)
    print("         WELCOME TO TODO LIST APP")
    print("=" * 50)

    if is_first_run:
        print("\nNo tasks found. Starting with sample data...")
        demo_mode(todo_list)

    while True:
        print_menu()
        choice = input("\nEnter your choice (0-8): ").strip()

        if choice == "0":
            print("\nThank you for using Todo List App!")
            print("Your tasks have been saved automatically.")
            break

        elif choice == "1":
            # View all tasks
            print("\n--- ALL TASKS ---")
            tasks = todo_list.get_all_tasks()
            if not tasks:
                print("No tasks yet. Add some tasks first!")
            else:
                for task in tasks:
                    print(task)
            input("\nPress Enter to continue...")

        elif choice == "2":
            # Add new task
            print("\n--- ADD NEW TASK ---")
            title = input("Enter task title: ").strip()
            if not title:
                print("Title cannot be empty. Task not saved.")
                input("Press Enter to continue...")
                continue

            description = input("Enter description (optional): ").strip()
            priority = get_priority_input()
            due_date = input("Enter due date (YYYY-MM-DD, optional): ").strip()
            tags = input("Enter tags (comma-separated, optional): ").strip()

            task_id = todo_list.add_task(title, description, priority, due_date, tags)
            print(f"\nTask #{task_id} added successfully!")
            input("Press Enter to continue...")

        elif choice == "3":
            # Complete a task
            print("\n--- COMPLETE TASK ---")
            tasks = todo_list.filter_by_status(False)
            if not tasks:
                print("No incomplete tasks to complete!")
            else:
                print("Incomplete tasks:")
                for task in tasks:
                    print(f"  {task}")
                task_id = get_valid_id(todo_list)
                if todo_list.complete_task(task_id):
                    print(f"Task #{task_id} marked as completed!")
                else:
                    print("Failed to complete task.")
            input("Press Enter to continue...")

        elif choice == "4":
            # Delete a task
            print("\n--- DELETE TASK ---")
            tasks = todo_list.get_all_tasks()
            if not tasks:
                print("No tasks to delete!")
            else:
                print("All tasks:")
                for task in tasks:
                    print(f"  {task}")
                task_id = get_valid_id(todo_list)
                confirm = input(f"Delete task #{task_id}? (y/n): ").strip().lower()
                if confirm == "y":
                    if todo_list.delete_task(task_id):
                        print(f"Task #{task_id} deleted successfully!")
                    else:
                        print("Failed to delete task.")
            input("Press Enter to continue...")

        elif choice == "5":
            # Update a task
            print("\n--- UPDATE TASK ---")
            tasks = todo_list.get_all_tasks()
            if not tasks:
                print("No tasks to update!")
            else:
                print("All tasks:")
                for task in tasks:
                    print(f"  {task}")
                task_id = get_valid_id(todo_list)
                task = todo_list.get_task_by_id(task_id)
                if task:
                    print(f"\nUpdating Task #{task_id} (leave blank to keep current value)")

                    new_title = input(f"Title [{task.title}]: ").strip()
                    new_desc = input(f"Description [{task.description}]: ").strip()
                    new_priority = input(f"Priority [{task.priority}]: ").strip()
                    new_due_date = input(f"Due date [{task.due_date}]: ").strip()
                    new_tags = input(f"Tags [{', '.join(task.tags)}]: ").strip()

                    if todo_list.update_task(task_id,
                                             title=new_title if new_title else None,
                                             description=new_desc if new_desc else None,
                                             priority=new_priority if new_priority else None,
                                             due_date=new_due_date if new_due_date else None,
                                             tags=new_tags if new_tags else None):
                        print(f"Task #{task_id} updated successfully!")
                    else:
                        print("Failed to update task.")
            input("Press Enter to continue...")

        elif choice == "6":
            # Search tasks
            print("\n--- SEARCH TASKS ---")
            keyword = input("Enter search keyword: ").strip()
            if keyword:
                results = todo_list.search_tasks(keyword)
                if results:
                    print(f"\nFound {len(results)} task(s):")
                    for task in results:
                        print(f"  {task}")
                else:
                    print("No tasks found matching your search.")
            else:
                print("Please enter a keyword to search.")
            input("\nPress Enter to continue...")

        elif choice == "7":
            # Filter by status
            print("\n--- FILTER BY STATUS ---")
            print("1. Show all tasks")
            print("2. Show only completed")
            print("3. Show only incomplete")
            filter_choice = input("Enter choice (1-3): ").strip()

            if filter_choice == "1":
                filtered_tasks = todo_list.filter_by_status(None)
            elif filter_choice == "2":
                filtered_tasks = todo_list.filter_by_status(True)
            elif filter_choice == "3":
                filtered_tasks = todo_list.filter_by_status(False)
            else:
                filtered_tasks = todo_list.get_all_tasks()

            print(f"\nFiltered tasks ({len(filtered_tasks)}):")
            for task in filtered_tasks:
                print(f"  {task}")
            input("\nPress Enter to continue...")

        elif choice == "8":
            # Sort tasks
            print("\n--- SORT TASKS ---")
            print("1. Sort by ID (default)")
            print("2. Sort by priority")
            print("3. Sort by due date")
            print("4. Sort by creation date")
            sort_choice = input("Enter choice (1-4): ").strip()

            sort_options = {"1": "id", "2": "priority", "3": "due_date", "4": "created"}
            sort_by = sort_options.get(sort_choice, "id")

            sorted_tasks = todo_list.sort_tasks(sort_by)
            print(f"\nTasks sorted by {sort_by}:")
            for task in sorted_tasks:
                print(f"  {task}")
            input("\nPress Enter to continue...")

        else:
            print("\nInvalid choice. Please enter a number from 0 to 8.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()