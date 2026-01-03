"""
Todo List Application
A simple command-line todo list manager with task management features.
"""

import json
import os
import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class Priority(Enum):
    """Task priority levels."""
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    
    def __str__(self):
        return self.name


class Task:
    """Represents a single task in the todo list."""
    
    def __init__(self, task_id: int, title: str, description: str = "",
                 priority: Priority = Priority.MEDIUM,
                 due_date: Optional[str] = None, completed: bool = False,
                 category: str = "General"):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.completed = completed
        self.category = category
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "due_date": self.due_date,
            "completed": self.completed,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task from dictionary."""
        priority_map = {1: Priority.LOW, 2: Priority.MEDIUM, 3: Priority.HIGH}
        return cls(
            task_id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=priority_map.get(data["priority"], Priority.MEDIUM),
            due_date=data.get("due_date"),
            completed=data.get("completed", False),
            category=data.get("category", "General")
        )
    
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date:
            return False
        try:
            due = datetime.datetime.strptime(self.due_date, "%Y-%m-%d").date()
            return due < datetime.date.today() and not self.completed
        except ValueError:
            return False
    
    def __str__(self) -> str:
        status = "[X]" if self.completed else "[ ]"
        overdue_str = " (OVERDUE!)" if self.is_overdue() else ""
        return f"{status} [{self.priority}] {self.title}{overdue_str}"
    
    def display_details(self) -> str:
        """Return detailed task information."""
        status = "Completed" if self.completed else "Pending"
        overdue = "Yes" if self.is_overdue() else "No"
        due = self.due_date if self.due_date else "Not set"
        return (
            f"ID: {self.id}\n"
            f"Title: {self.title}\n"
            f"Description: {self.description}\n"
            f"Priority: {self.priority}\n"
            f"Category: {self.category}\n"
            f"Due Date: {due}\n"
            f"Status: {status}\n"
            f"Overdue: {overdue}\n"
            f"Created: {self.created_at}"
        )


class TodoList:
    """Manages a collection of tasks with CRUD operations."""
    
    def __init__(self, storage_file: str = "tasks.json"):
        self.tasks: List[Task] = []
        self.storage_file = storage_file
        self.next_id = 1
        self.load_tasks()
    
    def load_tasks(self) -> None:
        """Load tasks from JSON file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data]
                    if self.tasks:
                        self.next_id = max(t.id for t in self.tasks) + 1
                    else:
                        self.next_id = 1
            except (json.JSONDecodeError, IOError):
                self.tasks = []
                self.next_id = 1
    
    def save_tasks(self) -> None:
        """Save tasks to JSON file."""
        data = [task.to_dict() for task in self.tasks]
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_task(self, title: str, description: str = "",
                 priority: Priority = Priority.MEDIUM,
                 due_date: Optional[str] = None,
                 category: str = "General") -> Task:
        """Create and add a new task."""
        task = Task(
            task_id=self.next_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category
        )
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return task
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Find task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task attributes."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        valid_fields = ['title', 'description', 'priority', 'due_date', 'category', 'completed']
        for key, value in kwargs.items():
            if key in valid_fields:
                if key == 'priority' and isinstance(value, str):
                    value = Priority[value.upper()]
                setattr(task, key, value)
        
        task.updated_at = datetime.datetime.now().isoformat()
        self.save_tasks()
        return True
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a single task."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        self.tasks.remove(task)
        self.save_tasks()
        return True
    
    def delete_completed(self) -> int:
        """Delete all completed tasks. Returns count of deleted tasks."""
        completed = [t for t in self.tasks if t.completed]
        count = len(completed)
        self.tasks = [t for t in self.tasks if not t.completed]
        self.save_tasks()
        return count
    
    def toggle_task(self, task_id: int) -> bool:
        """Toggle task completion status."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        task.completed = not task.completed
        task.updated_at = datetime.datetime.now().isoformat()
        self.save_tasks()
        return True
    
    def list_tasks(self, sort_by: str = "id", reverse: bool = False,
                   filter_completed: Optional[bool] = None,
                   filter_category: Optional[str] = None,
                   filter_priority: Optional[Priority] = None) -> List[Task]:
        """Get filtered and sorted task list."""
        result = self.tasks[:]
        
        if filter_completed is not None:
            result = [t for t in result if t.completed == filter_completed]
        
        if filter_category:
            result = [t for t in result if t.category.lower() == filter_category.lower()]
        
        if filter_priority:
            result = [t for t in result if t.priority == filter_priority]
        
        sort_keys = {
            "id": lambda t: t.id,
            "priority": lambda t: t.priority.value,
            "due_date": lambda t: t.due_date or "9999-12-31",
            "category": lambda t: t.category.lower(),
            "title": lambda t: t.title.lower()
        }
        
        if sort_by in sort_keys:
            result.sort(key=sort_keys[sort_by], reverse=reverse)
        
        return result
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        return sorted(set(t.category for t in self.tasks))
    
    def get_statistics(self) -> Dict[str, int]:
        """Get task statistics."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        overdue = sum(1 for t in self.tasks if t.is_overdue())
        high_priority = sum(1 for t in self.tasks if t.priority == Priority.HIGH and not t.completed)
        
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "overdue": overdue,
            "high_priority": high_priority
        }


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def print_menu() -> None:
    """Print the main menu."""
    print("\n--- TODO LIST MENU ---")
    print("1.  View all tasks")
    print("2.  Add new task")
    print("3.  View task details")
    print("4.  Edit task")
    print("5.  Toggle task completion")
    print("6.  Delete task")
    print("7.  Delete completed tasks")
    print("8.  Filter and sort tasks")
    print("9.  View statistics")
    print("10. View categories")
    print("0.  Exit")
    print("----------------------")


def get_input(prompt: str, required: bool = True) -> str:
    """Get user input with optional requirement."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required. Please try again.")


def get_priority() -> Priority:
    """Get priority selection from user."""
    print("Select priority: 1=Low, 2=Medium, 3=High")
    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice == "1":
            return Priority.LOW
        elif choice == "2":
            return Priority.MEDIUM
        elif choice == "3":
            return Priority.HIGH
        print("Invalid choice. Please enter 1, 2, or 3.")


def validate_date(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD."""
    if not date_str:
        return True
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def add_new_task(todo_list: TodoList) -> None:
    """Handle adding a new task."""
    print_header("Add New Task")
    
    title = get_input("Enter task title: ")
    description = input("Enter description (optional): ").strip()
    priority = get_priority()
    due_date = ""
    while due_date is not None:
        due_date = input("Enter due date (YYYY-MM-DD, or press Enter to skip): ").strip()
        if not due_date:
            due_date = None
            break
        if validate_date(due_date):
            break
        print("Invalid date format. Please use YYYY-MM-DD.")
    
    categories = todo_list.get_categories()
    if categories:
        print(f"Available categories: {', '.join(categories)}")
    category = input("Enter category (or press Enter for 'General'): ").strip()
    if not category:
        category = "General"
    
    task = todo_list.add_task(title, description, priority, due_date, category)
    print(f"\nTask added successfully! ID: {task.id}")


def view_task_details(todo_list: TodoList) -> None:
    """View detailed task information."""
    print_header("Task Details")
    task_id = get_input("Enter task ID: ")
    if not task_id.isdigit():
        print("Invalid task ID.")
        return
    
    task = todo_list.get_task_by_id(int(task_id))
    if not task:
        print("Task not found.")
        return
    
    print(f"\n{task.display_details()}")


def edit_task(todo_list: TodoList) -> None:
    """Edit an existing task."""
    print_header("Edit Task")
    task_id = get_input("Enter task ID to edit: ")
    if not task_id.isdigit():
        print("Invalid task ID.")
        return
    
    task = todo_list.get_task_by_id(int(task_id))
    if not task:
        print("Task not found.")
        return
    
    print(f"\nCurrent task: {task}")
    print("Leave field empty to keep current value.\n")
    
    new_title = input(f"New title [{task.title}]: ").strip()
    new_desc = input(f"New description [{task.description}]: ").strip()
    
    print("New priority:")
    new_priority_str = input(f"  (current: {task.priority}) Change? (y/n): ").strip().lower()
    new_priority = task.priority
    if new_priority_str == 'y':
        new_priority = get_priority()
    
    new_due = input(f"New due date (YYYY-MM-DD) [{task.due_date or 'not set'}]: ").strip()
    if new_due and not validate_date(new_due):
        print("Invalid date format. Due date not changed.")
        new_due = task.due_date
    
    new_cat = input(f"New category [{task.category}]: ").strip()
    
    updates = {}
    if new_title:
        updates['title'] = new_title
    if new_desc:
        updates['description'] = new_desc
    if new_priority != task.priority:
        updates['priority'] = new_priority
    if new_due:
        updates['due_date'] = new_due
    if new_cat:
        updates['category'] = new_cat
    
    if updates:
        if todo_list.update_task(task.id, **updates):
            print("Task updated successfully!")
        else:
            print("Failed to update task.")
    else:
        print("No changes made.")


def toggle_task_completion(todo_list: TodoList) -> None:
    """Toggle task completion status."""
    print_header("Toggle Task Completion")
    task_id = get_input("Enter task ID: ")
    if not task_id.isdigit():
        print("Invalid task ID.")
        return
    
    if todo_list.toggle_task(int(task_id)):
        task = todo_list.get_task_by_id(int(task_id))
        status = "completed" if task.completed else "pending"
        print(f"Task marked as {status}.")
    else:
        print("Task not found.")


def delete_task(todo_list: TodoList) -> None:
    """Delete a single task."""
    print_header("Delete Task")
    task_id = get_input("Enter task ID to delete: ")
    if not task_id.isdigit():
        print("Invalid task ID.")
        return
    
    confirm = input("Are you sure? (y/n): ").strip().lower()
    if confirm == 'y':
        if todo_list.delete_task(int(task_id)):
            print("Task deleted successfully.")
        else:
            print("Task not found.")
    else:
        print("Deletion cancelled.")


def delete_completed_tasks(todo_list: TodoList) -> None:
    """Delete all completed tasks."""
    print_header("Delete Completed Tasks")
    stats = todo_list.get_statistics()
    if stats['completed'] == 0:
        print("No completed tasks to delete.")
        return
    
    print(f"You have {stats['completed']} completed task(s).")
    confirm = input("Delete all completed tasks? (y/n): ").strip().lower()
    if confirm == 'y':
        count = todo_list.delete_completed()
        print(f"Deleted {count} completed task(s).")
    else:
        print("Deletion cancelled.")


def filter_and_sort_tasks(todo_list: TodoList) -> None:
    """Filter and sort tasks display."""
    print_header("Filter and Sort Tasks")
    
    print("Sort by: 1=ID, 2=Priority, 3=Due Date, 4=Category, 5=Title")
    sort_choice = input("Enter choice (1-5, default=1): ").strip()
    sort_map = {"1": "id", "2": "priority", "3": "due_date", "4": "category", "5": "title"}
    sort_by = sort_map.get(sort_choice, "id")
    
    reverse = input("Reverse order? (y/n, default=n): ").strip().lower() == 'y'
    
    print("\nFilter by status: 1=All, 2=Pending only, 3=Completed only")
    filter_choice = input("Enter choice (1-3): ").strip()
    filter_map = {"1": None, "2": False, "3": True}
    filter_completed = filter_map.get(filter_choice)
    
    filter_cat = input("\nFilter by category (press Enter for all): ").strip() or None
    
    print("\nFilter by priority: 1=All, 2=High, 3=Medium, 4=Low")
    pri_choice = input("Enter choice (1-4): ").strip()
    pri_map = {"1": None, "2": Priority.HIGH, "3": Priority.MEDIUM, "4": Priority.LOW}
    filter_priority = pri_map.get(pri_choice)
    
    tasks = todo_list.list_tasks(
        sort_by=sort_by,
        reverse=reverse,
        filter_completed=filter_completed,
        filter_category=filter_cat,
        filter_priority=filter_priority
    )
    
    print_header(f"Tasks ({len(tasks)} items)")
    if not tasks:
        print("No tasks match your criteria.")
    else:
        for task in tasks:
            print(f"  {task}")


def view_statistics(todo_list: TodoList) -> None:
    """Display task statistics."""
    print_header("Task Statistics")
    stats = todo_list.get_statistics()
    
    print(f"Total tasks:      {stats['total']}")
    print(f"Completed:        {stats['completed']}")
    print(f"Pending:          {stats['pending']}")
    print(f"Overdue:          {stats['overdue']}")
    print(f"High priority:    {stats['high_priority']}")


def view_categories(todo_list: TodoList) -> None:
    """Display all categories."""
    print_header("Categories")
    categories = todo_list.get_categories()
    
    if not categories:
        print("No categories yet.")
    else:
        print("Available categories:")
        for cat in categories:
            count = sum(1 for t in todo_list.tasks if t.category == cat)
            print(f"  - {cat} ({count} task(s))")


def display_all_tasks(todo_list: TodoList) -> None:
    """Display all tasks in a simple list."""
    print_header("All Tasks")
    tasks = todo_list.list_tasks()
    
    if not tasks:
        print("No tasks yet. Add your first task!")
    else:
        for task in tasks:
            print(f"  {task}")


def main():
    """Main application entry point."""
    clear_screen()
    print_header("Welcome to Todo List App!")
    print("A simple command-line task manager")
    print("Your tasks are automatically saved to 'tasks.json'\n")
    
    todo_list = TodoList()
    
    # Add some sample tasks if list is empty
    if not todo_list.tasks:
        print("Creating sample tasks for demonstration...")
        todo_list.add_task("Learn Python", "Study Python basics and advanced features",
                          Priority.HIGH, "2025-12-31", "Learning")
        todo_list.add_task("Buy groceries", "Milk, bread, eggs, and vegetables",
                          Priority.LOW, "2025-01-15", "Personal")
        todo_list.add_task("Finish project", "Complete the todo list application",
                          Priority.HIGH, "2025-01-20", "Work")
        todo_list.add_task("Read book", "Read 'Python Cookbook'",
                          Priority.MEDIUM, None, "Learning")
        print("Sample tasks created!\n")
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (0-10): ").strip()
        
        if choice == "0":
            print("\nThank you for using Todo List App!")
            print("Goodbye!")
            break
        
        elif choice == "1":
            display_all_tasks(todo_list)
        
        elif choice == "2":
            add_new_task(todo_list)
        
        elif choice == "3":
            view_task_details(todo_list)
        
        elif choice == "4":
            edit_task(todo_list)
        
        elif choice == "5":
            toggle_task_completion(todo_list)
        
        elif choice == "6":
            delete_task(todo_list)
        
        elif choice == "7":
            delete_completed_tasks(todo_list)
        
        elif choice == "8":
            filter_and_sort_tasks(todo_list)
        
        elif choice == "9":
            view_statistics(todo_list)
        
        elif choice == "10":
            view_categories(todo_list)
        
        else:
            print("\nInvalid choice. Please enter a number between 0 and 10.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()