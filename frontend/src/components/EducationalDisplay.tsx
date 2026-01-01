"use client";

import React from 'react';

interface EducationalMessage {
  phase: string;
  title: string;
  content: string;
  whatAIisDoing: string[];
  whyImportant: string;
  learningPoints: string[];
}

interface EducationalDisplayProps {
  currentPhase?: string;
  isVisible: boolean;
  onClose: () => void;
}

const PHASE_EDUCATIONAL_CONTENT: Record<string, EducationalMessage> = {
  specify: {
    phase: "第一阶段：需求分析",
    title: "🎯 需求分析阶段",
    content: "正在分析您的自然语言需求，转换为清晰的技术规格...",
    whatAIisDoing: [
      "理解您的需求意图和核心功能",
      "识别技术约束和边界条件",
      "分析用户场景和使用流程",
      "定义验收标准和成功指标"
    ],
    whyImportant: "需求分析是软件开发的基础。一个清晰的需求分析可以避免开发中的返工和修改，确保功能完整性和一致性，为后续设计阶段提供准确依据。",
    learningPoints: [
      "需求分析是连接用户需求和技术实现的桥梁",
      "好的需求分析应该包含功能、性能、约束三个维度",
      "边界条件的识别可以显著降低开发风险"
    ]
  },
  plan: {
    phase: "第二阶段：技术设计",
    title: "🛠️ 技术设计阶段",
    content: "基于需求分析，正在制定详细的技术实现方案...",
    whatAIisDoing: [
      "选择合适的编程语言和框架",
      "设计系统架构和组件结构",
      "规划开发步骤和里程碑",
      "评估技术风险和依赖关系"
    ],
    whyImportant: "技术设计是将需求转换为可执行方案的关键阶段。一个好的设计可以降低开发复杂度，提高代码质量和可维护性。",
    learningPoints: [
      "技术选型需要考虑成熟度、生态系统、学习成本",
      "良好的架构设计应该遵循SOLID原则和设计模式",
      "模块化设计可以提高代码的可重用性和可测试性",
      "提前考虑扩展性可以降低未来重构成本"
    ]
  },
  implement: {
    phase: "第三阶段：代码实现",
    title: "💻 代码实现阶段",
    content: "正在将设计方案转换为实际可运行的代码...",
    whatAIisDoing: [
      "生成符合规范的源代码文件",
      "实现所有设计的功能和逻辑",
      "添加必要的注释和文档",
      "确保代码语法正确性和可运行性"
    ],
    whyImportant: "代码实现是将设计思想转换为实际产品的最终阶段。高质量的代码实现可以直接交付可运行的软件产品。",
    learningPoints: [
      "代码质量是软件工程的核心竞争力",
      "良好的编码习惯包括命名规范、注释完整、错误处理",
      "单元测试是保证代码质量的重要手段",
      "代码审查可以及早发现潜在问题"
    ]
  }
};

const EducationalDisplay: React.FC<EducationalDisplayProps> = ({
  currentPhase,
  isVisible,
  onClose
}) => {
  if (!isVisible || !currentPhase) return null;

  const educationalContent = PHASE_EDUCATIONAL_CONTENT[currentPhase];

  if (!educationalContent) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-lg">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">{educationalContent.title}</h2>
              <p className="text-blue-100 mt-2">{educationalContent.content}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* What AI is Doing */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              📋 这一阶段AI在做什么：
            </h3>
            <ul className="space-y-2">
              {educationalContent.whatAIisDoing.map((item, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span className="text-gray-700">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Why Important */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              💡 为什么需要这一步：
            </h3>
            <p className="text-gray-700 leading-relaxed bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-400">
              {educationalContent.whyImportant}
            </p>
          </div>

          {/* Learning Points */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              🎓 学习要点：
            </h3>
            <div className="grid gap-3">
              {educationalContent.learningPoints.map((point, index) => (
                <div key={index} className="bg-blue-50 p-3 rounded-lg border-l-4 border-blue-400">
                  <span className="text-blue-800 font-medium">{point}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Progress Indicator */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex justify-between items-center text-sm text-gray-600">
              <span>阶段进度</span>
              <span className="font-medium">
                {educationalContent.phase}
              </span>
            </div>
            <div className="mt-2 bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-500"
                style={{
                  width: currentPhase === 'specify' ? '33%' :
                         currentPhase === 'plan' ? '66%' : '100%'
                }}
              ></div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 rounded-b-lg flex justify-end">
          <button
            onClick={onClose}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
          >
            知道了，继续生成
          </button>
        </div>
      </div>
    </div>
  );
};

export default EducationalDisplay;
