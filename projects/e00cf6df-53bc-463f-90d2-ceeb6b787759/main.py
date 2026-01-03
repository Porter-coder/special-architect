#!/usr/bin/env python3
"""
TODO List Application - A simple command-line TODO list manager

Features:
- Create, view, edit, delete tasks
- Track task status (todo, in-progress, completed, archived)
- Priority levels (low, medium, high)
- Categories/tags
- Due dates
- Data persistence (JSON)
"""

import json
import os
import datetime
from typing import List, Dict, Optional

# Constants
DATA_FILE = "todos.json"


class Task:
    """Represents a single task in the TODO list"""

    def __init__(self, task_id: int, title: str, description: str = "",
                 priority: str = "medium", due_date: str = "",
                 category: str = "General", status: str = "todo"):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.category = category
        self.status = status
        self.created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at

    def to_dict(self) -> Dict:
        """Convert task to dictionary for JSON storage"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Task':
        """Create Task from dictionary"""
        task = Task(
            task_id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "medium"),
            due_date=data.get("due_date", ""),
            category=data.get("category", "General"),
            status=data.get("status", "todo")
        )
        task.created_at = data.get("created_at", "")
        task.updated_at = data.get("updated_at", "")
        return task


class TodoList:
    """Manages a collection of tasks"""

    def __init__(self):
        self.tasks: List[Task] = []
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.tasks.append(Task.from_dict(item))
            except (json.JSONDecodeError, IOError):
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([task.to_dict() for task in self.tasks], f, ensure_ascii=False, indent=2)

    def create_task(self, title: str, description: str = "",
                    priority: str = "medium", due_date: str = "",
                    category: str = "General") -> Task:
        """Create a new task"""
        task_id = max([t.id for t in self.tasks], default=0) + 1
        task = Task(task_id, title, description, priority, due_date, category)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        """Update a task's properties"""
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key) and key not in ['id', 'created_at']:
                    setattr(task, key, value)
            task.updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.save_tasks()
        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task permanently"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            return True
        return False

    def list_tasks(self, status: str = None, category: str = None,
                   priority: str = None) -> List[Task]:
        """Retrieve tasks with optional filters"""
        result = self.tasks
        if status:
            result = [t for t in result if t.status == status]
        if category:
            result = [t for t in result if t.category == category]
        if priority:
            result = [t for t in result if t.priority == priority]
        return result

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = set()
        for task in self.tasks:
            categories.add(task.category)
        return sorted(list(categories))


class TodoApp:
    """Command-line interface for the TODO application"""

    def __init__(self):
        self.todo_list = TodoList()

    def display_menu(self):
        """Print the main menu"""
        print("\n" + "=" * 50)
        print("              TODO LIST APPLICATION")
        print("=" * 50)
        print("1. View all tasks")
        print("2. Create new task")
        print("3. Update task")
        print("4. Delete task")
        print("5. Filter tasks")
        print("6. Mark task as in-progress")
        print("7. Mark task as completed")
        print("8. Search tasks")
        print("9. View statistics")
        print("10. Exit")
        print("=" * 50)

    def get_input(self, prompt: str) -> str:
        """Get user input with a prompt"""
        return input(prompt).strip()

    def display_task_table(self, tasks: List[Task], title: str = "Tasks"):
        """Display tasks in a formatted table"""
        if not tasks:
            print(f"\nNo {title.lower()} found.")
            return

        print(f"\n--- {title} ({len(tasks)} tasks) ---")
        print("-" * 95)
        print(f"{'ID':<5} {'Title':<25} {'Priority':<10} {'Category':<15} {'Status':<15} {'Due Date':<12}")
        print("-" * 95)

        for task in tasks:
            status_display = task.status.replace('-', ' ').title()
            due_date_display = task.due_date if task.due_date else "Not set"
            print(f"{task.id:<5} {task.title[:25]:<25} {task.priority:<10} {task.category:<15} {status_display:<15} {due_date_display:<12}")

    def run(self):
        """Main application loop"""
        print("\n" + "=" * 50)
        print("      Welcome to TODO List Application!")
        print("=" * 50)
        print("Manage your tasks efficiently and never miss")
        print("a deadline again!")
        print("=" * 50)

        # Add sample tasks if this is first run
        if len(self.todo_list.tasks) == 0:
            print("\nAdding sample tasks to get you started...")
            self.todo_list.create_task(
                title="Learn Python programming",
                description="Complete Python basics tutorial",
                priority="high",
                category="Learning",
                due_date="2025-01-15"
            )
            self.todo_list.create_task(
                title="Buy groceries",
                description="Milk, eggs, bread, and fruits",
                priority="medium",
                category="Personal",
                due_date="2025-01-10"
            )
            self.todo_list.create_task(
                title="Prepare meeting agenda",
                description="Outline topics for weekly team meeting",
                priority="high",
                category="Work",
                due_date="2025-01-12"
            )
            self.todo_list.create_task(
                title="Read book",
                description="Finish reading 'Python Crash Course'",
                priority="low",
                category="Personal",
                due_date="2025-02-01"
            )
            print("Sample tasks added successfully!")

        while True:
            self.display_menu()
            choice = self.get_input("Select an option (1-10): ")

            if choice == '1':
                self.view_tasks()
            elif choice == '2':
                self.create_task()
            elif choice == '3':
                self.update_task()
            elif choice == '4':
                self.delete_task()
            elif choice == '5':
                self.filter_tasks()
            elif choice == '6':
                self.mark_in_progress()
            elif choice == '7':
                self.mark_completed()
            elif choice == '8':
                self.search_tasks()
            elif choice == '9':
                self.view_statistics()
            elif choice == '10':
                print("\nThank you for using TODO List Application!")
                print("Your tasks have been saved automatically.")
                print("Goodbye!")
                break
            else:
                print("\nInvalid option. Please enter a number between 1-10.")

            self.get_input("\nPress Enter to continue...")

    def view_tasks(self):
        """Display all tasks"""
        tasks = self.todo_list.list_tasks()
        if not tasks:
            print("\nNo tasks found. Create some tasks first!")
        else:
            self.display_task_table(tasks, "All Tasks")

    def create_task(self):
        """Create a new task"""
        print("\n--- Create New Task ---")

        title = self.get_input("Enter task title: ")

        if not title:
            print("Title cannot be empty!")
            return

        description = self.get_input("Enter description (optional): ")

        print("\nPriority levels: low, medium, high")
        priority = self.get_input("Enter priority (default: medium): ")
        priority = priority.lower() if priority.lower() in ['low', 'medium', 'high'] else 'medium'

        categories = self.todo_list.get_categories()
        if categories:
            print(f"\nExisting categories: {', '.join(categories)}")
        category = self.get_input("Enter category (default: General): ")
        category = category if category else "General"

        print("\nDate format: YYYY-MM-DD (e.g., 2025-01-15)")
        due_date = self.get_input("Enter due date (optional): ")

        # Validate date format if provided
        if due_date:
            try:
                datetime.datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Due date will not be set.")
                due_date = ""

        task = self.todo_list.create_task(title, description, priority, due_date, category)
        print(f"\nTask created successfully!")
        print(f"  Title: {task.title}")
        print(f"  Priority: {task.priority}")
        print(f"  Category: {task.category}")
        print(f"  Due Date: {task.due_date if task.due_date else 'Not set'}")

    def update_task(self):
        """Update an existing task"""
        task_id_str = self.get_input("Enter task ID to update: ")

        try:
            task_id = int(task_id_str)
        except ValueError:
            print("Invalid task ID! Please enter a number.")
            return

        task = self.todo_list.get_task(task_id)
        if not task:
            print(f"Task with ID {task_id} not found!")
            return

        print(f"\n--- Update Task (ID: {task.id}) ---")
        print(f"Current values - Title: {task.title}, Priority: {task.priority}, ")
        print(f"                Category: {task.category}, Status: {task.status}")
        print("\nLeave fields blank to keep current value.")

        new_title = self.get_input(f"Enter new title ({task.title}): ")
        new_description = self.get_input(f"Enter new description ({task.description}): ")

        print("\nPriority levels: low, medium, high")
        new_priority = self.get_input(f"Enter new priority (current: {task.priority}): ")
        new_category = self.get_input(f"Enter new category ({task.category}): ")

        print("\nStatus levels: todo, in-progress, completed, archived")
        new_status = self.get_input(f"Enter new status (current: {task.status}): ")

        print("\nDate format: YYYY-MM-DD")
        new_due_date = self.get_input(f"Enter new due date ({task.due_date}): ")

        updates = {}
        if new_title:
            updates['title'] = new_title
        if new_description:
            updates['description'] = new_description
        if new_priority in ['low', 'medium', 'high']:
            updates['priority'] = new_priority
        if new_category:
            updates['category'] = new_category
        if new_status in ['todo', 'in-progress', 'completed', 'archived']:
            updates['status'] = new_status
        if new_due_date:
            try:
                datetime.datetime.strptime(new_due_date, "%Y-%m-%d")
                updates['due_date'] = new_due_date
            except ValueError:
                print("Invalid date format. Due date not updated.")

        if updates:
            self.todo_list.update_task(task_id, **updates)
            print("\nTask updated successfully!")
        else:
            print("\nNo changes made.")

    def delete_task(self):
        """Delete a task"""
        task_id_str = self.get_input("Enter task ID to delete: ")

        try:
            task_id = int(task_id_str)
        except ValueError:
            print("Invalid task ID! Please enter a number.")
            return

        task = self.todo_list.get_task(task_id)
        if not task:
            print(f"Task with ID {task_id} not found!")
            return

        confirm = self.get_input(f"Delete task '{task.title}'? (y/n): ")
        if confirm.lower() == 'y':
            if self.todo_list.delete_task(task_id):
                print("Task deleted successfully!")
            else:
                print("Failed to delete task.")
        else:
            print("Deletion cancelled.")

    def filter_tasks(self):
        """Filter tasks by status, category, or priority"""
        print("\n--- Filter Tasks ---")
        print("1. Filter by status")
        print("2. Filter by category")
        print("3. Filter by priority")
        print("4. Show all tasks")

        choice = self.get_input("Select filter option (1-4): ")

        status = None
        category = None
        priority = None
        filter_name = ""

        if choice == '1':
            print("\nStatus options: todo, in-progress, completed, archived")
            status = self.get_input("Enter status to filter: ")
            if status not in ['todo', 'in-progress', 'completed', 'archived']:
                print("Invalid status. Showing all tasks.")
                status = None
            else:
                filter_name = status.replace('-', ' ').title()
        elif choice == '2':
            category = self.get_input("Enter category to filter: ")
            filter_name = category
        elif choice == '3':
            print("\nPriority options: low, medium, high")
            priority = self.get_input("Enter priority to filter: ")
            if priority not in ['low', 'medium', 'high']:
                print("Invalid priority. Showing all tasks.")
                priority = None
            else:
                filter_name = priority.title()
        else:
            pass

        tasks = self.todo_list.list_tasks(status=status, category=category, priority=priority)
        self.display_task_table(tasks, f"Filtered Tasks ({filter_name})" if filter_name else "All Tasks")

    def mark_in_progress(self):
        """Mark a task as in-progress"""
        task_id_str = self.get_input("Enter task ID to mark as in-progress: ")

        try:
            task_id = int(task_id_str)
        except ValueError:
            print("Invalid task ID! Please enter a number.")
            return

        task = self.todo_list.get_task(task_id)
        if not task:
            print(f"Task with ID {task_id} not found!")
            return

        if task.status == 'in-progress':
            print(f"Task '{task.title}' is already in progress.")
            return

        self.todo_list.update_task(task_id, status='in-progress')
        print(f"Task '{task.title}' marked as in-progress!")

    def mark_completed(self):
        """Mark a task as completed"""
        task_id_str = self.get_input("Enter task ID to mark as completed: ")

        try:
            task_id = int(task_id_str)
        except ValueError:
            print("Invalid task ID! Please enter a number.")
            return

        task = self.todo_list.get_task(task_id)
        if not task:
            print(f"Task with ID {task_id} not found!")
            return

        if task.status == 'completed':
            print(f"Task '{task.title}' is already completed.")
            return

        self.todo_list.update_task(task_id, status='completed')
        print(f"Task '{task.title}' marked as completed! Great job!")

    def search_tasks(self):
        """Search tasks by title or description"""
        keyword = self.get_input("Enter keyword to search: ").lower()

        if not keyword:
            print("Please enter a keyword.")
            return

        results = []
        for task in self.todo_list.tasks:
            if keyword in task.title.lower() or keyword in task.description.lower():
                results.append(task)

        if results:
            print(f"\n--- Search Results ({len(results)} tasks found) ---")
            for task in results:
                status_display = task.status.replace('-', ' ').title()
                print(f"  [{{ID: {task.id}}}] {task.title} - {status_display} ({task.priority})")
        else:
            print(f"\nNo tasks found containing '{keyword}'.")

    def view_statistics(self):
        """Display task statistics"""
        tasks = self.todo_list.tasks
        total = len(tasks)

        if total == 0:
            print("\nNo tasks to display statistics for.")
            return

        # Count by status
        todo_count = len([t for t in tasks if t.status == 'todo'])
        in_progress_count = len([t for t in tasks if t.status == 'in-progress'])
        completed_count = len([t for t in tasks if t.status == 'completed'])
        archived_count = len([t for t in tasks if t.status == 'archived'])

        # Count by priority
        high_count = len([t for t in tasks if t.priority == 'high'])
        medium_count = len([t for t in tasks if t.priority == 'medium'])
        low_count = len([t for t in tasks if t.priority == 'low'])

        # Calculate completion rate
        completed_rate = (completed_count / total) * 100 if total > 0 else 0

        print("\n--- Task Statistics ---")
        print(f"\nTotal Tasks: {total}")
        print(f"\nBy Status:")
        print(f"  Todo:        {todo_count} ({todo_count/total*100:.1f}%)")
        print(f"  In Progress: {in_progress_count} ({in_progress_count/total*100:.1f}%)")
        print(f"  Completed:   {completed_count} ({completed_count/total*100:.1f}%)")
        print(f"  Archived:    {archived_count} ({archived_count/total*100:.1f}%)")
        print(f"\nBy Priority:")
        print(f"  High:    {high_count} ({high_count/total*100:.1f}%)")
        print(f"  Medium:  {medium_count} ({medium_count/total*100:.1f}%)")
        print(f"  Low:     {low_count} ({low_count/total*100:.1f}%)")
        print(f"\nCompletion Rate: {completed_rate:.1f}%")
        print(f"Overall Progress: {'=' * int(completed_rate//5)}{' ' * (20 - int(completed_rate//5))}")


if __name__ == '__main__':
    app = TodoApp()
    app.run()