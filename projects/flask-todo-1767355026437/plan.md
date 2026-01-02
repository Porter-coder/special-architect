# 实现计划

## 用户需求
一个使用Flask的简单TODO应用，要求有Web界面，可以添加、删除、查看任务

## 详细计划
# Flask TODO 应用 - 技术实现方案

## 1. 系统架构

```
Flask TODO 应用架构
├── 应用层 (app.py)
│   ├── 路由控制器
│   ├── 业务逻辑层
│   └── 数据访问层
├── 表现层 (templates/)
│   ├── HTML5模板
│   ├── Bootstrap 5 CSS
│   └── JavaScript交互
└── 数据层
    └── SQLite3数据库
```

## 2. 组件职责

| 组件 | 职责 |
|------|------|
| 路由层 | 处理HTTP请求，分发到业务逻辑 |
| 业务逻辑层 | 数据验证、任务CRUD操作 |
| 数据访问层 | SQLite数据库连接和查询 |
| Web界面 | 响应式UI、用户交互 |

## 3. 数据流

```
用户操作 → HTTP请求 → Flask路由 → 业务逻辑 → 数据库 → 模板渲染 → HTML响应
```

## 4. 集成点

- **前端框架**: Bootstrap 5（CDN加载）
- **数据库**: SQLite3（内置，无需额外安装）
- **依赖**: Flask框架

---

## PHASE 2: 完整实现

### 依赖项

```
flask>=2.3.0
```

### 文件结构

```
flask_todo/
├── app.py
├── templates/
│   └── index.html
└── requirements.txt
```

### 1. requirements.txt

```txt
flask>=2.3.0
```

### 2. app.py

```python
"""
Flask TODO应用 - 完整的任务管理系统
功能：添加、删除、查看、完成任务
作者：AI Architect
"""

import os
import sqlite3
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g

# ===================== 配置 =====================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'todos.db')
app.config['DEBUG'] = os.environ.get('DEBUG', 'True').lower() == 'true'

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===================== 数据库层 =====================
def get_db():
    """获取数据库连接（请求上下文中）"""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')  # 启用外键约束
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """初始化数据库表"""
    try:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
                    status INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    due_date TEXT
                )
            ''')
            db.commit()
            logger.info("数据库初始化完成: %s", app.config['DATABASE'])
            return True
    except sqlite3.Error as e:
        logger.error("数据库初始化失败: %s", e)
        return False

# ===================== 业务逻辑层 =====================
def validate_todo_data(data: dict) -> tuple:
    """
    验证TODO数据
    Returns: (is_valid: bool, error_message: str or None)
    """
    title = data.get('title', '').strip()
    
    # 验证标题
    if not title:
        return False, "任务标题不能为空"
    
    if len(title) > 200:
        return False, "任务标题不能超过200个字符"
    
    # 验证优先级
    priority = data.get('priority', 'medium')
    valid_priorities = ['low', 'medium', 'high']
    if priority not in valid_priorities:
        return False, f"无效的优先级。必须是: {', '.join(valid_priorities)}"
    
    # 验证日期格式
    due_date = data.get('due_date', '').strip()
    if due_date:
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return False, "截止日期格式无效，请使用 YYYY-MM-DD 格式"
    
    return True, None

class TodoService:
    """TODO服务类"""
    
    @staticmethod
    def get_all(sort: str = 'created_desc') -> list:
        """获取所有任务"""
        db = get_db()
        cursor = db.cursor()
        
        # 排序映射
        order_map = {
            'created_asc': 'created_at ASC',
            'created_desc': 'created_at DESC',
            'priority': 'CASE priority WHEN "high" THEN 1 WHEN "medium" THEN 2 WHEN "low" THEN 3 END',
            'due_date': 'COALESCE(due_date, "9999-12-31") ASC',
            'title': 'title COLLATE NOCASE ASC'
        }
        order_sql = order_map.get(sort, 'created_at DESC')
        
        cursor.execute(f'SELECT * FROM todos ORDER BY {order_sql}')
        todos = [dict(row) for row in cursor.fetchall()]
        
        # 格式化日期
        for todo in todos:
            if todo['due_date']:
                try:
                    due = datetime.fromisoformat(todo['due_date'])
                    todo['due_date_formatted'] = due.strftime('%Y年%m月%d日')
                except (ValueError, TypeError):
                    todo['due_date_formatted'] = None
            else:
                todo['due_date_formatted'] = None
            
            # 创建时间格式化
            if todo['created_at']:
                try:
                    created = datetime.fromisoformat(todo['created_at'])
                    todo['created_formatted'] = created.strftime('%Y-%m-%d %H:%M')
                except (ValueError, TypeError):
                    todo['created_formatted'] = todo['created_at']
        
        return todos
    
    @staticmethod
    def get_by_id(todo_id: int) -> dict:
        """根据ID获取任务"""
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def create(data: dict) -> int:
        """创建新任务"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO todos (title, description, priority, due_date)
            VALUES (?, ?, ?, ?)
        ''', (
            data['title'].strip(),
            data.get('description', '').strip() or None,
            data.get('priority', 'medium'),
            data.get('due_date', '').strip() or None
        ))
        db.commit()
        logger.info("创建任务成功: ID=%d", cursor.lastrowid)
        return cursor.lastrowid
    
    @staticmethod
    def update(todo_id: int, data: dict) -> bool:
        """更新任务"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE todos 
            SET title = ?, description = ?, priority = ?, due_date = ?
            WHERE id = ?
        ''', (
            data['title'].strip(),
            data.get('description', '').strip() or None,
            data.get('priority', 'medium'),
            data.get('due_date', '').strip() or None,
            todo_id
        ))
        db.commit()
        
        if cursor.rowcount > 0:
            logger.info("更新任务成功: ID=%d", todo_id)
            return True
        return False
    
    @staticmethod
    def toggle_status(todo_id: int) -> bool:
        """切换任务完成状态"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE todos SET status = NOT status WHERE id = ?
        ''', (todo_id,))
        db.commit()
        
        if cursor.rowcount > 0:
            logger.info("切换任务状态成功: ID=%d", todo_id)
            return True
        return False
    
    @staticmethod
    def delete(todo_id: int) -> bool:
        """删除任务"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        db.commit()

