# 需求规格说明

## 用户需求
一个使用Flask的简单TODO应用，要求有Web界面，可以添加、删除、查看任务

## 技术规格
# PHASE 1: 需求分析

## 技术规范文档：Flask TODO 应用

### 1. 核心功能与特性

**基本功能：**
- 查看所有待办任务
- 添加新任务（包含标题、描述、优先级、截止日期）
- 删除任务
- 标记任务为已完成
- 持久化数据存储（SQLite数据库）

**扩展功能：**
- 任务分类/标签
- 搜索功能
- 响应式Web界面
- 实时更新（可选AJAX）

### 2. 技术要求与约束

**技术栈：**
- Python 3.8+
- Flask 2.3+
- SQLite3（内置）
- HTML/CSS/JavaScript（前端）
- Bootstrap 5（UI框架）

**约束条件：**
- 单文件或简洁的多文件结构
- 无需外部数据库服务器
- 支持跨平台运行
- 最小依赖原则

### 3. 数据结构设计

```python
# 任务模型
{
    "id": Integer,           # 主键
    "title": String(200),    # 任务标题（必填）
    "description": Text,     # 任务描述（可选）
    "priority": String(20),  # 优先级：low/medium/high
    "status": Boolean,       # 完成状态
    "created_at": DateTime,  # 创建时间
    "due_date": DateTime     # 截止日期（可选）
}
```

### 4. 用户界面设计

**Web界面结构：**
- 顶部导航栏：应用标题
- 任务表单区域：添加新任务
- 任务列表区域：展示所有任务
- 任务卡片：显示单个任务详情
- 操作按钮：编辑、删除、完成

**交互模式：**
- 表单提交：添加任务
- 按钮点击：删除/完成操作
- 确认对话框：删除操作

### 5. 错误处理与边界情况

| 场景 | 处理方式 |
|------|----------|
| 空任务标题 | 返回错误提示，表单高亮 |
| 无效日期格式 | 使用默认日期，显示警告 |
| 删除不存在任务 | 忽略操作，记录日志 |
| 数据库错误 | 回滚事务，显示友好错误页 |
| 并发访问 | Flask默认处理 |

### 6. 性能考虑

- SQLite适合小规模应用（<10000任务）
- 每次请求独立数据库连接
- 使用索引优化查询
- 模板缓存启用

---

现在我将开始实现完整的应用程序。

## PHASE 2: 系统设计与实现

我将创建一个完整的Flask TODO应用，包含以下文件：

1. `app.py` - 主应用文件
2. `templates/index.html` - 前端界面
3. `requirements.txt` - 依赖列表
4. `schema.sql` - 数据库初始化脚本

让我开始编写代码：
</think>

## 技术规范文档

### 1. 核心功能与特性

| 功能 | 描述 |
|------|------|
| 查看任务 | 以卡片形式展示所有任务，显示状态图标 |
| 添加任务 | 表单输入：标题、描述、优先级、截止日期 |
| 删除任务 | 一键删除，带确认对话框 |
| 完成任务 | 切换任务完成状态 |
| 数据持久化 | SQLite数据库存储 |

### 2. 技术要求与约束

- **后端**: Flask 2.3+, Python 3.8+
- **数据库**: SQLite3（内置）
- **前端**: Bootstrap 5 + 自定义CSS
- **部署**: 单机运行，开发环境
- **依赖**: 最简化外部依赖

### 3. 数据结构

```python
# Todo模型
- id: Integer (主键)
- title: String (必填, 200字符)
- description: Text (可选)
- priority: String (low/medium/high, 默认medium)
- status: Boolean (默认False未完成)
- created_at: DateTime (自动生成)
- due_date: DateTime (可选)
```

### 4. 用户界面

- 响应式Web界面（Bootstrap 5）
- 任务卡片布局
- 模态框添加任务
- 颜色编码优先级

### 5. 错误处理

- 空标题验证
- 日期格式验证
- 数据库事务回滚
- 友好错误提示

### 6. 性能

- SQLite适合小规模数据
- 连接按需创建和关闭
- 简单索引优化

---

## PHASE 2: 系统实现

以下是完整的可执行代码：

```python
"""
Flask TODO应用
功能：完整的TODO任务管理系统
作者：AI Architect
"""

import os
import sqlite3
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g

# ===================== 配置 =====================
app = Flask(__name__)
app.secret_key = os.urandom(24)  # 会话密钥
app.config['DATABASE'] = 'todos.db'
app.config['DEBUG'] = True

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== 数据库层 =====================
def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """初始化数据库表"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                status INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                due_date TEXT
            )
        ''')
        db.commit()
        logger.info("数据库初始化完成")

# ===================== 业务逻辑层 =====================
def validate_todo_data(data: dict) -> tuple:
    """
    验证TODO数据
    返回: (is_valid, error_message)
    """
    title = data.get('title', '').strip()
    
    if not title:
        return False, "任务标题不能为空"
    
    if len(title) > 200:
        return False, "任务标题不能超过200个字符"
    
    priority = data.get('priority', 'medium')
    valid_priorities = ['low', 'medium', 'high']
    if priority not in valid_priorities:
        return False, f"优先级必须是: {', '.join(valid_priorities)}"
    
    # 验证日期格式
    due_date = data.get('due_date', '').strip()
    if due_date:
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return False, "截止日期格式无效，请使用YYYY-MM-DD格式"
    
    return True, None

# ===================== 路由层 =====================
@app.route('/')
def index():
    """主页 - 显示所有任务"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # 获取排序参数
        sort = request.args.get('sort', 'created_desc')
        
        # 构建排序SQL
        order_map = {
            'created_asc': 'created_at ASC',
            'created_desc': 'created_at DESC',
            'priority': 'CASE priority WHEN "high" THEN 1 WHEN "medium" THEN 2 WHEN "low" THEN 3 END',
            'due_date': 'due_date IS NULL, due_date ASC'
        }
        order_sql = order_map.get(sort, 'created_at DESC')
        
        cursor.execute(f'SELECT * FROM todos ORDER BY {order_sql}')
        todos = [dict(row) for row in cursor.fetchall()]
        
        # 格式化日期
        for todo in todos:
            if todo['due_date']:
                try:
                    due = datetime.fromisoformat(todo['due_date'])
                    todo['due_date'] = due.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    todo['due_date'] = None
        
        return render_template('index.html', todos=todos, sort=sort)
    
    except sqlite3.Error as e:
        logger.error(f"数据库错误: {e}")
        flash("加载任务失败，请重试", "danger")
        return render_template('index.html', todos=[])

@app.route('/add', methods=['POST'])
def add_todo():
    """添加新任务"""
    data = {
        'title': request.form.get('title', ''),
        'description': request.form.get('description', ''),
        'priority': request.form.get('priority', 'medium'),
        'due_date': request.form.get('due_date', '')
    }
    
   
