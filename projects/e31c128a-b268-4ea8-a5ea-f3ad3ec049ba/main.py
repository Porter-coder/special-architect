"""
Todo List Manager System
A simple and efficient task management application with categories, tags, and reminders.
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Optional
import uuid


# ==================== Data Models ====================

class Tag:
    """Represents a tag that can be applied to tasks."""
    
    def __init__(self, name: str, color: str = "#3498db"):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.color = color
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Tag":
        tag = cls(data["name"], data.get("color", "#3498db"))
        tag.id = data["id"]
        tag.created_at = data["created_at"]
        return tag


class Category:
    """Represents a category for organizing tasks."""
    
    def __init__(self, name: str, description: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        category = cls(data["name"], data.get("description", ""))
        category.id = data["id"]
        category.created_at = data["created_at"]
        return category


class Task:
    """Represents a task in the todo list."""
    
    STATUS_PENDING = "Pending"
    STATUS_IN_PROGRESS = "In Progress"
    STATUS_COMPLETED = "Completed"
    STATUS_ARCHIVED = "Archived"
    
    PRIORITY_LOW = "Low"
    PRIORITY_MEDIUM = "Medium"
    PRIORITY_HIGH = "High"
    PRIORITY_URGENT = "Urgent"
    
    def __init__(
        self,
        title: str,
        description: str = "",
        priority: str = PRIORITY_MEDIUM,
        deadline: Optional[str] = None,
        category_id: Optional[str] = None,
        tag_ids: Optional[list] = None
    ):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.description = description
        self.priority = priority
        self.status = Task.STATUS_PENDING
        self.deadline = deadline
        self.category_id = category_id
        self.tag_ids = tag_ids if tag_ids else []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.completed_at = None
    
    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if not self.deadline:
            return False
        try:
            deadline_dt = datetime.fromisoformat(self.deadline)
            return deadline_dt < datetime.now() and self.status != Task.STATUS_COMPLETED
        except (ValueError, TypeError):
            return False
    
    def mark_completed(self):
        """Mark the task as completed."""
        self.status = Task.STATUS_COMPLETED
        self.completed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def update_status(self, new_status: str):
        """Update the task status."""
        valid_statuses = [
            Task.STATUS_PENDING,
            Task.STATUS_IN_PROGRESS,
            Task.STATUS_COMPLETED,
            Task.STATUS_ARCHIVED
        ]
        if new_status in valid_statuses:
            self.status = new_status
            if new_status == Task.STATUS_COMPLETED:
                self.completed_at = datetime.now().isoformat()
            self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "deadline": self.deadline,
            "category_id": self.category_id,
            "tag_ids": self.tag_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        task = cls(
            data["title"],
            data.get("description", ""),
            data.get("priority", Task.PRIORITY_MEDIUM),
            data.get("deadline"),
            data.get("category_id"),
            data.get("tag_ids", [])
        )
        task.id = data["id"]
        task.status = data.get("status", Task.STATUS_PENDING)
        task.created_at = data.get("created_at", datetime.now().isoformat())
        task.updated_at = data.get("updated_at", datetime.now().isoformat())
        task.completed_at = data.get("completed_at")
        return task


# ==================== Storage Manager ====================

class StorageManager:
    """Handles data persistence using JSON files."""
    
    def __init__(self, data_file: str = "todos_data.json"):
        self.data_file = data_file
        self.data = {
            "tasks": [],
            "categories": [],
            "tags": []
        }
        self.load_data()
    
    def load_data(self):
        """Load data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = {"tasks": [], "categories": [], "tags": []}
    
    def save_data(self):
        """Save data to JSON file."""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving data: {e}")
    
    def get_tasks(self) -> list:
        return [Task.from_dict(t) for t in self.data.get("tasks", [])]
    
    def add_task(self, task: Task):
        self.data["tasks"].append(task.to_dict())
        self.save_data()
    
    def update_task(self, task_id: str, updated_task: Task):
        tasks = self.data.get("tasks", [])
        for i, t in enumerate(tasks):
            if t["id"] == task_id:
                tasks[i] = updated_task.to_dict()
                self.save_data()
                return True
        return False
    
    def delete_task(self, task_id: str) -> bool:
        tasks = self.data.get("tasks", [])
        for i, t in enumerate(tasks):
            if t["id"] == task_id:
                del tasks[i]
                self.save_data()
                return True
        return False
    
    def get_categories(self) -> list:
        return [Category.from_dict(c) for c in self.data.get("categories", [])]
    
    def add_category(self, category: Category):
        self.data["categories"].append(category.to_dict())
        self.save_data()
    
    def delete_category(self, category_id: str) -> bool:
        categories = self.data.get("categories", [])
        for i, c in enumerate(categories):
            if c["id"] == category_id:
                del categories[i]
                self.save_data()
                return True
        return False
    
    def get_tags(self) -> list:
        return [Tag.from_dict(t) for t in self.data.get("tags", [])]
    
    def add_tag(self, tag: Tag):
        self.data["tags"].append(tag.to_dict())
        self.save_data()
    
    def delete_tag(self, tag_id: str) -> bool:
        tags = self.data.get("tags", [])
        for i, t in enumerate(tags):
            if t["id"] == tag_id:
                del tags[i]
                self.save_data()
                return True
        return False


# ==================== Task Manager ====================

class TaskManager:
    """Main business logic for managing tasks."""
    
    def __init__(self):
        self.storage = StorageManager()
        self.reminder_active = False
    
    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = Task.PRIORITY_MEDIUM,
        deadline: Optional[str] = None,
        category_id: Optional[str] = None,
        tag_ids: Optional[list] = None
    ) -> Task:
        """Create a new task."""
        task = Task(title, description, priority, deadline, category_id, tag_ids)
        self.storage.add_task(task)
        return task
    
    def get_all_tasks(self) -> list:
        """Get all tasks."""
        return self.storage.get_tasks()
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        for task in self.get_all_tasks():
            if task.id == task_id:
                return task
        return None
    
    def get_tasks_by_status(self, status: str) -> list:
        """Get tasks filtered by status."""
        return [t for t in self.get_all_tasks() if t.status == status]
    
    def get_tasks_by_category(self, category_id: str) -> list:
        """Get tasks filtered by category."""
        return [t for t in self.get_all_tasks() if t.category_id == category_id]
    
    def get_tasks_by_tag(self, tag_id: str) -> list:
        """Get tasks filtered by tag."""
        return [t for t in self.get_all_tasks() if tag_id in t.tag_ids]
    
    def get_overdue_tasks(self) -> list:
        """Get all overdue tasks."""
        return [t for t in self.get_all_tasks() if t.is_overdue()]
    
    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        deadline: Optional[str] = None,
        category_id: Optional[str] = None,
        tag_ids: Optional[list] = None
    ) -> bool:
        """Update an existing task."""
        task = self.get_task_by_id(task_id)
        if not task:
            return False
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if status is not None:
            task.update_status(status)
        if deadline is not None:
            task.deadline = deadline
        if category_id is not None:
            task.category_id = category_id
        if tag_ids is not None:
            task.tag_ids = tag_ids
        
        task.updated_at = datetime.now().isoformat()
        return self.storage.update_task(task_id, task)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        return self.storage.delete_task(task_id)
    
    def bulk_update_status(self, task_ids: list, new_status: str) -> int:
        """Bulk update status for multiple tasks."""
        count = 0
        for task_id in task_ids:
            if self.update_task(task_id, status=new_status):
                count += 1
        return count
    
    def bulk_delete(self, task_ids: list) -> int:
        """Bulk delete multiple tasks."""
        count = 0
        for task_id in task_ids:
            if self.delete_task(task_id):
                count += 1
        return count
    
    # Category management
    def create_category(self, name: str, description: str = "") -> Category:
        """Create a new category."""
        category = Category(name, description)
        self.storage.add_category(category)
        return category
    
    def get_all_categories(self) -> list:
        """Get all categories."""
        return self.storage.get_categories()
    
    def delete_category(self, category_id: str) -> bool:
        """Delete a category."""
        return self.storage.delete_category(category_id)
    
    # Tag management
    def create_tag(self, name: str, color: str = "#3498db") -> Tag:
        """Create a new tag."""
        tag = Tag(name, color)
        self.storage.add_tag(tag)
        return tag
    
    def get_all_tags(self) -> list:
        """Get all tags."""
        return self.storage.get_tags()
    
    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag."""
        return self.storage.delete_tag(tag_id)
    
    # Statistics
    def get_statistics(self) -> dict:
        """Get task statistics."""
        tasks = self.get_all_tasks()
        return {
            "total": len(tasks),
            "pending": len([t for t in tasks if t.status == Task.STATUS_PENDING]),
            "in_progress": len([t for t in tasks if t.status == Task.STATUS_IN_PROGRESS]),
            "completed": len([t for t in tasks if t.status == Task.STATUS_COMPLETED]),
            "archived": len([t for t in tasks if t.status == Task.STATUS_ARCHIVED]),
            "overdue": len(self.get_overdue_tasks())
        }
    
    # Reminder system
    def start_reminder_check(self, interval: int = 60):
        """Start background thread for checking reminders."""
        self.reminder_active = True
        thread = threading.Thread(target=self._reminder_loop, args=(interval,), daemon=True)
        thread.start()
    
    def _reminder_loop(self, interval: int):
        """Background loop to check for due tasks."""
        while self.reminder_active:
            overdue = self.get_overdue_tasks()
            if overdue:
                print("\n" + "=" * 50)
                print(f"WARNING: You have {len(overdue)} overdue task(s)!")
                for task in overdue[:3]:  # Show first 3
                    print(f"  - [{task.priority}] {task.title}")
                if len(overdue) > 3:
                    print(f"  ... and {len(overdue) - 3} more")
                print("=" * 50 + "\n")
            time.sleep(interval)


# ==================== CLI Interface ====================

class CLIInterface:
    """Command-line interface for the todo manager."""
    
    def __init__(self):
        self.manager = TaskManager()
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 50)
        print(f"  {title}")
        print("=" * 50)
    
    def print_menu(self, options: list, title: str = "Main Menu"):
        """Print a numbered menu."""
        self.print_header(title)
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print("  0. Back/Exit")
        print("")
    
    def get_input(self, prompt: str) -> str:
        """Get user input."""
        return input(f"  {prompt}: ").strip()
    
    def get_int_input(self, prompt: str, default: int = 0) -> int:
        """Get integer input."""
        while True:
            try:
                value = input(f"  {prompt}: ").strip()
                return int(value) if value else default
            except ValueError:
                print("  Please enter a valid number.")
    
    def print_tasks(self, tasks: list, show_details: bool = False):
        """Print a list of tasks."""
        if not tasks:
            print("  No tasks found.")
            return
        
        categories = {c.id: c.name for c in self.manager.get_all_categories()}
        tags = {t.id: t.name for t in self.manager.get_all_tags()}
        
        for i, task in enumerate(tasks, 1):
            status_icon = {
                Task.STATUS_PENDING: "[ ]",
                Task.STATUS_IN_PROGRESS: "[~]",
                Task.STATUS_COMPLETED: "[X]",
                Task.STATUS_ARCHIVED: "[-]"
            }.get(task.status, "[?]")
            
            overdue标记 = " (!OVERDUE)" if task.is_overdue() else ""
            
            category_name = categories.get(task.category_id, "Uncategorized")
            tag_names = [tags.get(tid, "") for tid in task.tag_ids if tid in tags]
            tag_str = f" | Tags: {', '.join(tag_names)}" if tag_names else ""
            
            print(f"  {i}. {status_icon} {task.title}{overdue标记}")
            print(f"     ID: {task.id} | Priority: {task.priority} | Status: {task.status}")
            print(f"     Category: {category_name}{tag_str}")
            
            if task.deadline:
                print(f"     Deadline: {task.deadline}")
            
            if show_details and task.description:
                print(f"     Description: {task.description}")
            print()
    
    def print_statistics(self):
        """Print task statistics."""
        stats = self.manager.get_statistics()
        print("\n  Task Statistics:")
        print(f"    Total Tasks:    {stats['total']}")
        print(f"    Pending:        {stats['pending']}")
        print(f"    In Progress:    {stats['in_progress']}")
        print(f"    Completed:      {stats['completed']}")
        print(f"    Archived:       {stats['archived']}")
        print(f"    Overdue:        {stats['overdue']}\n")
    
    def create_sample_data(self):
        """Create sample data for demonstration."""
        # Create categories
        cat_work = self.manager.create_category("Work", "Work-related tasks")
        cat_personal = self.manager.create_category("Personal", "Personal tasks")
        cat_study = self.manager.create_category("Study", "Learning and study tasks")
        
        # Create tags
        tag_important = self.manager.create_tag("Important", "#e74c3c")
        tag_urgent = self.manager.create_tag("Urgent", "#f39c12")
        tag_idea = self.manager.create_tag("Idea", "#9b59b6")
        
        # Create sample tasks
        self.manager.create_task(
            "Complete project report",
            "Write and submit the quarterly project report",
            Task.PRIORITY_HIGH,
            (datetime.now() + timedelta(days=2)).isoformat(),
            cat_work.id,
            [tag_important.id, tag_urgent.id]
        )
        
        self.manager.create_task(
            "Read Python documentation",
            "Review the new Python 3.12 features",
            Task.PRIORITY_MEDIUM,
            (datetime.now() + timedelta(days=5)).isoformat(),
            cat_study.id,
            [tag_idea.id]
        )
        
        self.manager.create_task(
            "Buy groceries",
            "Milk, bread, eggs, and vegetables",
            Task.PRIORITY_LOW,
            datetime.now().isoformat(),  # Today
            cat_personal.id
        )
        
        self.manager.create_task(
            "Prepare presentation",
            "Create slides for Monday's meeting",
            Task.PRIORITY_HIGH,
            (datetime.now() - timedelta(days=1)).isoformat(),  # Yesterday - overdue
            cat_work.id,
            [tag_important.id]
        )
        
        self.manager.create_task(
            "Exercise",
            "30 minutes cardio workout",
            Task.PRIORITY_MEDIUM,
            None,
            cat_personal.id
        )
        
        print("  Sample data created successfully!\n")
    
    def task_menu(self):
        """Task management menu."""
        while True:
            self.print_menu([
                "View All Tasks",
                "View by Status",
                "View Overdue Tasks",
                "Search Tasks",
                "Create New Task",
                "Update Task",
                "Delete Task",
                "Bulk Operations",
                "View Statistics"
            ], "Task Management")
            
            choice = self.get_int_input("Enter your choice")
            
            if choice == 0:
                break
            
            elif choice == 1:
                self.view_all_tasks()
            elif choice == 2:
                self.view_by_status()
            elif choice == 3:
                self.view_overdue_tasks()
            elif choice == 4:
                self.search_tasks()
            elif choice == 5:
                self.create_task()
            elif choice == 6:
                self.update_task()
            elif choice == 7:
                self.delete_task()
            elif choice == 8:
                self.bulk_operations()
            elif choice == 9:
                self.print_statistics()
    
    def view_all_tasks(self):
        """View all tasks."""
        self.print_header("All Tasks")
        tasks = self.manager.get_all_tasks()
        self.print_tasks(tasks, show_details=True)
        input("  Press Enter to continue...")
    
    def view_by_status(self):
        """View tasks by status."""
        self.print_header("View by Status")
        print("  1. Pending")
        print("  2. In Progress")
        print("  3. Completed")
        print("  4. Archived")
        
        status_map = {
            1: Task.STATUS_PENDING,
            2: Task.STATUS_IN_PROGRESS,
            3: Task.STATUS_COMPLETED,
            4: Task.STATUS_ARCHIVED
        }
        
        choice = self.get_int_input("Select status")
        status = status_map.get(choice)
        
        if status:
            tasks = self.manager.get_tasks_by_status(status)
            self.print_header(f"Tasks - {status}")
            self.print_tasks(tasks)
            input("  Press Enter to continue...")
    
    def view_overdue_tasks(self):
        """View overdue tasks."""
        self.print_header("Overdue Tasks")
        tasks = self.manager.get_overdue_tasks()
        if tasks:
            self.print_tasks(tasks)
        else:
            print("  No overdue tasks. Great job!")
        input("  Press Enter to continue...")
    
    def search_tasks(self):
        """Search tasks by keyword."""
        self.print_header("Search Tasks")
        keyword = self.get_input("Enter search keyword")
        
        if keyword:
            all_tasks = self.manager.get_all_tasks()
            results = [
                t for t in all_tasks
                if keyword.lower() in t.title.lower() or 
                   keyword.lower() in t.description.lower()
            ]
            self.print_header(f"Search Results for '{keyword}'")
            self.print_tasks(results)
        input("  Press Enter to continue...")
    
    def create_task(self):
        """Create a new task."""
        self.print_header("Create New Task")
        
        title = self.get_input("Title")
        if not title:
            print("  Title is required!")
            input("  Press Enter to continue...")
            return
        
        description = self.get_input("Description (optional)")
        
        print("  Priority: 1-Low, 2-Medium, 3-High, 4-Urgent")
        priority_map = {1: Task.PRIORITY_LOW, 2: Task.PRIORITY_MEDIUM, 
                       3: Task.PRIORITY_HIGH, 4: Task.PRIORITY_URGENT}
        priority_choice = self.get_int_input("Priority", 2)
        priority = priority_map.get(priority_choice, Task.PRIORITY_MEDIUM)
        
        deadline = self.get_input("Deadline (YYYY-MM-DD HH:MM, optional)")
        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d %H:%M")
            except ValueError:
                print("  Invalid date format, deadline will be skipped.")
                deadline = None
        
        # Category selection
        categories = self.manager.get_all_categories()
        if categories:
            self.print_header("Select Category")
            for i, cat in enumerate(categories, 1):
                print(f"  {i}. {cat.name}")
            print("  0. No Category")
            cat_choice = self.get_int_input("Category", 0)
            category_id = categories[cat_choice - 1].id if 1 <= cat_choice <= len(categories) else None
        else:
            category_id = None
        
        # Tag selection
        tags = self.manager.get_all_tags()
        tag_ids = []
        if tags:
            self.print_header("Select Tags (comma-separated numbers, 0 for none)")
            for i, tag in enumerate(tags, 1):
                print(f"  {i}. {tag.name}")
            tag_input = self.get_input("Tags")
            if tag_input:
                try:
                    tag_indices = [int(x.strip()) for x in tag_input.split(",")]
                    tag_ids = [tags[i-1].id for i in tag_indices if 1 <= i <= len(tags)]
                except ValueError:
                    pass
        
        task = self.manager.create_task(title, description, priority, deadline, category_id, tag_ids)
        print(f"\n  Task created successfully! ID: {task.id}")
        input("  Press Enter to continue...")
    
    def update_task(self):
        """Update an existing task."""
        self.print_header("Update Task")
        task_id = self.get_input("Enter Task ID to update")
        
        task = self.manager.get_task_by_id(task_id)
        if not task:
            print("  Task not found!")
            input("  Press Enter to continue...")
            return
        
        self.print_header(f"Updating: {task.title}")
        print(f"  Current: {task.description}")
        print(f"  Current Priority: {task.priority}")
        print(f"  Current Status: {task.status}")
        if task.deadline:
            print(f"  Current Deadline: {task.deadline}")
        
        print("\n  Leave fields blank to keep current value.")
        
        title = self.get_input("New Title")
        description = self.get_input("New Description")
        
        print("  Priority: 1-Low, 2-Medium, 3-High, 4-Urgent (0 to keep)")
        priority_choice = self.get_int_input("New Priority", 0)
        
        print("  Status: 1-Pending, 2-In Progress, 3-Completed, 4-Archived (0 to keep)")
        status_choice = self.get_int_input("New Status", 0)
        
        deadline = self.get_input("New Deadline (YYYY-MM-DD HH:MM)")
        
        if self.manager.update_task(
            task_id,
            title=title if title else None,
            description=description if description else None,
            priority=Task.PRIORITY_LOW if priority_choice == 1 else
                     Task.PRIORITY_MEDIUM if priority_choice == 2 else
                     Task.PRIORITY_HIGH if priority_choice == 3 else
                     Task.PRIORITY_URGENT if priority_choice == 4 else None,
            status=Task.STATUS_PENDING if status_choice == 1 else
                   Task.STATUS_IN_PROGRESS if status_choice == 2 else
                   Task.STATUS_COMPLETED if status_choice == 3 else
                   Task.STATUS_ARCHIVED if status_choice == 4 else None,
            deadline=deadline if deadline else None
        ):
            print("  Task updated successfully!")
        else:
            print("  Failed to update task!")
        
        input("  Press Enter to continue...")
    
    def delete_task(self):
        """Delete a task."""
        self.print_header("Delete Task")
        task_id = self.get_input("Enter Task ID to delete")
        
        if self.manager.delete_task(task_id):
            print("  Task deleted successfully!")
        else:
            print("  Task not found!")
        
        input("  Press Enter to continue...")
    
    def bulk_operations(self):
        """Bulk operations on tasks."""
        while True:
            self.print_header("Bulk Operations")
            print("  1. Mark multiple tasks as completed")
            print("  2. Delete multiple tasks")
            print("  0. Back")
            
            choice = self.get_int_input("Enter your choice")
            
            if choice == 0:
                break
            elif choice in [1, 2]:
                task_ids_input = self.get_input("Enter Task IDs (comma-separated)")
                task_ids = [tid.strip() for tid in task_ids_input.split(",")]
                
                if choice == 1:
                    count = self.manager.bulk_update_status(task_ids, Task.STATUS_COMPLETED)
                    print(f"  {count} task(s) marked as completed.")
                else:
                    count = self.manager.bulk_delete(task_ids)
                    print(f"  {count} task(s) deleted.")
                
                input("  Press Enter to continue...")
    
    def category_menu(self):
        """Category management menu."""
        while True:
            self.print_menu([
                "View Categories",
                "Create Category",
                "Delete Category"
            ], "Category Management")
            
            choice = self.get_int_input("Enter your choice")
            
            if choice == 0:
                break
            
            elif choice == 1:
                self.view_categories()
            elif choice == 2:
                self.create_category()
            elif choice == 3:
                self.delete_category()
    
    def view_categories(self):
        """View all categories."""
        self.print_header("Categories")
        categories = self.manager.get_all_categories()
        
        if not categories:
            print("  No categories found.")
        else:
            for i, cat in enumerate(categories, 1):
                task_count = len(self.manager.get_tasks_by_category(cat.id))
                print(f"  {i}. {cat.name} ({task_count} tasks)")
                if cat.description:
                    print(f"     {cat.description}")
        
        input("  Press Enter to continue...")
    
    def create_category(self):
        """Create a new category."""
        self.print_header("Create Category")
        name = self.get_input("Category name")
        
        if not name:
            print("  Category name is required!")
            input("  Press Enter to continue...")
            return
        
        description = self.get_input("Description (optional)")
        
        category = self.manager.create_category(name, description)
        print(f"  Category '{category.name}' created successfully!")
        input("  Press Enter to continue...")
    
    def delete_category(self):
        """Delete a category."""
        self.print_header("Delete Category")
        categories = self.manager.get_all_categories()
        
        if not categories:
            print("  No categories to delete.")
            input("  Press Enter to continue...")
            return
        
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat.name}")
        
        choice = self.get_int_input("Select category to delete")
        
        if 1 <= choice <= len(categories):
            category = categories[choice - 1]
            if self.manager.delete_category(category.id):
                print(f"  Category '{category.name}' deleted successfully!")
            else:
                print("  Failed to delete category!")
        else:
            print("  Invalid selection!")
        
        input("  Press Enter to continue...")
    
    def tag_menu(self):
        """Tag management menu."""
        while True:
            self.print_menu([
                "View Tags",
                "Create Tag",
                "Delete Tag"
            ], "Tag Management")
            
            choice = self.get_int_input("Enter your choice")
            
            if choice == 0:
                break
            
            elif choice == 1:
                self.view_tags()
            elif choice == 2:
                self.create_tag()
            elif choice == 3:
                self.delete_tag()
    
    def view_tags(self):
        """View all tags."""
        self.print_header("Tags")
        tags = self.manager.get_all_tags()
        
        if not tags:
            print("  No tags found.")
        else:
            for tag in tags:
                print(f"  - {tag.name}")
        
        input("  Press Enter to continue...")
    
    def create_tag(self):
        """Create a new tag."""
        self.print_header("Create Tag")
        name = self.get_input("Tag name")
        
        if not name:
            print("  Tag name is required!")
            input("  Press Enter to continue...")
            return
        
        color = self.get_input("Color (hex, e.g., #3498db)", "#3498db")
        
        tag = self.manager.create_tag(name, color)
        print(f"  Tag '{tag.name}' created successfully!")
        input("  Press Enter to continue...")
    
    def delete_tag(self):
        """Delete a tag."""
        self.print_header("Delete Tag")
        tags = self.manager.get_all_tags()
        
        if not tags:
            print("  No tags to delete.")
            input("  Press Enter to continue...")
            return
        
        for i, tag in enumerate(tags, 1):
            print(f"  {i}. {tag.name}")
        
        choice = self.get_int_input("Select tag to delete")
        
        if 1 <= choice <= len(tags):
            tag = tags[choice - 1]
            if self.manager.delete_tag(tag.id):
                print(f"  Tag '{tag.name}' deleted successfully!")
            else:
                print("  Failed to delete tag!")
        else:
            print("  Invalid selection!")
        
        input("  Press Enter to continue...")
    
    def run(self):
        """Main application loop."""
        self.clear_screen()
        print("\n" + "=" * 50)
        print("  Welcome to Todo List Manager!")
        print("  Your personal task management solution")
        print("=" * 50 + "\n")
        
        # Check if first run
        if not os.path.exists("todos_data.json") or not self.manager.get_all_tasks():
            print("  It looks like you're running this for the first time.")
            create_sample = self.get_input("Create sample data? (y/n)")
            if create_sample.lower() == "y":
                self.create_sample_data()
        
        # Start reminder system
        self.manager.start_reminder_check(300)  # Check every 5 minutes
        
        while True:
            self.print_menu([
                "Task Management",
                "Category Management",
                "Tag Management",
                "View Statistics",
                "Help"
            ], "Main Menu")
            
            choice = self.get_int_input("Enter your choice")
            
            if choice == 0:
                print("\n  Thank you for using Todo List Manager!")
                print("  Goodbye!\n")
                break
            
            elif choice == 1:
                self.task_menu()
            elif choice == 2:
                self.category_menu()
            elif choice == 3:
                self.tag_menu()
            elif choice == 4:
                self.print_statistics()
                input("  Press Enter to continue...")
            elif choice == 5:
                self.show_help()
    
    def show_help(self):
        """Show help information."""
        self.print_header("Help")
        print("""
  Todo List Manager - Quick Guide
  
  Tasks:
    - Create tasks with title, description, priority, and deadline
    - Organize tasks using categories and tags
    - Track progress through status changes: Pending -> In Progress -> Completed
    - Overdue tasks are automatically flagged
  
  Status Icons:
    [ ] Pending
    [~] In Progress
    [X] Completed
    [-] Archived
  
  Priority Levels:
    - Low, Medium, High, Urgent
  
  Tips:
    - Use categories to group related tasks
    - Use tags for flexible cross-category organization
    - Check statistics to see your progress
    - Reminders will notify you of overdue tasks
        """)
        input("  Press Enter to continue...")


# ==================== Entry Point ====================

if __name__ == "__main__":
    app = CLIInterface()
    app.run()