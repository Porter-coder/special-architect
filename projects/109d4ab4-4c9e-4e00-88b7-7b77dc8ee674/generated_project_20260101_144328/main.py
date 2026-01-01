"""
待办事项列表管理器 (Task Manager)
=================================
一个功能完整的命令行待办事项管理应用.

功能特性:
- 创建、查看、更新和删除任务
- 任务优先级设置(高/中/低)
- 截止日期管理
- 数据自动持久化到JSON文件
- 友好的命令行界面

作者: Python Software Architect
版本: 1.0.0
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import List, Optional

class TaskStatus(Enum):
    """任务状态枚举"""
    TODO = "待办"
    IN_PROGRESS = "进行中"
    COMPLETED = "已完成"

class TaskPriority(Enum):
    """任务优先级枚举"""
    HIGH = 3
    MEDIUM = 2
    LOW = 1

    @classmethod
    def from_string(cls, priority_str: str) -> 'TaskPriority':
        """从字符串解析优先级"""
        priority_map = {
            "高": cls.HIGH,
            "中": cls.MEDIUM,
            "低": cls.LOW,
            "1": cls.LOW,
            "2": cls.MEDIUM,
            "3": cls.HIGH
        }
        return priority_map.get(priority_str, cls.MEDIUM)

class Task:
    """
    任务数据模型类

    Attributes:
        task_id: 唯一任务标识符
        title: 任务标题
        description: 任务描述
        status: 任务状态
        priority: 任务优先级
        created_at: 创建时间
        due_date: 截止日期
    """

    def __init__(
        self,
        task_id: int,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[str] = None
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.status = TaskStatus.TODO
        self.priority = priority
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.due_date = due_date

    def to_dict(self) -> dict:
        """将任务转换为字典格式"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "due_date": self.due_date
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """从字典创建任务实例"""
        task = cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=TaskPriority(data["priority"]),
            due_date=data.get("due_date")
        )
        task.status = TaskStatus(data["status"])
        task.created_at = data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return task

    def __str__(self) -> str:
        """任务字符串表示"""
        status_icon = {"待办": "○", "进行中": "◐", "已完成": "✓"}
        icon = status_icon.get(self.status.value, "○")
        due_info = f" 截止: {self.due_date}" if self.due_date else ""
        return f"{icon} [{self.priority.value}级] {self.title}{due_info}"

class TaskManager:
    """
    任务管理器类

    负责任务的CRUD操作和数据持久化
    """

    DEFAULT_DATA_FILE = "tasks.json"

    def __init__(self, data_file: str = DEFAULT_DATA_FILE):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.load_tasks()

    def load_tasks(self) -> None:
        """从JSON文件加载任务数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
            except (json.JSONDecodeError, IOError):
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self) -> None:
        """保存任务数据到JSON文件"""
        task_data = [task.to_dict() for task in self.tasks]
        with open(self.data_file, 'w', encoding='utf-8') as file:
            json.dump(task_data, file, ensure_ascii=False, indent=2)

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[str] = None
    ) -> Task:
        """创建新任务"""
        if self.tasks:
            new_id = max(task.task_id for task in self.tasks) + 1
        else:
            new_id = 1

        task = Task(
            task_id=new_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        self.tasks.append(task)
        self.save_tasks()
        return task

    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return self.tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        """更新任务状态"""
        task = self.get_task_by_id(task_id)
        if task:
            task.status = status
            self.save_tasks()
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self.save_tasks()
            return True
        return False

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """按状态筛选任务"""
        return [task for task in self.tasks if task.status == status]

class CLIView:
    """
    命令行视图类

    处理用户界面交互
    """

    @staticmethod
    def display_welcome() -> None:
        """显示欢迎信息"""
        print("=" * 50)
        print("      待办事项列表管理器 v1.0")
        print("=" * 50)
        print()

    @staticmethod
    def display_menu() -> None:
        """显示主菜单"""
        print("请选择操作:")
        print("  1. 查看所有任务")
        print("  2. 添加新任务")
        print("  3. 更新任务状态")
        print("  4. 删除任务")
        print("  5. 按状态筛选查看")
        print("  0. 退出程序")
        print()

    @staticmethod
    def get_user_input(prompt: str) -> str:
        """获取用户输入"""
        return input(prompt).strip()

    @staticmethod
    def display_tasks(tasks: List[Task], title: str = "任务列表") -> None:
        """显示任务列表"""
        if not tasks:
            print(f"\n暂无{title}.")
            return

        print(f"\n{'=' * 50}")
        print(f"  {title} (共 {len(tasks)} 个)")
        print("=" * 50)

        for task in tasks:
            status_indicator = {
                TaskStatus.TODO: "[ ]",
                TaskStatus.IN_PROGRESS: "[进行中]",
                TaskStatus.COMPLETED: "[完成]"
            }
            priority_display = {3: "高", 2: "中", 1: "低"}

            print(f"\n  编号: #{task.task_id}")
            print(f"  标题: {task.title}")
            if task.description:
                print(f"  描述: {task.description}")
            print(f"  状态: {status_indicator[task.status]} {task.status.value}")
            print(f"  优先级: {priority_display[task.priority.value]}")
            if task.due_date:
                print(f"  截止日期: {task.due_date}")
            print(f"  创建时间: {task.created_at}")
            print("-" * 50)

    @staticmethod
    def display_message(message: str, is_error: bool = False) -> None:
        """显示消息"""
        if is_error:
            print(f"错误: {message}")
        else:
            print(message)

    @staticmethod
    def display_goodbye() -> None:
        """显示退出信息"""
        print("\n感谢使用待办事项列表管理器,再见！")

class Application:
    """
    应用程序主控制器类

    协调任务管理器和视图之间的交互
    """

    def __init__(self):
        self.task_manager = TaskManager()
        self.view = CLIView()
        self.running = True

    def run(self) -> None:
        """运行应用程序主循环"""
        self.view.display_welcome()

        while self.running:
            self.view.display_menu()
            choice = self.view.get_user_input("请输入选项编号: ")
            print()

            if choice == "1":
                self.handle_view_all_tasks()
            elif choice == "2":
                self.handle_add_task()
            elif choice == "3":
                self.handle_update_status()
            elif choice == "4":
                self.handle_delete_task()
            elif choice == "5":
                self.handle_filter_by_status()
            elif choice == "0":
                self.running = False
            else:
                self.view.display_message("无效选项,请重新输入.", is_error=True)

            if self.running:
                print()
                input("按回车键继续...")
                print()

        self.view.display_goodbye()

    def handle_view_all_tasks(self) -> None:
        """处理查看所有任务"""
        tasks = self.task_manager.get_all_tasks()
        self.view.display_tasks(tasks, "所有任务")

    def handle_add_task(self) -> None:
        """处理添加新任务"""
        title = self.view.get_user_input("请输入任务标题: ")
        if not title:
            self.view.display_message("任务标题不能为空.", is_error=True)
            return

        description = self.view.get_user_input("请输入任务描述 (可选): ")

        print("请选择优先级: 1-低 2-中 3-高")
        priority_input = self.view.get_user_input("请输入优先级编号: ")
        priority = TaskPriority.from_string(priority_input)

        due_date = self.view.get_user_input("请输入截止日期 (如: 2024-12-31,可选): ")
        if not due_date:
            due_date = None

        task = self.task_manager.create_task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        self.view.display_message(f"任务创建成功！编号: #{task.task_id}")

    def handle_update_status(self) -> None:
        """处理更新任务状态"""
        task_id_str = self.view.get_user_input("请输入要更新的任务编号: ")
        try:
            task_id = int(task_id_str)
        except ValueError:
            self.view.display_message("无效的任务编号.", is_error=True)
            return

        task = self.task_manager.get_task_by_id(task_id)
        if not task:
            self.view.display_message(f"未找到编号为 #{task_id} 的任务.", is_error=True)
            return

        print(f"当前状态: {task.status.value}")
        print("请选择新状态: 1-待办 2-进行中 3-已完成")
        status_choice = self.view.get_user_input("请输入状态编号: ")

        status_map = {"1": TaskStatus.TODO, "2": TaskStatus.IN_PROGRESS, "3": TaskStatus.COMPLETED}
        new_status = status_map.get(status_choice)

        if new_status:
            self.task_manager.update_task_status(task_id, new_status)
            self.view.display_message(f"任务 #{task_id} 状态已更新为: {new_status.value}")
        else:
            self.view.display_message("无效的状态选择.", is_error=True)

    def handle_delete_task(self) -> None:
        """处理删除任务"""
        task_id_str = self.view.get_user_input("请输入要删除的任务编号: ")
        try:
            task_id = int(task_id_str)
        except ValueError:
            self.view.display_message("无效的任务编号.", is_error=True)
            return

        confirm = self.view.get_user_input(f"确定要删除任务 #{task_id} 吗? (y/n): ")
        if confirm.lower() == "y":
            if self.task_manager.delete_task(task_id):
                self.view.display_message(f"任务 #{task_id} 已删除.")
            else:
                self.view.display_message(f"未找到编号为 #{task_id} 的任务.", is_error=True)
        else:
            self.view.display_message("已取消删除.")

    def handle_filter_by_status(self) -> None:
        """处理按状态筛选查看"""
        print("请选择筛选状态: 1-待办 2-进行中 3-已完成")
        status_choice = self.view.get_user_input("请输入状态编号: ")

        status_map = {"1": TaskStatus.TODO, "2": TaskStatus.IN_PROGRESS, "3": TaskStatus.COMPLETED}
        status = status_map.get(status_choice)

        if status:
            tasks = self.task_manager.get_tasks_by_status(status)
            self.view.display_tasks(tasks, f"{status.value}的任务")
        else:
            self.view.display_message("无效的状态选择.", is_error=True)

if __name__ == "__main__":
    # 创建并运行应用程序
    app = Application()
    app.run()