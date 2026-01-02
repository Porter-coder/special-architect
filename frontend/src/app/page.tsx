'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const router = useRouter()

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    setIsGenerating(true)

    try {
      // Generate a unique project ID
      const projectId = crypto.randomUUID()

      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          projectId: projectId,
          application_type: 'python'
        })
      })

      if (response.ok) {
        // Redirect to workbench with streaming mode
        router.push(`/workbench?mode=streaming&project_id=${projectId}`)
      } else {
        const error = await response.json()
        alert(`生成失败: ${error.error}`)
      }
    } catch (error) {
      console.error('Generation error:', error)
      alert('生成请求失败，请稍后重试')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono flex items-center justify-center p-8">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 text-green-300">
            🏗️ Architectural Studio
          </h1>
          <p className="text-green-500">
            AI-powered code generation with real-time workbench
          </p>
        </div>

        <div className="bg-gray-900 border border-green-500 rounded-lg p-6">
          <div className="mb-4">
            <label className="block text-green-400 mb-2">
              描述你想要创建的应用：
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="例如：创建一个贪吃蛇游戏..."
              className="w-full h-32 bg-black border border-green-600 rounded p-3 text-green-400 placeholder-green-700 focus:border-green-400 focus:outline-none"
              disabled={isGenerating}
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={!prompt.trim() || isGenerating}
            className="w-full bg-green-600 hover:bg-green-500 disabled:bg-gray-600 text-black font-bold py-3 px-6 rounded transition-colors"
          >
            {isGenerating ? '🔄 生成中...' : '🚀 开始生成'}
          </button>
        </div>

        <div className="mt-8 text-center text-green-600">
          <p>生成过程将实时显示文件创建进度</p>
        </div>
      </div>
    </div>
  )
}
