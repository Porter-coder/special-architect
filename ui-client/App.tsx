import React, { useState } from 'react';
import LandingView from './components/LandingView';
import WorkbenchView from './components/WorkbenchView';
import { ViewState } from './types';

const App: React.FC = () => {
  const [view, setView] = useState<ViewState>('landing');
  const [userPrompt, setUserPrompt] = useState('');
  const [projectId, setProjectId] = useState<string>('');
  const [debugMode, setDebugMode] = useState<boolean>(false);

  const handleGenerate = async (prompt: string) => {
    console.log('🔥 [DEBUG] Generating architecture for:', prompt);

    // Generate unique project ID
    const newProjectId = crypto.randomUUID();
    setProjectId(newProjectId);
    setUserPrompt(prompt);

    console.log('🔥 [DEBUG] Generated project ID:', newProjectId);

    // Transition to workbench immediately for better UX
    setView('workbench');

    try {
      // Make API call to start generation
      console.log('🔥 [DEBUG] Making API call to /api/generate');
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          projectId: newProjectId,
        }),
      });

      console.log('🔥 [DEBUG] API response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('🔥 [DEBUG] API error:', errorData);
        throw new Error(errorData.error || 'Generation failed');
      }

      const result = await response.json();
      console.log('🔥 [DEBUG] Generation started:', result);

    } catch (error) {
      console.error('🔥 [DEBUG] Failed to start generation:', error);
      // In a real app, you'd want to handle this error state
    }
  };

  const handleDebugMode = (existingProjectId: string) => {
    console.log('🔧🔧🔧🔧🔧 DEBUG MODE ACTIVATED - PROJECT ID:', existingProjectId);
    setDebugMode(true);
    setProjectId(existingProjectId);
    setUserPrompt('Debug Mode - Loading existing project');
    setView('workbench');
    console.log('🔧🔧🔧🔧🔧 DEBUG MODE ACTIVATED - STATE SET, VIEW CHANGED');
  };

  return (
    <main className="antialiased text-zinc-200">
      {view === 'landing' ? (
        <LandingView onGenerate={handleGenerate} onDebugMode={handleDebugMode} />
      ) : (
        <WorkbenchView initialPrompt={userPrompt} projectId={projectId} debugMode={debugMode} />
      )}
    </main>
  );
};

export default App;