"use client";

import React from 'react';

interface PhaseInfo {
  id: string;
  name: string;
  chineseName: string;
  description: string;
  icon: string;
  status: 'pending' | 'active' | 'completed' | 'error';
  duration?: number; // in seconds
  contentLength?: number; // characters generated
}

interface PhaseProgressProps {
  phases: PhaseInfo[];
  currentPhase?: string;
  showDetails?: boolean;
}

const PHASE_CONFIG: Record<string, Omit<PhaseInfo, 'status' | 'duration' | 'contentLength'>> = {
  specify: {
    id: 'specify',
    name: 'Specify',
    chineseName: '需求分析',
    description: '分析需求，定义边界',
    icon: '🎯'
  },
  plan: {
    id: 'plan',
    name: 'Plan',
    chineseName: '技术设计',
    description: '制定技术方案',
    icon: '🛠️'
  },
  implement: {
    id: 'implement',
    name: 'Implement',
    chineseName: '代码实现',
    description: '生成可运行代码',
    icon: '💻'
  }
};

const PhaseProgress: React.FC<PhaseProgressProps> = ({
  phases = [],
  currentPhase,
  showDetails = true
}) => {
  // Convert phases array to phase objects if needed
  const phaseObjects = phases.length > 0 ? phases : Object.keys(PHASE_CONFIG).map(phaseId => ({
    ...PHASE_CONFIG[phaseId],
    status: currentPhase === phaseId ? 'active' :
            phases.find(p => p.id === phaseId)?.status || 'pending'
  }));

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500 border-green-500';
      case 'active':
        return 'bg-blue-500 border-blue-500 animate-pulse';
      case 'error':
        return 'bg-red-500 border-red-500';
      default:
        return 'bg-gray-300 border-gray-300';
    }
  };

  const getStatusTextColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-700';
      case 'active':
        return 'text-blue-700';
      case 'error':
        return 'text-red-700';
      default:
        return 'text-gray-500';
    }
  };

  const getConnectorColor = (fromStatus: string, toStatus: string) => {
    if (fromStatus === 'completed' && (toStatus === 'active' || toStatus === 'completed')) {
      return 'bg-green-500';
    }
    return 'bg-gray-300';
  };

  return (
    <div className="w-full">
      {/* Desktop/Tablet View */}
      <div className="hidden md:block">
        <div className="flex items-center justify-between">
          {phaseObjects.map((phase, index) => (
            <React.Fragment key={phase.id}>
              {/* Phase Node */}
              <div className="flex flex-col items-center">
                <div className={`w-16 h-16 rounded-full border-4 flex items-center justify-center text-2xl mb-3 transition-all duration-300 ${
                  getStatusColor(phase.status)
                }`}>
                  <span className="text-white">{phase.icon}</span>
                </div>

                <div className="text-center">
                  <h3 className={`font-semibold text-sm ${getStatusTextColor(phase.status)}`}>
                    {phase.chineseName}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1 max-w-20">
                    {phase.description}
                  </p>

                  {showDetails && phase.duration && (
                    <p className="text-xs text-gray-400 mt-1">
                      {phase.duration}s
                    </p>
                  )}

                  {showDetails && phase.contentLength && (
                    <p className="text-xs text-gray-400">
                      {phase.contentLength} 字符
                    </p>
                  )}
                </div>
              </div>

              {/* Connector Line */}
              {index < phaseObjects.length - 1 && (
                <div className="flex-1 h-1 mx-4 relative">
                  <div className={`h-full rounded transition-all duration-300 ${
                    getConnectorColor(phase.status, phaseObjects[index + 1].status)
                  }`}></div>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Mobile View */}
      <div className="md:hidden">
        <div className="space-y-4">
          {phaseObjects.map((phase, index) => (
            <div key={phase.id} className="flex items-center space-x-4">
              {/* Phase Indicator */}
              <div className={`w-12 h-12 rounded-full border-3 flex items-center justify-center text-xl flex-shrink-0 ${
                getStatusColor(phase.status)
              }`}>
                <span className="text-white">{phase.icon}</span>
              </div>

              {/* Phase Info */}
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <h3 className={`font-semibold ${getStatusTextColor(phase.status)}`}>
                    {phase.chineseName}
                  </h3>
                  {phase.duration && (
                    <span className="text-xs text-gray-400">
                      {phase.duration}s
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {phase.description}
                </p>
                {phase.contentLength && (
                  <p className="text-xs text-gray-400 mt-1">
                    {phase.contentLength} 字符
                  </p>
                )}
              </div>

              {/* Status Badge */}
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                phase.status === 'completed' ? 'bg-green-100 text-green-800' :
                phase.status === 'active' ? 'bg-blue-100 text-blue-800' :
                phase.status === 'error' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-600'
              }`}>
                {phase.status === 'completed' ? '✓ 完成' :
                 phase.status === 'active' ? '进行中' :
                 phase.status === 'error' ? '错误' : '等待中'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Overall Progress Bar */}
      {showDetails && (
        <div className="mt-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>整体进度</span>
            <span>
              {phaseObjects.filter(p => p.status === 'completed').length} / {phaseObjects.length} 阶段完成
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-500"
              style={{
                width: `${(phaseObjects.filter(p => p.status === 'completed').length / phaseObjects.length) * 100}%`
              }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PhaseProgress;
