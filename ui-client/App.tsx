import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
      <AnimatePresence mode="wait">
        {view === 'landing' ? (
          <motion.div
            key="landing"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05, filter: "blur(10px)" }}
            transition={{
              duration: 0.8,
              ease: [0.25, 0.46, 0.45, 0.94],
              exit: { duration: 0.6 }
            }}
            className="absolute inset-0"
          >
            <LandingView onGenerate={handleGenerate} onDebugMode={handleDebugMode} />
          </motion.div>
        ) : (
          <motion.div
            key="workbench"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{
              duration: 0.6,
              ease: [0.25, 0.46, 0.45, 0.94]
            }}
            className="absolute inset-0"
          >
            <WorkbenchView initialPrompt={userPrompt} projectId={projectId} debugMode={debugMode} />
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
};

export default App;