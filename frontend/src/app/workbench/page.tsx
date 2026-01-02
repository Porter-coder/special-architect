'use client'

import { useState, useEffect, Suspense, useCallback } from 'react'
import { useSearchParams } from 'next/navigation'
import FileExplorer from '../../components/FileExplorer'
import WorkbenchScene from '../../components/WorkbenchScene'
import SSEConnector, { SSEEvent, ConnectionStatus } from '../../components/SSEConnector'

function WorkbenchContent() {
  const searchParams = useSearchParams()
  const mode = searchParams.get('mode')
  const projectId = searchParams.get('project_id')

  console.log(`[Workbench] URL params - mode: "${mode}", projectId: "${projectId}"`)

  const [files, setFiles] = useState<any[]>([])
  const [isStreaming, setIsStreaming] = useState(mode === 'streaming')
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'completed' | 'error'>('connecting')

  // Update isStreaming when mode changes
  useEffect(() => {
    const newIsStreaming = mode === 'streaming'
    if (newIsStreaming !== isStreaming) {
      console.log(`[Workbench] isStreaming changed from ${isStreaming} to ${newIsStreaming}`)
      setIsStreaming(newIsStreaming)
    }
  }, [mode, isStreaming])

  console.log(`[Workbench] COMPONENT RENDER - mode: "${mode}", isStreaming: ${isStreaming}, projectId: ${projectId}`)

  // Monitor search params changes
  useEffect(() => {
    console.log(`[Workbench] useEffect - mode: "${mode}", projectId: "${projectId}", isStreaming: ${isStreaming}`)
  }, [mode, projectId, isStreaming])

  // Track re-renders
  useEffect(() => {
    console.log(`[Workbench] WorkbenchContent component mounted/re-rendered`)
  })

  const handleStreamEvent = useCallback((event: SSEEvent) => {
    console.log('Received SSE event:', event)

    switch (event.type) {
      case 'file_created':
        // Add new file to the tree
        setFiles(prev => [...prev, {
          name: event.filename,
          path: event.path,
          type: 'file',
          size: event.size_bytes,
          created: new Date().toISOString()
        }])
        break

      case 'generation_complete':
        setConnectionStatus('completed')
        setIsStreaming(false)
        break

      case 'error':
        setConnectionStatus('error')
        console.error('Generation error:', event.message || event.error)
        break

      case 'phase_start':
      case 'phase_complete':
      case 'chunk':
      case 'thinking':
        // These events can be handled for UI feedback if needed
        console.log(`Phase event: ${event.type}`, event)
        break
    }
  }, [])

  const handleStatusChange = useCallback((status: ConnectionStatus) => {
    // Map ConnectionStatus to WorkbenchScene expected types
    const statusMap: Record<ConnectionStatus, 'connecting' | 'connected' | 'completed' | 'error'> = {
      'disconnected': 'connecting',
      'connecting': 'connecting',
      'connected': 'connected',
      'reconnecting': 'connecting',
      'completed': 'completed',
      'error': 'error'
    };
    setConnectionStatus(statusMap[status] || 'connecting')
  }, [])

  const streamUrl = projectId ? `/api/stream/${projectId}` : ''

  console.log(`[Workbench] isStreaming: ${isStreaming}, projectId: ${projectId}, streamUrl: ${streamUrl}, shouldRenderSSE: ${isStreaming && streamUrl}`)
  console.log(`[Workbench] mode check: mode === 'streaming' is ${mode === 'streaming'}`)

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono">
      {isStreaming && streamUrl && (
        <SSEConnector
          url={streamUrl}
          onEvent={handleStreamEvent}
          onStatusChange={handleStatusChange}
        />
      )}
      {isStreaming && streamUrl && console.log(`[Workbench] SSEConnector should be rendered with url: ${streamUrl}`)}
      {isStreaming && streamUrl && (() => { console.log(`[Workbench] Should render SSEConnector with url: ${streamUrl}`); return null; })()}
      <WorkbenchScene
        files={files}
        isStreaming={isStreaming}
        connectionStatus={connectionStatus}
      />
    </div>
  )
}

export default function WorkbenchPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black text-green-400 font-mono flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-400 mx-auto mb-4"></div>
          <p>Loading workbench...</p>
        </div>
      </div>
    }>
      <WorkbenchContent />
    </Suspense>
  )
}
