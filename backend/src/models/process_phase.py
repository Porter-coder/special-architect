"""
Process Phase Model

Tracks the three-phase progress of the software engineering process.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class PhaseName(str, Enum):
    """Development phase enumeration."""
    SPECIFY = "specify"
    PLAN = "plan"
    IMPLEMENT = "implement"


class ProcessPhase(BaseModel):
    """
    Tracks the three-phase progress of the software engineering process.

    Fields:
    - phase_id (UUID): Unique identifier for phase record
    - request_id (UUID): Reference to parent request
    - phase_name (PhaseName): Current development phase
    - educational_message (str): Chinese message explaining current phase
    - timestamp (datetime): When this phase was entered
    - thinking_trace (str, optional): AI thinking content for current phase
    """

    phase_id: UUID = Field(default_factory=uuid4, description="Unique identifier for phase record")
    request_id: UUID = Field(..., description="Reference to parent request")
    phase_name: PhaseName = Field(..., description="Current development phase")
    educational_message: str = Field(..., description="Chinese message explaining current phase")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this phase was entered")
    thinking_trace: Optional[str] = Field(None, description="AI thinking content for current phase")

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    @validator('educational_message')
    def validate_educational_message(cls, v):
        """Validate educational message is in Chinese and not empty."""
        if not v or not v.strip():
            raise ValueError('教育性消息不能为空')
        # Basic check for Chinese characters (contains CJK unicode range)
        if not any('\u4e00' <= char <= '\u9fff' for char in v):
            raise ValueError('教育性消息必须包含中文字符')
        return v.strip()

    @validator('phase_name')
    def validate_phase_name(cls, v):
        """Validate phase name is one of the allowed phases."""
        if v not in [PhaseName.SPECIFY, PhaseName.PLAN, PhaseName.IMPLEMENT]:
            raise ValueError(f'无效的阶段名称: {v}')
        return v

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'ProcessPhase':
        """Create instance from dictionary (for JSON deserialization)."""
        # Handle UUID string conversion
        for field in ['phase_id', 'request_id']:
            if field in data and isinstance(data[field], str):
                data[field] = UUID(data[field])

        # Handle datetime string conversion
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

        return cls(**data)


# Phase progression utilities
PHASE_ORDER = [PhaseName.SPECIFY, PhaseName.PLAN, PhaseName.IMPLEMENT]

PHASE_MESSAGES = {
    PhaseName.SPECIFY: """
🎯 第一阶段：需求分析 (Specify Phase)

正在分析您的自然语言需求，转换为清晰的技术规格...

📋 这一阶段AI在做什么：
• 理解您的需求意图和核心功能
• 识别技术约束和边界条件
• 分析用户场景和使用流程
• 定义验收标准和成功指标

💡 为什么需要这一步：
需求分析是软件开发的基础。一个清晰的需求分析可以：
- 避免开发中的返工和修改
- 确保功能完整性和一致性
- 为后续设计阶段提供准确依据
- 帮助评估项目复杂度和工作量

🎓 学习要点：
• 需求分析是连接用户需求和技术实现的桥梁
• 好的需求分析应该包含功能、性能、约束三个维度
• 边界条件的识别可以显著降低开发风险
    """.strip(),
    PhaseName.PLAN: """
🛠️ 第二阶段：技术设计 (Plan Phase)

基于需求分析，正在制定详细的技术实现方案...

📋 这一阶段AI在做什么：
• 选择合适的编程语言和框架
• 设计系统架构和组件结构
• 规划开发步骤和里程碑
• 评估技术风险和依赖关系

💡 为什么需要这一步：
技术设计是将需求转换为可执行方案的关键阶段。一个好的设计可以：
- 降低开发复杂度，提高代码质量
- 优化性能和可维护性
- 提前识别技术风险和难点
- 为团队协作提供清晰指导

🎓 学习要点：
• 技术选型需要考虑成熟度、生态系统、学习成本
• 良好的架构设计应该遵循SOLID原则和设计模式
• 模块化设计可以提高代码的可重用性和可测试性
• 提前考虑扩展性可以降低未来重构成本
    """.strip(),
    PhaseName.IMPLEMENT: """
💻 第三阶段：代码实现 (Implement Phase)

正在将设计方案转换为实际可运行的代码...

📋 这一阶段AI在做什么：
• 生成符合规范的源代码文件
• 实现所有设计的功能和逻辑
• 添加必要的注释和文档
• 确保代码语法正确性和可运行性

💡 为什么需要这一步：
代码实现是将设计思想转换为实际产品的最终阶段。高质量的代码实现可以：
- 直接交付可运行的软件产品
- 为后续维护和扩展奠定基础
- 通过实际运行验证设计正确性
- 提供可复用的代码组件

🎓 学习要点：
• 代码质量是软件工程的核心竞争力
• 良好的编码习惯包括命名规范、注释完整、错误处理
• 单元测试是保证代码质量的重要手段
• 代码审查可以及早发现潜在问题
    """.strip()
}


def get_phase_message(phase: PhaseName) -> str:
    """Get the default educational message for a phase."""
    return PHASE_MESSAGES.get(phase, "正在处理中...")


def is_valid_phase_transition(from_phase: Optional[PhaseName], to_phase: PhaseName) -> bool:
    """
    Check if a phase transition is valid.

    Args:
        from_phase: Previous phase (None for initial phase)
        to_phase: Target phase

    Returns:
        True if transition is valid, False otherwise
    """
    if from_phase is None:
        return to_phase == PhaseName.SPECIFY

    from_index = PHASE_ORDER.index(from_phase)
    to_index = PHASE_ORDER.index(to_phase)

    # Can only move forward in phase order
    return to_index > from_index
