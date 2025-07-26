import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [socket, setSocket] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io(API_BASE_URL);
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to server');
      addLog('Connected to Python Code Generator', 'success');
    });

    newSocket.on('progress_update', (data) => {
      console.log('Progress update:', data);
      addLog(data.message, 'info');
    });

    newSocket.on('project_completed', (data) => {
      console.log('Project completed:', data);
      setIsGenerating(false);
      setCurrentProject(data);
      addLog('Project generation completed successfully!', 'success');
    });

    newSocket.on('project_failed', (data) => {
      console.log('Project failed:', data);
      setIsGenerating(false);
      addLog(`Project generation failed: ${data.error}`, 'error');
    });

    return () => {
      newSocket.close();
    };
  }, []);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { message, type, timestamp, id: Date.now() }]);
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      addLog('Please enter a project description', 'warning');
      return;
    }

    setIsGenerating(true);
    setCurrentProject(null);
    addLog('Starting project generation...', 'info');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/generate`, {
        prompt: prompt.trim()
      });

      if (response.data.project_id) {
        addLog(`Project started with ID: ${response.data.project_id}`, 'success');
        socket.emit('join_project', { project_id: response.data.project_id });
      }
    } catch (error) {
      console.error('Error starting generation:', error);
      setIsGenerating(false);
      addLog(`Failed to start generation: ${error.message}`, 'error');
    }
  };

  const handleDownload = async () => {
    if (!currentProject?.project_id) return;

    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/projects/${currentProject.project_id}/download`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `python_project_${currentProject.project_id}.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      addLog('Project downloaded successfully!', 'success');
    } catch (error) {
      console.error('Error downloading project:', error);
      addLog(`Failed to download project: ${error.message}`, 'error');
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-green-400 to-purple-500 bg-clip-text text-transparent">
            Python Code Generator
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Transform your ideas into complete Python projects using AI-powered multi-agent system.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Project Description</h2>
            <textarea
              className="w-full h-32 p-3 bg-gray-700 rounded-lg text-white resize-none"
              placeholder="Example: Create a calculator app with a GUI that can perform basic arithmetic operations..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={isGenerating}
            />
            <div className="mt-4 space-y-2">
              <button 
                onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}
                className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white py-2 px-4 rounded-lg transition-colors"
              >
                {isGenerating ? 'Generating...' : 'Generate Project'}
              </button>

              {currentProject?.result?.success && (
                <button 
                  onClick={handleDownload}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
                >
                  Download Project
                </button>
              )}
            </div>
          </div>

          {/* Logs Section */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Live Logs</h2>
            <div className="h-64 overflow-y-auto bg-gray-900 rounded-lg p-3">
              {logs.length === 0 ? (
                <p className="text-gray-400">No logs yet. Start generating a project to see live updates.</p>
              ) : (
                logs.map((log) => (
                  <div key={log.id} className={`mb-2 p-2 rounded text-sm ${
                    log.type === 'success' ? 'bg-green-900 text-green-200' :
                    log.type === 'warning' ? 'bg-yellow-900 text-yellow-200' :
                    log.type === 'error' ? 'bg-red-900 text-red-200' :
                    'bg-blue-900 text-blue-200'
                  }`}>
                    <div className="flex justify-between">
                      <span>{log.message}</span>
                      <span className="text-xs opacity-70">{log.timestamp}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Project Results */}
        {currentProject?.result?.success && (
          <div className="mt-8 bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-green-400">Project Generated Successfully</h2>
            {currentProject.result.project_plan && (
              <div className="bg-gray-700 p-4 rounded-lg">
                <p><strong>Name:</strong> {currentProject.result.project_plan.project_name}</p>
                <p><strong>Description:</strong> {currentProject.result.project_plan.description}</p>
                <p><strong>Files:</strong> {currentProject.result.project_plan.files?.length || 0}</p>
                <p><strong>Runtime Test:</strong> 
                  <span className={currentProject.result.runtime_success ? 'text-green-400' : 'text-red-400'}>
                    {currentProject.result.runtime_success ? ' Passed' : ' Failed'}
                  </span>
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

