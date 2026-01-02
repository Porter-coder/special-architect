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