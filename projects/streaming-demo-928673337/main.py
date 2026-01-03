"""
Todo List Application
A simple command-line todo list manager with priority, categories, search, and filtering.
"""

import json
import os
from datetime import datetime
from enum import Enum


class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    
    @classmethod
    def from_string(cls, s):
        """Convert string to Priority enum."""
        mapping = {
            "1": cls.LOW,
            "2": cls.MEDIUM,
            "3": cls.HIGH,
            "low": cls.LOW,
            "medium": cls.MEDIUM,
            "high": cls.HIGH
        }
        return mapping.get(s.lower(), cls.MEDIUM)
    
    def __str__(self):
        """Return human-readable priority name."""
        return self.name.capitalize()


class Task:
    """Represents a single todo task."""
    
    def __init__(self, title, description="", priority=Priority.MEDIUM, 
                 category="General", due_date=None):
        self.id = self._generate_id()
        self.title = title
        self.description = description
        self.priority = priority
        self.category = category
        self.due_date = due_date
        self.completed = False
        self.created_at = datetime.now()
    
    def _generate_id(self):
        """Generate unique task identifier based on timestamp."""
        return int(datetime.now().timestamp() * 1000000)
    
    def mark_complete(self):
        """Mark task as completed."""
        self.completed = True
    
    def mark_incomplete(self):
        """Mark task as incomplete."""
        self.completed = False
    
    def update(self, title=None, description=None, priority=None, 
               category=None, due_date=None):
        """Update task attributes."""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        if category is not None:
            self.category = category
        if due_date is not None:
            self.due_date = due_date
    
    def is_overdue(self):
        """Check if task is overdue."""
        if self.due_date is None:
            return False
        return datetime.now() > self.due_date
    
    def to_dict(self):
        """Convert task to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "category": self.category,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create task from dictionary."""
        task = cls.__new__(cls)
        task.id = data["id"]
        task.title = data["title"]
        task.description = data.get("description", "")
        task.priority = Priority(data["priority"])
        task.category = data.get("category", "General")
        due_date_str = data.get("due_date")
        task.due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
        task.completed = data.get("completed", False)
        created_at_str = data.get("created_at")
        task.created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.now()
        return task
    
    def __str__(self):
        """Return string representation of task."""
        status = "[X]" if self.completed else "[ ]"
        due_str = f" (Due: {self.due_date.strftime('%Y-%m-%d')})" if self.due_date else ""
        overdue_str = " (OVERDUE!)" if self.is_overdue() and not self.completed else ""
        return f"{status} [{self.priority}] {self.title}{due_str}{overdue_str}"


class TodoList:
    """Manages a collection of tasks."""
    
    def __init__(self, filename="tasks.json"):
        """Initialize todo list with file storage."""
        self.filename = filename
        self.tasks = []
        self.load_tasks()
    
    def add_task(self, task):
        """Add a new task to the list."""
        self.tasks.append(task)
        self.save_tasks()
    
    def get_task(self, task_id):
        """Get task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_all_tasks(self):
        """Return all tasks."""
        return self.tasks
    
    def update_task(self, task_id, **kwargs):
        """Update task attributes."""
        task = self.get_task(task_id)
        if task:
            task.update(**kwargs)
            self.save_tasks()
            return True
        return False
    
    def delete_task(self, task_id):
        """Delete task by ID."""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            return True
        return False
    
    def mark_complete(self, task_id):
        """Mark task as completed."""
        task = self.get_task(task_id)
        if task:
            task.mark_complete()
            self.save_tasks()
            return True
        return False
    
    def mark_incomplete(self, task_id):
        """Mark task as incomplete."""
        task = self.get_task(task_id)
        if task:
            task.mark_incomplete()
            self.save_tasks()
            return True
        return False
    
    def get_tasks_by_status(self, completed):
        """Get tasks filtered by completion status."""
        return [t for t in self.tasks if t.completed == completed]
    
    def get_tasks_by_priority(self, priority):
        """Get tasks filtered by priority."""
        return [t for t in self.tasks if t.priority == priority]
    
    def get_tasks_by_category(self, category):
        """Get tasks filtered by category."""
        return [t for t in self.tasks if t.category.lower() == category.lower()]
    
    def search_tasks(self, query):
        """Search tasks by keyword in title or description."""
        query_lower = query.lower()
        return [t for t in self.tasks 
                if query_lower in t.title.lower() or query_lower in t.description.lower()]
    
    def sort_tasks(self, sort_by="created_at", reverse=True):
        """Return sorted list of tasks."""
        sort_keys = {
            "created_at": lambda t: t.created_at,
            "priority": lambda t: t.priority.value,
            "due_date": lambda t: t.due_date if t.due_date else datetime.min,
            "title": lambda t: t.title.lower()
        }
        
        if sort_by not in sort_keys:
            sort_by = "created_at"
        
        return sorted(self.tasks, key=sort_keys[sort_by], reverse=reverse)
    
    def get_categories(self):
        """Get all unique categories."""
        return list(set(t.category for t in self.tasks))
    
    def save_tasks(self):
        """Save tasks to JSON file."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2, ensure_ascii=False)
    
    def load_tasks(self):
        """Load tasks from JSON file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data]
            except (json.JSONDecodeError, IOError):
                self.tasks = []
        else:
            self.tasks = []
    
    def get_stats(self):
        """Get task statistics."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.completed)
        pending = total - completed
        overdue = sum(1 for t in self.tasks if t.is_overdue() and not t.completed)
        by_priority = {p.name: sum(1 for t in self.tasks if t.priority == p) for p in Priority}
        categories = self.get_categories()
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "by_priority": by_priority,
            "categories": categories
        }


def get_date_input(prompt):
    """Get valid date input from user."""
    while True:
        date_str = input(prompt).strip()
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")


def create_task_from_input():
    """Create a new task from user input."""
    print("\n--- Create New Task ---")
    
    title = input("Enter task title: ").strip()
    while not title:
        print("Title cannot be empty.")
        title = input("Enter task title: ").strip()
    
    description = input("Enter task description (optional): ").strip()
    
    print("Select priority: 1=Low, 2=Medium, 3=High")
    priority_input = input("Priority [2]: ").strip()
    priority = Priority.from_string(priority_input) if priority_input else Priority.MEDIUM
    
    category = input("Enter category [General]: ").strip()
    if not category:
        category = "General"
    
    due_date = get_date_input("Enter due date (YYYY-MM-DD, optional): ")
    
    return Task(title, description, priority, category, due_date)


def display_tasks(tasks, title="Tasks"):
    """Display list of tasks."""
    if not tasks:
        print(f"\nNo {title.lower()} to display.")
        return
    
    print(f"\n--- {title} ({len(tasks)}) ---")
    for i, task in enumerate(tasks, 1):
        due_str = ""
        if task.due_date:
            due_str = f" | Due: {task.due_date.strftime('%Y-%m-%d')}"
            if task.is_overdue() and not task.completed:
                due_str += " (OVERDUE!)"
        
        cat_str = f" | Category: {task.category}"
        desc_str = f"\n     Description: {task.description}" if task.description else ""
        
        print(f"{i}. [{task.priority}]{' [DONE]' if task.completed else ''} {task.title}{due_str}{cat_str}{desc_str}")


def display_stats(stats):
    """Display task statistics."""
    print("\n--- Statistics ---")
    print(f"Total Tasks: {stats['total']}")
    print(f"Completed: {stats['completed']}")
    print(f"Pending: {stats['pending']}")
    print(f"Overdue: {stats['overdue']}")
    print("By Priority:")
    for name, count in stats['by_priority'].items():
        print(f"  {name}: {count}")
    print(f"Categories: {', '.join(stats['categories']) if stats['categories'] else 'None'}")


def main():
    """Main application entry point."""
    print("=" * 50)
    print("       WELCOME TO TODO LIST MANAGER")
    print("=" * 50)
    
    todo_list = TodoList()
    
    if not os.path.exists(todo_list.filename):
        print("\nNo existing data found. Starting with empty list.")
    
    sample_tasks_created = False
    if len(todo_list.get_all_tasks()) == 0:
        print("\nCreating sample tasks for demonstration...")
        sample_tasks = [
            Task("Learn Python", "Complete the Python tutorial", Priority.HIGH, "Learning"),
            Task("Buy groceries", "Milk, Bread, Eggs, Butter", Priority.LOW, "Personal"),
            Task("Finish project", "Submit before deadline", Priority.HIGH, "Work", 
                 datetime.now().replace(day=datetime.now().day + 3)),
            Task("Read book", "Chapter 5-10", Priority.MEDIUM, "Personal"),
            Task("Clean room", "Organize desk and closet", Priority.LOW, "Personal", 
                 datetime.now().replace(day=datetime.now().day + 7))
        ]
        for task in sample_tasks:
            todo_list.add_task(task)
        sample_tasks_created = True
    
    if sample_tasks_created:
        print("Sample tasks created successfully!")
    
    while True:
        print("\n" + "=" * 50)
        print("       TODO LIST - MAIN MENU")
        print("=" * 50)
        print("1. View All Tasks")
        print("2. View Pending Tasks")
        print("3. View Completed Tasks")
        print("4. Create New Task")
        print("5. Update Task")
        print("6. Delete Task")
        print("7. Mark Task as Complete")
        print("8. Mark Task as Incomplete")
        print("9. Search Tasks")
        print("10. Filter by Category")
        print("11. Sort Tasks")
        print("12. View Statistics")
        print("13. Exit")
        print("=" * 50)
        
        choice = input("Enter your choice (1-13): ").strip()
        
        if choice == "1":
            tasks = todo_list.get_all_tasks()
            display_tasks(tasks, "All Tasks")
        
        elif choice == "2":
            tasks = todo_list.get_tasks_by_status(False)
            display_tasks(tasks, "Pending Tasks")
        
        elif choice == "3":
            tasks = todo_list.get_tasks_by_status(True)
            display_tasks(tasks, "Completed Tasks")
        
        elif choice == "4":
            task = create_task_from_input()
            todo_list.add_task(task)
            print(f"\nTask '{task.title}' created successfully!")
        
        elif choice == "5":
            tasks = todo_list.get_all_tasks()
            if not tasks:
                print("\nNo tasks available to update.")
            else:
                display_tasks(tasks, "All Tasks")
                try:
                    idx = int(input("\nEnter task number to update: ")) - 1
                    if 0 <= idx < len(tasks):
                        task = tasks[idx]
                        print(f"Updating: {task.title}")
                        new_title = input(f"New title [{task.title}]: ").strip()
                        new_desc = input(f"New description [{task.description}]: ").strip()
                        print("New priority (1=Low, 2=Medium, 3=High) [current]: ")
                        new_priority_input = input("").strip()
                        new_category = input(f"New category [{task.category}]: ").strip()
                        new_due = get_date_input(f"New due date [current: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'none'}]: ")
                        
                        todo_list.update_task(
                            task.id,
                            title=new_title if new_title else None,
                            description=new_desc if new_desc else None,
                            priority=Priority.from_string(new_priority_input) if new_priority_input else None,
                            category=new_category if new_category else None,
                            due_date=new_due
                        )
                        print("Task updated successfully!")
                    else:
                        print("Invalid task number.")
                except ValueError:
                    print("Please enter a valid number.")
        
        elif choice == "6":
            tasks = todo_list.get_all_tasks()
            if not tasks:
                print("\nNo tasks available to delete.")
            else:
                display_tasks(tasks, "All Tasks")
                try:
                    idx = int(input("\nEnter task number to delete: ")) - 1
                    if 0 <= idx < len(tasks):
                        task = tasks[idx]
                        confirm = input(f"Delete '{task.title}'? (y/n): ").lower()
                        if confirm == 'y':
                            todo_list.delete_task(task.id)
                            print("Task deleted successfully!")
                    else:
                        print("Invalid task number.")
                except ValueError:
                    print("Please enter a valid number.")
        
        elif choice == "7":
            tasks = todo_list.get_tasks_by_status(False)
            if not tasks:
                print("\nNo pending tasks to complete.")
            else:
                display_tasks(tasks, "Pending Tasks")
                try:
                    idx = int(input("\nEnter task number to mark complete: ")) - 1
                    if 0 <= idx < len(tasks):
                        task = tasks[idx]
                        todo_list.mark_complete(task.id)
                        print(f"Task '{task.title}' marked as complete!")
                    else:
                        print("Invalid task number.")
                except ValueError:
                    print("Please enter a valid number.")
        
        elif choice == "8":
            tasks = todo_list.get_tasks_by_status(True)
            if not tasks:
                print("\nNo completed tasks to mark as incomplete.")
            else:
                display_tasks(tasks, "Completed Tasks")
                try:
                    idx = int(input("\nEnter task number to mark incomplete: ")) - 1
                    if 0 <= idx < len(tasks):
                        task = tasks[idx]
                        todo_list.mark_incomplete(task.id)
                        print(f"Task '{task.title}' marked as incomplete!")
                    else:
                        print("Invalid task number.")
                except ValueError:
                    print("Please enter a valid number.")
        
        elif choice == "9":
            query = input("\nEnter search keyword: ").strip()
            if query:
                results = todo_list.search_tasks(query)
                display_tasks(results, f"Search Results for '{query}'")
            else:
                print("Please enter a search keyword.")
        
        elif choice == "10":
            categories = todo_list.get_categories()
            if not categories:
                print("\nNo categories available.")
            else:
                print(f"\nAvailable categories: {', '.join(categories)}")
                category = input("Enter category name: ").strip()
                if category:
                    tasks = todo_list.get_tasks_by_category(category)
                    display_tasks(tasks, f"Tasks in '{category}'")
        
        elif choice == "11":
            print("\nSort by: 1=Created Date, 2=Priority, 3=Due Date, 4=Title")
            sort_choice = input("Enter choice: ").strip()
            sort_map = {"1": "created_at", "2": "priority", "3": "due_date", "4": "title"}
            sort_by = sort_map.get(sort_choice, "created_at")
            
            reverse_choice = input("Order: 1=Descending, 2=Ascending [1]: ").strip()
            reverse = reverse_choice != "2"
            
            tasks = todo_list.sort_tasks(sort_by, reverse)
            order_name = "Descending" if reverse else "Ascending"
            display_tasks(tasks, f"Sorted by {sort_by.capitalize()} ({order_name})")
        
        elif choice == "12":
            stats = todo_list.get_stats()
            display_stats(stats)
        
        elif choice == "13":
            print("\nThank you for using Todo List Manager!")
            print("Your tasks have been saved automatically.")
            break
        
        else:
            print("\nInvalid choice. Please enter a number from 1 to 13.")


if __name__ == "__main__":
    main()