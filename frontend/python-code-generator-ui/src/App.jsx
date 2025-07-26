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
  const [activeTab, setActiveTab] = useState('generator');
  const [projectHistory, setProjectHistory] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectFiles, setProjectFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const [executionResult, setExecutionResult] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionLogs, setExecutionLogs] = useState([]);
  const [runningProjects, setRunningProjects] = useState([]);
  const [showAdvancedLogs, setShowAdvancedLogs] = useState(false);
  const [generationStats, setGenerationStats] = useState(null);

  // File Explorer Component
  const FileExplorer = ({ files, path = '' }) => {
    const toggleFolder = (folderPath) => {
      const newExpanded = new Set(expandedFolders);
      if (newExpanded.has(folderPath)) {
        newExpanded.delete(folderPath);
      } else {
        newExpanded.add(folderPath);
      }
      setExpandedFolders(newExpanded);
    };

    const getFileIcon = (fileName) => {
      if (fileName.endsWith('.py')) return '◉';
      if (fileName.endsWith('.md')) return '◫';
      if (fileName.endsWith('.txt')) return '◪';
      if (fileName.endsWith('.json')) return '◩';
      if (fileName.endsWith('.yml') || fileName.endsWith('.yaml')) return '◨';
      if (fileName.endsWith('.html')) return '◧';
      if (fileName.endsWith('.css')) return '◦';
      if (fileName.endsWith('.js')) return '◎';
      if (fileName.endsWith('.png') || fileName.endsWith('.jpg') || fileName.endsWith('.jpeg')) return '◐';
      return '◯';
    };

    return (
      <div className="space-y-1">
        {Object.entries(files).map(([name, item]) => {
          const currentPath = path ? `${path}/${name}` : name;
          
          if (item.type === 'folder') {
            const isExpanded = expandedFolders.has(currentPath);
            return (
              <div key={currentPath}>
                <div
                  onClick={() => toggleFolder(currentPath)}
                  className="flex items-center space-x-3 p-2 rounded-lg cursor-pointer hover:bg-slate-700/30 transition-colors"
                >
                  <span className="text-slate-400 text-sm w-4 flex justify-center">
                    {isExpanded ? '▼' : '▶'}
                  </span>
                  <span className="text-slate-400 text-sm">▣</span>
                  <span className="text-white text-sm font-medium">{name}</span>
                </div>
                {isExpanded && (
                  <div className="ml-6 border-l border-slate-700 pl-3 mt-1">
                    <FileExplorer files={item.children} path={currentPath} />
                  </div>
                )}
              </div>
            );
          } else {
            return (
              <div
                key={currentPath}
                onClick={() => {
                  setSelectedFile(item);
                  fetchFileContent(selectedProject.id, item.path);
                }}
                className={`flex items-center space-x-3 p-2 rounded-lg cursor-pointer transition-colors ${
                  selectedFile?.path === item.path
                    ? 'bg-slate-700/50 border border-slate-600'
                    : 'hover:bg-slate-700/30'
                }`}
              >
                <span className="text-slate-400 text-sm w-4 flex justify-center">◦</span>
                <span className="text-slate-400 text-sm">{getFileIcon(name)}</span>
                <span className="text-white text-sm font-mono flex-1">{name}</span>
                <span className="text-xs text-slate-500">
                  {Math.round(item.size / 1024 * 10) / 10}KB
                </span>
              </div>
            );
          }
        })}
      </div>
    );
  };

  const fetchProjectHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects/history`);
      setProjectHistory(response.data);
    } catch (error) {
      console.error('Error fetching project history:', error);
      addLog('⚠️ Failed to fetch project history', 'warning');
    }
  };

  const fetchProjectFiles = async (projectId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects/${projectId}/files`);
      
      // Organize files into a tree structure
      const fileTree = {};
      response.data.forEach(file => {
        const pathParts = file.path.split('/').filter(part => part);
        let current = fileTree;
        
        for (let i = 0; i < pathParts.length; i++) {
          const part = pathParts[i];
          if (i === pathParts.length - 1) {
            // This is a file
            current[part] = {
              type: 'file',
              ...file
            };
          } else {
            // This is a folder
            if (!current[part]) {
              current[part] = {
                type: 'folder',
                children: {}
              };
            }
            current = current[part].children;
          }
        }
      });
      
      setProjectFiles(fileTree);
    } catch (error) {
      console.error('Error fetching project files:', error);
      addLog('⚠️ Failed to fetch project files', 'warning');
    }
  };

  const fetchFileContent = async (projectId, filePath) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects/${projectId}/files/${encodeURIComponent(filePath)}`);
      setFileContent(response.data.content);
    } catch (error) {
      console.error('Error fetching file content:', error);
      addLog('⚠️ Failed to fetch file content', 'warning');
    }
  };

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io(API_BASE_URL);
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to server');
      addLog('🔗 Connected to Python Code Generator', 'success');
    });

    newSocket.on('progress_update', (data) => {
      console.log('Progress update:', data);
      addLog(`🔄 ${data.message}`, 'info', data.data);
      
      // Track generation statistics
      if (data.stage === 'planning') {
        setGenerationStats(prev => ({ ...prev, agentCalls: (prev?.agentCalls || 0) + 1 }));
      } else if (data.stage === 'development') {
        setGenerationStats(prev => ({ ...prev, agentCalls: (prev?.agentCalls || 0) + 1 }));
      } else if (data.stage === 'testing') {
        setGenerationStats(prev => ({ ...prev, agentCalls: (prev?.agentCalls || 0) + 1 }));
      }
      
      if (data.data && data.data.filesCreated) {
        setGenerationStats(prev => ({ ...prev, filesCreated: data.data.filesCreated }));
      }
    });

    newSocket.on('project_completed', (data) => {
      console.log('Project completed:', data);
      setIsGenerating(false);
      setCurrentProject(data);
      
      // Calculate duration
      const duration = generationStats?.startTime 
        ? Math.round((Date.now() - generationStats.startTime) / 1000) + 's'
        : 'Unknown';
      setGenerationStats(prev => ({ ...prev, duration }));
      
      addLog('✅ Project generation completed successfully!', 'success');
      fetchProjectHistory(); // Refresh history
    });

    newSocket.on('project_failed', (data) => {
      console.log('Project failed:', data);
      setIsGenerating(false);
      addLog(`❌ Project generation failed: ${data.error}`, 'error');
    });

    newSocket.on('execution_complete', (data) => {
      console.log('Execution completed:', data);
      setIsExecuting(false);
      setExecutionResult(data.result);
      
      // If it's a Streamlit app that auto-opened, show special message
      if (data.result.method === 'streamlit' && data.result.auto_opened) {
        addLog(`🌐 Streamlit app opened in browser automatically!`, 'success');
        addLog(`🔗 App URL: ${data.result.url}`, 'info');
      } else {
        addLog(`🚀 Project execution completed: ${data.result.status}`, 'success');
      }
    });

    newSocket.on('execution_error', (data) => {
      console.log('Execution error:', data);
      setIsExecuting(false);
      setExecutionResult(data.error);
      addLog(`❌ Project execution failed: ${data.error.error}`, 'error');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setIsGenerating(false); // Reset generating state on disconnect
      setIsExecuting(false); // Reset execution state on disconnect
      addLog('🔌 Disconnected from Python Code Generator', 'warning');
    });

    // Load project history on component mount
    fetchProjectHistory();

    return () => {
      newSocket.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const addLog = (message, type = 'info', details = null) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { message, type, timestamp, details, id: Date.now() }]);
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      addLog('⚠️ Please enter a project description', 'warning');
      return;
    }

    setIsGenerating(true);
    setCurrentProject(null);
    setLogs([]); // Clear previous logs
    setGenerationStats({ agentCalls: 0, filesCreated: 0, startTime: Date.now() });
    addLog('🚀 Initializing project generation...', 'info');

    try {
      addLog('📡 Sending request to server...', 'info');
      const response = await axios.post(`${API_BASE_URL}/api/generate`, {
        prompt: prompt.trim()
      });

      if (response.data.project_id) {
        addLog(`🆔 Project created with ID: ${response.data.project_id}`, 'success');
        addLog('👥 Connecting to multi-agent system...', 'info');
        socket.emit('join_project', { project_id: response.data.project_id });
      }
    } catch (error) {
      console.error('Error starting generation:', error);
      setIsGenerating(false);
      addLog(`❌ Failed to start generation: ${error.message}`, 'error');
    }
  };

  // Add cleanup effect for component unmount
  useEffect(() => {
    return () => {
      setIsGenerating(false);
    };
  }, []);

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

  const runProject = async (projectId) => {
    try {
      setIsExecuting(true);
      setExecutionResult(null);
      setExecutionLogs([]);
      addLog('🚀 Starting project execution...', 'info');

      const response = await axios.post(`${API_BASE_URL}/api/projects/${projectId}/run`);
      
      addLog(`🔧 Using execution method: ${response.data.run_method}`, 'info');
      
      if (response.data.run_method === 'streamlit') {
        addLog('🌐 Streamlit app will be available at http://localhost:8501', 'info');
      }
      
    } catch (error) {
      console.error('Error running project:', error);
      setIsExecuting(false);
      addLog(`❌ Failed to run project: ${error.message}`, 'error');
    }
  };

  const stopProject = async (projectId) => {
    try {
      // Immediately update UI state for responsiveness
      addLog('🛑 Stopping project...', 'warning');
      
      // Clear execution states immediately to enable run button
      setIsExecuting(false);
      if (selectedProject?.id === projectId) {
        setExecutionResult(null);
      }
      
      // Refresh running projects immediately to remove from list
      checkRunningProjects();
      
      // Make the API call
      await axios.post(`${API_BASE_URL}/api/projects/${projectId}/stop`);
      addLog('✅ Project execution stopped successfully', 'success');
      
      // Refresh running projects again to ensure clean state
      setTimeout(() => checkRunningProjects(), 500);
      
    } catch (error) {
      console.error('Error stopping project:', error);
      addLog(`❌ Failed to stop project: ${error.message}`, 'error');
    }
  };

  const getExecutionStatus = async (projectId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects/${projectId}/execution`);
      return response.data;
    } catch (error) {
      console.error('Error getting execution status:', error);
      return null;
    }
  };

  const checkRunningProjects = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects/running`);
      setRunningProjects(response.data);
    } catch (error) {
      console.error('Error checking running projects:', error);
    }
  };

  const isProjectRunning = async (projectId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects/${projectId}/is-running`);
      return response.data.running;
    } catch (error) {
      console.error('Error checking project running status:', error);
      return false;
    }
  };

  // Periodically check for running projects
  useEffect(() => {
    const interval = setInterval(checkRunningProjects, 5000); // Check every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-gray-900 to-slate-900">
      {/* Sophisticated Background Pattern */}
      <div 
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23334155' fill-opacity='0.08'%3E%3Cpath d='M50 0L100 50L50 100L0 50Z'/%3E%3C/g%3E%3C/svg%3E")`
        }}
      ></div>
      
      <div className="relative z-10 min-h-screen">
        {/* Professional Header */}
        <header className="bg-black/40 backdrop-blur-2xl border-b border-slate-700/50 shadow-2xl">
          <div className="max-w-7xl mx-auto px-6 py-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="relative">
                  <div className="w-14 h-14 bg-gradient-to-br from-slate-700 via-slate-600 to-slate-500 rounded-lg flex items-center justify-center shadow-xl border border-slate-600/50">
                    <div className="text-white text-xl font-bold font-mono">{'</>'}</div>
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-slate-900 shadow-lg"></div>
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-white tracking-tight">
                    Python Code Generator
                  </h1>
                  <p className="text-slate-400 text-sm font-medium mt-1">
                    Enterprise AI Development Platform
                  </p>
                </div>
              </div>
              
              {/* Professional Navigation */}
              <nav className="flex space-x-2 bg-slate-800/50 rounded-lg p-2 backdrop-blur-sm border border-slate-700/50">
                <button
                  onClick={() => setActiveTab('generator')}
                  className={`px-6 py-3 rounded-md transition-all duration-200 font-semibold text-sm ${
                    activeTab === 'generator'
                      ? 'bg-slate-700 text-white shadow-lg border border-slate-600'
                      : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  Code Generator
                </button>
                <button
                  onClick={() => setActiveTab('run')}
                  className={`px-6 py-3 rounded-md transition-all duration-200 font-semibold text-sm relative ${
                    activeTab === 'run'
                      ? 'bg-slate-700 text-white shadow-lg border border-slate-600'
                      : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  Run & Test
                  {runningProjects.length > 0 && (
                    <span className="absolute -top-1 -right-1 bg-emerald-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
                      {runningProjects.length}
                    </span>
                  )}
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`px-6 py-3 rounded-md transition-all duration-200 font-semibold text-sm ${
                    activeTab === 'history'
                      ? 'bg-slate-700 text-white shadow-lg border border-slate-600'
                      : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  Project Archive
                </button>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-10">
          {activeTab === 'generator' && (
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-10">
              {/* Professional Input Section */}
              <div className="xl:col-span-1">
                <div className="bg-slate-800/30 backdrop-blur-xl rounded-lg border border-slate-700/50 p-8 shadow-2xl">
                  <div className="flex items-center space-x-3 mb-8">
                    <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center border border-slate-600">
                      <div className="w-5 h-5 border-2 border-slate-400 border-t-white rounded-full"></div>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-white">Project Specification</h2>
                      <p className="text-slate-400 text-sm">Define your project requirements</p>
                    </div>
                  </div>
                  
                  <div className="space-y-6">
                    <div className="relative">
                      <label className="block text-sm font-medium text-slate-300 mb-3">
                        Project Description
                      </label>
                      <textarea
                        className="w-full h-48 p-4 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 resize-none focus:outline-none focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 text-sm leading-relaxed"
                        placeholder="Describe your Python project requirements in detail...

Example: Create a web scraping application that extracts product information from e-commerce websites, stores data in PostgreSQL database, and generates analytical reports with data visualization charts."
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        disabled={isGenerating}
                      />
                      <div className="absolute bottom-3 right-3 text-xs text-slate-500 bg-slate-800/80 px-2 py-1 rounded">
                        {prompt.length}/2000
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <button 
                        onClick={handleGenerate}
                        disabled={isGenerating || !prompt.trim()}
                        className="w-full bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-500 text-white py-4 px-6 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl disabled:cursor-not-allowed flex items-center justify-center space-x-3 border border-slate-600 hover:border-slate-500"
                      >
                        {isGenerating ? (
                          <>
                            <div className="w-5 h-5 border-2 border-slate-400 border-t-white rounded-full animate-spin"></div>
                            <span>Generating Project...</span>
                          </>
                        ) : (
                          <>
                            <div className="w-5 h-5 border-2 border-white rounded border-t-transparent"></div>
                            <span>Generate Project</span>
                          </>
                        )}
                      </button>

                      {currentProject?.result?.success && (
                        <button 
                          onClick={handleDownload}
                          className="w-full bg-emerald-700 hover:bg-emerald-600 text-white py-4 px-6 rounded-lg font-semibold transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center space-x-3 border border-emerald-600"
                        >
                          <div className="w-5 h-5">
                            <svg fill="currentColor" viewBox="0 0 24 24">
                              <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                            </svg>
                          </div>
                          <span>Download Project</span>
                        </button>
                      )}
                    </div>

                    {/* Professional Templates */}
                    <div className="border-t border-slate-700 pt-6">
                      <h3 className="text-sm font-semibold text-slate-300 mb-4">Project Templates</h3>
                      <div className="grid grid-cols-1 gap-3">
                        {[
                          "Web API with authentication system",
                          "Data analysis with machine learning", 
                          "Desktop application with GUI",
                          "Automation script with scheduling"
                        ].map((template, idx) => (
                          <button
                            key={idx}
                            onClick={() => setPrompt(template)}
                            className="text-left p-3 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-sm text-slate-300 hover:text-white transition-all duration-200 border border-slate-700 hover:border-slate-600"
                          >
                            {template}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Professional Logs Section */}
              <div className="xl:col-span-2">
                <div className="bg-slate-800/30 backdrop-blur-xl rounded-lg border border-slate-700/50 p-8 h-[700px] flex flex-col shadow-2xl">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center border border-slate-600">
                        <div className="w-5 h-5">
                          <svg fill="currentColor" viewBox="0 0 24 24" className="text-slate-300">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                          </svg>
                        </div>
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-white">Development Console</h2>
                        <p className="text-slate-400 text-sm">Real-time AI agent collaboration</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setShowAdvancedLogs(!showAdvancedLogs)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border ${
                          showAdvancedLogs 
                            ? 'bg-slate-600 text-white border-slate-500' 
                            : 'bg-slate-700/50 text-slate-400 border-slate-600 hover:bg-slate-600 hover:text-white'
                        }`}
                      >
                        Advanced
                      </button>
                      {logs.length > 0 && (
                        <button
                          onClick={() => setLogs([])}
                          className="text-slate-400 hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-700/50 transition-colors border border-slate-600 hover:border-slate-500 text-xs"
                        >
                          Clear
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Generation Statistics */}
                  {(isGenerating || generationStats) && (
                    <div className="mb-6 p-4 bg-slate-900/40 rounded-lg border border-slate-700/50">
                      <h3 className="text-sm font-semibold text-white mb-3">Generation Metrics</h3>
                      <div className="grid grid-cols-3 gap-4 text-xs">
                        <div className="bg-slate-800/50 p-2 rounded">
                          <div className="text-slate-400">Agent Calls</div>
                          <div className="text-white font-mono">{generationStats?.agentCalls || (isGenerating ? '...' : '0')}</div>
                        </div>
                        <div className="bg-slate-800/50 p-2 rounded">
                          <div className="text-slate-400">Files Created</div>
                          <div className="text-white font-mono">{generationStats?.filesCreated || (isGenerating ? '...' : '0')}</div>
                        </div>
                        <div className="bg-slate-800/50 p-2 rounded">
                          <div className="text-slate-400">Duration</div>
                          <div className="text-white font-mono">{generationStats?.duration || (isGenerating ? 'Active' : '0s')}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Execution Results */}
                  {executionResult && (
                    <div className="mb-6 p-4 bg-slate-900/40 rounded-lg border border-slate-700/50">
                      <h3 className="text-sm font-semibold text-white mb-3 flex items-center space-x-2">
                        <span>Execution Result</span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          executionResult.success 
                            ? 'bg-emerald-900/50 text-emerald-300' 
                            : 'bg-red-900/50 text-red-300'
                        }`}>
                          {executionResult.method}
                        </span>
                      </h3>
                      
                      {executionResult.method === 'streamlit' && executionResult.success ? (
                        <div className="bg-emerald-900/20 border border-emerald-700 rounded p-3 text-sm">
                          <div className="text-emerald-300 font-medium mb-2 flex items-center space-x-2">
                            <span>🌐 Streamlit App Running</span>
                            {executionResult.auto_opened && (
                              <span className="text-xs bg-emerald-800/50 px-2 py-1 rounded">Auto-opened</span>
                            )}
                          </div>
                          <div className="text-emerald-100 text-xs mb-3">
                            {executionResult.auto_opened ? 
                              'Application opened automatically in your browser' : 
                              'Access your application at:'
                            }
                          </div>
                          <div className="flex items-center space-x-3 mb-3">
                            <a 
                              href="http://localhost:8501" 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-emerald-300 underline hover:text-emerald-200 font-mono text-xs flex items-center space-x-1"
                            >
                              <span>🔗</span>
                              <span>http://localhost:8501</span>
                              <div className="w-3 h-3">
                                <svg fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z"/>
                                </svg>
                              </div>
                            </a>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => stopProject(selectedProject?.id)}
                              className="px-3 py-1.5 bg-red-700/20 text-red-300 rounded text-xs hover:bg-red-700/30 transition-colors border border-red-700/50 flex items-center space-x-1"
                            >
                              <span>🛑</span>
                              <span>Stop Server</span>
                            </button>
                            <button
                              onClick={() => window.open('http://localhost:8501', '_blank')}
                              className="px-3 py-1.5 bg-blue-700/20 text-blue-300 rounded text-xs hover:bg-blue-700/30 transition-colors border border-blue-700/50 flex items-center space-x-1"
                            >
                              <span>🔗</span>
                              <span>Open in New Tab</span>
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="text-xs">
                          {executionResult.output && (
                            <pre className="bg-black/30 p-3 rounded border text-slate-300 overflow-x-auto whitespace-pre-wrap">
                              {executionResult.output}
                            </pre>
                          )}
                          {executionResult.error && (
                            <div className="mt-2 bg-red-900/20 border border-red-700 rounded p-3 text-red-200">
                              {executionResult.error}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className="flex-1 overflow-y-auto bg-slate-900/40 rounded-lg p-6 border border-slate-700/50 backdrop-blur-sm">
                    {logs.length === 0 ? (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <div className="w-16 h-16 bg-slate-800 rounded-lg flex items-center justify-center mx-auto mb-6 border border-slate-700">
                            <div className="w-8 h-8 border-2 border-slate-600 border-t-slate-400 rounded-full animate-spin"></div>
                          </div>
                          <h3 className="text-lg font-semibold text-white mb-2">Ready for Development</h3>
                          <p className="text-slate-400 text-base mb-4">Enter project specifications to begin AI-powered code generation</p>
                          <div className="text-sm text-slate-500 bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                            Multi-agent system: Planning → Development → Testing → Optimization
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {logs.map((log, index) => (
                          <div 
                            key={log.id} 
                            className={`p-4 rounded-lg border-l-4 transition-all duration-300 ${
                              log.type === 'success' ? 'bg-emerald-900/20 border-emerald-600 text-emerald-100' :
                              log.type === 'warning' ? 'bg-amber-900/20 border-amber-600 text-amber-100' :
                              log.type === 'error' ? 'bg-red-900/20 border-red-600 text-red-100' :
                              'bg-slate-800/30 border-slate-600 text-slate-200'
                            }`}
                            style={{
                              animation: `slideInRight 0.3s ease-out ${index * 0.05}s both`
                            }}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <span className="font-medium text-sm pr-4">{log.message}</span>
                                {showAdvancedLogs && log.details && (
                                  <div className="mt-2 text-xs opacity-80 bg-black/20 rounded p-2">
                                    {typeof log.details === 'string' ? log.details : JSON.stringify(log.details, null, 2)}
                                  </div>
                                )}
                              </div>
                              <span className="text-xs opacity-70 flex-shrink-0 bg-black/20 px-2 py-1 rounded font-mono">
                                {log.timestamp}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Run & Test Tab */}
          {activeTab === 'run' && (
            <div className="space-y-10">
              {/* Running Projects Status */}
              {runningProjects.length > 0 && (
                <div className="bg-emerald-900/20 backdrop-blur-xl rounded-lg border border-emerald-700/50 p-6 shadow-2xl">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
                      <div className="w-4 h-4">
                        <svg fill="currentColor" viewBox="0 0 24 24" className="text-emerald-100">
                          <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M11,16.5L18,9.5L16.59,8.09L11,13.67L7.91,10.59L6.5,12L11,16.5Z"/>
                        </svg>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-emerald-300">Currently Running Projects</h3>
                      <p className="text-emerald-100 text-sm">{runningProjects.length} project{runningProjects.length > 1 ? 's' : ''} active</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {runningProjects.map((project) => (
                      <div key={project.project_id} className="bg-emerald-900/30 border border-emerald-700 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h4 className="text-emerald-200 font-semibold text-sm">Project Running</h4>
                            <p className="text-emerald-300 font-mono text-xs">{project.project_id.substring(0, 8)}...</p>
                          </div>
                          <div className="flex items-center space-x-1">
                            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                            <span className="text-emerald-300 text-xs">Active</span>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => window.open('http://localhost:8501', '_blank')}
                            className="flex-1 px-3 py-2 bg-emerald-700/30 text-emerald-200 rounded text-xs hover:bg-emerald-700/40 transition-colors border border-emerald-600/50 flex items-center justify-center space-x-1"
                          >
                            <span>🔗</span>
                            <span>Open App</span>
                          </button>
                          <button
                            onClick={() => stopProject(project.project_id)}
                            className="px-3 py-2 bg-red-700/20 text-red-300 rounded text-xs hover:bg-red-700/30 transition-colors border border-red-700/50"
                          >
                            🛑 Stop
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="bg-slate-800/30 backdrop-blur-xl rounded-lg border border-slate-700/50 p-8 shadow-2xl">
                <div className="flex items-center space-x-3 mb-8">
                  <div className="w-10 h-10 bg-emerald-700 rounded-lg flex items-center justify-center border border-emerald-600">
                    <div className="w-5 h-5">
                      <svg fill="currentColor" viewBox="0 0 24 24" className="text-emerald-200">
                        <path d="M8 5v14l11-7z"/>
                      </svg>
                    </div>
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">Project Execution Center</h2>
                    <p className="text-slate-400 text-sm">Run and test your generated Python projects</p>
                  </div>
                </div>

                {projectHistory.length === 0 ? (
                  <div className="text-center py-16">
                    <div className="w-20 h-20 bg-slate-800 rounded-lg flex items-center justify-center mx-auto mb-6 border border-slate-700">
                      <div className="w-10 h-10">
                        <svg fill="currentColor" viewBox="0 0 24 24" className="text-slate-400">
                          <path d="M8 5v14l11-7z"/>
                        </svg>
                      </div>
                    </div>
                    <h3 className="text-xl font-semibold text-white mb-3">No Projects Available</h3>
                    <p className="text-slate-400 mb-6">Generate some projects first to test them here</p>
                    <button
                      onClick={() => setActiveTab('generator')}
                      className="bg-slate-700 hover:bg-slate-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors border border-slate-600"
                    >
                      Go to Generator
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {projectHistory.filter(p => p.status === 'completed').map((project, index) => (
                      <div
                        key={project.id}
                        className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:bg-slate-700/50 hover:border-slate-600 transition-all duration-200"
                        style={{
                          animation: `scaleIn 0.3s ease-out ${index * 0.1}s both`
                        }}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <h3 className="text-white font-semibold text-lg truncate pr-2">{project.name}</h3>
                          <span className="text-xs px-2 py-1 rounded font-medium bg-emerald-900/50 text-emerald-300 border border-emerald-700">
                            Ready
                          </span>
                        </div>
                        
                        <p className="text-slate-400 text-sm mb-6 line-clamp-2">{project.description}</p>
                        
                        <div className="space-y-3">
                          <button
                            onClick={() => runProject(project.id)}
                            disabled={isExecuting}
                            className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-emerald-700/20 text-emerald-300 rounded-lg hover:bg-emerald-700/30 transition-colors border border-emerald-700/50 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {isExecuting ? (
                              <>
                                <div className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
                                <span>Running...</span>
                              </>
                            ) : (
                              <>
                                <div className="w-4 h-4">
                                  <svg fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M8 5v14l11-7z"/>
                                  </svg>
                                </div>
                                <span>Run Project</span>
                              </>
                            )}
                          </button>
                          
                          <div className="flex space-x-2">
                            <button
                              onClick={() => {
                                setSelectedProject(project);
                                fetchProjectFiles(project.id);
                                setActiveTab('history');
                              }}
                              className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-slate-700/20 text-slate-300 rounded-lg hover:bg-slate-700/30 transition-colors border border-slate-700/50 text-sm"
                            >
                              <div className="w-3 h-3">
                                <svg fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                                </svg>
                              </div>
                              <span>View Files</span>
                            </button>
                            
                            <button
                              onClick={() => {/* Download functionality */}}
                              className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-slate-700/20 text-slate-300 rounded-lg hover:bg-slate-700/30 transition-colors border border-slate-700/50 text-sm"
                            >
                              <div className="w-3 h-3">
                                <svg fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                                </svg>
                              </div>
                              <span>Download</span>
                            </button>
                          </div>
                        </div>
                        
                        {/* Execution Status */}
                        {executionResult && selectedProject?.id === project.id && (
                          <div className="mt-4 pt-4 border-t border-slate-700">
                            <div className="text-xs text-slate-400 mb-2">Last Execution</div>
                            <div className={`text-sm p-3 rounded-lg border ${
                              executionResult.success
                                ? 'bg-emerald-900/20 border-emerald-700 text-emerald-300'
                                : 'bg-red-900/20 border-red-700 text-red-300'
                            }`}>
                              {executionResult.method === 'streamlit' && executionResult.success ? (
                                <div>
                                  <div className="font-medium mb-1">Streamlit Running</div>
                                  <a href="http://localhost:8501" target="_blank" rel="noopener noreferrer" className="underline text-xs">
                                    http://localhost:8501
                                  </a>
                                </div>
                              ) : executionResult.success ? (
                                <div className="font-medium">Executed Successfully</div>
                              ) : (
                                <div className="font-medium">Execution Failed</div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
              {/* Professional Project List */}
              <div className="lg:col-span-1">
                <div className="bg-slate-800/30 backdrop-blur-xl rounded-lg border border-slate-700/50 p-8 shadow-2xl">
                  <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center border border-slate-600">
                        <div className="w-5 h-5">
                          <svg fill="currentColor" viewBox="0 0 24 24" className="text-slate-300">
                            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                          </svg>
                        </div>
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-white">Project Archive</h2>
                        <p className="text-slate-400 text-sm">{projectHistory.length} total projects</p>
                      </div>
                    </div>
                    <button
                      onClick={fetchProjectHistory}
                      className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-700/50 transition-colors border border-slate-600 hover:border-slate-500"
                      title="Refresh"
                    >
                      <div className="w-5 h-5">
                        <svg fill="currentColor" viewBox="0 0 24 24">
                          <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                        </svg>
                      </div>
                    </button>
                  </div>
                  
                  <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                    {projectHistory.length === 0 ? (
                      <div className="text-center py-12">
                        <div className="w-16 h-16 bg-slate-800 rounded-lg flex items-center justify-center mx-auto mb-4 border border-slate-700">
                          <div className="w-8 h-8">
                            <svg fill="currentColor" viewBox="0 0 24 24" className="text-slate-400">
                              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                            </svg>
                          </div>
                        </div>
                        <h3 className="text-lg font-semibold text-white mb-2">No Projects Available</h3>
                        <p className="text-slate-400">Generated projects will be archived here</p>
                      </div>
                    ) : (
                      projectHistory.map((project, index) => (
                        <div
                          key={project.id}
                          onClick={() => {
                            setSelectedProject(project);
                            fetchProjectFiles(project.id);
                            setSelectedFile(null);
                            setFileContent('');
                            setExpandedFolders(new Set());
                          }}
                          className={`p-5 rounded-lg border cursor-pointer transition-all duration-200 ${
                            selectedProject?.id === project.id
                              ? 'bg-slate-700/50 border-slate-600 shadow-lg'
                              : 'bg-slate-800/50 border-slate-700 hover:bg-slate-700/50 hover:border-slate-600'
                          }`}
                          style={{
                            animation: `slideInLeft 0.2s ease-out ${index * 0.05}s both`
                          }}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <h3 className="text-white font-semibold text-base truncate pr-2">{project.name}</h3>
                            <span className={`text-xs px-2 py-1 rounded font-medium ${
                              project.status === 'completed' 
                                ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700' 
                                : 'bg-red-900/50 text-red-300 border border-red-700'
                            }`}>
                              {project.status}
                            </span>
                          </div>
                          <p className="text-slate-400 text-sm mb-4 line-clamp-2">{project.description}</p>
                          <div className="flex items-center justify-between text-xs mb-3">
                            <div className="flex items-center space-x-4">
                              <span className="text-slate-500 flex items-center space-x-1">
                                <span>◯</span>
                                <span>{project.file_count} files</span>
                              </span>
                            </div>
                            <span className="text-slate-500 font-mono">
                              {project.created_at}
                            </span>
                          </div>
                          
                          {/* Project Actions */}
                          {project.status === 'completed' && (
                            <div className="flex items-center space-x-2 pt-3 border-t border-slate-700">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  runProject(project.id);
                                }}
                                disabled={isExecuting}
                                className="flex items-center space-x-2 px-3 py-1.5 bg-emerald-700/20 text-emerald-300 rounded-md hover:bg-emerald-700/30 transition-colors border border-emerald-700/50 text-xs font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                <div className="w-3 h-3">
                                  <svg fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M8 5v14l11-7z"/>
                                  </svg>
                                </div>
                                <span>Run</span>
                              </button>
                              
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  // Download functionality
                                }}
                                className="flex items-center space-x-2 px-3 py-1.5 bg-slate-700/20 text-slate-300 rounded-md hover:bg-slate-700/30 transition-colors border border-slate-700/50 text-xs font-medium"
                              >
                                <div className="w-3 h-3">
                                  <svg fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
                                  </svg>
                                </div>
                                <span>Download</span>
                              </button>
                              
                              {executionResult && selectedProject?.id === project.id && (
                                <div className="ml-2">
                                  <span className={`text-xs px-2 py-1 rounded font-medium ${
                                    executionResult.success 
                                      ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700'
                                      : 'bg-red-900/50 text-red-300 border border-red-700'
                                  }`}>
                                    {executionResult.method === 'streamlit' && executionResult.success ? 'Running' : 
                                     executionResult.success ? 'Completed' : 'Failed'}
                                  </span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>

              {/* File Explorer & Viewer */}
              <div className="lg:col-span-2">
                {selectedProject ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Professional File Explorer */}
                    <div className="bg-slate-800/30 backdrop-blur-xl rounded-lg border border-slate-700/50 p-8 shadow-2xl">
                      <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center border border-slate-600">
                            <div className="w-5 h-5">
                              <svg fill="currentColor" viewBox="0 0 24 24" className="text-slate-300">
                                <path d="M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z"/>
                              </svg>
                            </div>
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-white">File Structure</h3>
                            <p className="text-slate-400 text-sm">{selectedProject.name}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="max-h-[400px] overflow-y-auto pr-2 bg-slate-900/30 rounded-lg p-4 border border-slate-700/50">
                        <FileExplorer files={projectFiles} />
                      </div>
                    </div>

                    {/* Professional File Viewer */}
                    <div className="bg-slate-800/30 backdrop-blur-xl rounded-lg border border-slate-700/50 p-8 shadow-2xl">
                      <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center border border-slate-600">
                            <div className="w-5 h-5">
                              <svg fill="currentColor" viewBox="0 0 24 24" className="text-slate-300">
                                <path d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"/>
                              </svg>
                            </div>
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-white">
                              {selectedFile ? selectedFile.name : 'Code Viewer'}
                            </h3>
                            {selectedFile && (
                              <p className="text-slate-400 text-sm font-mono">{selectedFile.path}</p>
                            )}
                          </div>
                        </div>
                        {selectedFile && (
                          <span className="text-xs text-slate-400 bg-slate-700/50 px-3 py-1 rounded border border-slate-600">
                            {Math.round(selectedFile.size / 1024 * 10) / 10}KB
                          </span>
                        )}
                      </div>
                      
                      <div className="bg-slate-900/40 rounded-lg p-6 border border-slate-700/50 h-[400px] overflow-auto backdrop-blur-sm">
                        {selectedFile ? (
                          <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap leading-relaxed">
                            {fileContent || (
                              <div className="flex items-center justify-center h-full">
                                <div className="text-center">
                                  <div className="w-8 h-8 border-2 border-slate-600 border-t-slate-400 rounded-full animate-spin mb-4 mx-auto"></div>
                                  <p className="text-slate-400">Loading file content...</p>
                                </div>
                              </div>
                            )}
                          </pre>
                        ) : (
                          <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                              <div className="w-16 h-16 bg-slate-800 rounded-lg flex items-center justify-center mx-auto mb-4 border border-slate-700">
                                <div className="w-8 h-8">
                                  <svg fill="currentColor" viewBox="0 0 24 24" className="text-slate-400">
                                    <path d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"/>
                                  </svg>
                                </div>
                              </div>
                              <h4 className="text-lg font-semibold text-white mb-2">Select File</h4>
                              <p className="text-slate-400">Choose a file from the structure to view its content</p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-slate-800/30 backdrop-blur-xl rounded-lg border border-slate-700/50 p-8 shadow-2xl">
                    <div className="flex items-center justify-center h-[500px]">
                      <div className="text-center">
                        <div className="w-20 h-20 bg-slate-800 rounded-lg flex items-center justify-center mx-auto mb-6 border border-slate-700">
                          <div className="w-10 h-10">
                            <svg fill="currentColor" viewBox="0 0 24 24" className="text-slate-400">
                              <path d="M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z"/>
                            </svg>
                          </div>
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Select Project</h3>
                        <p className="text-slate-400 text-base">Choose a project from the archive to explore its structure and code</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Project Results - Professional Display */}
          {activeTab === 'generator' && currentProject?.result?.success && (
            <div className="mt-10">
              <div className="bg-slate-800/30 backdrop-blur-xl rounded-lg border border-slate-700/50 p-8 shadow-2xl">
                <div className="flex items-center space-x-3 mb-8">
                  <div className="w-10 h-10 bg-emerald-700 rounded-lg flex items-center justify-center border border-emerald-600">
                    <div className="w-5 h-5">
                      <svg fill="currentColor" viewBox="0 0 24 24" className="text-emerald-200">
                        <path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/>
                      </svg>
                    </div>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-emerald-400">Project Generated Successfully</h2>
                    <p className="text-slate-400 text-sm">Code generation completed and ready for download</p>
                  </div>
                </div>
                
                {currentProject.result.project_plan && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                      <div className="text-sm text-slate-400 mb-2">Project Name</div>
                      <div className="text-white font-semibold">{currentProject.result.project_plan.project_name}</div>
                    </div>
                    <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                      <div className="text-sm text-slate-400 mb-2">Files Generated</div>
                      <div className="text-white font-semibold">{currentProject.result.project_plan.files?.length || 0}</div>
                    </div>
                    <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                      <div className="text-sm text-slate-400 mb-2">Runtime Test</div>
                      <div className={`font-semibold ${currentProject.result.runtime_success ? 'text-emerald-400' : 'text-red-400'}`}>
                        {currentProject.result.runtime_success ? 'PASSED' : 'FAILED'}
                      </div>
                    </div>
                    <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                      <div className="text-sm text-slate-400 mb-2">Project ID</div>
                      <div className="text-white font-mono text-sm">{currentProject.project_id?.substring(0, 8)}...</div>
                    </div>
                  </div>
                )}
                
                {currentProject.result.project_plan?.description && (
                  <div className="mt-6 bg-slate-800/50 p-6 rounded-lg border border-slate-700">
                    <div className="text-sm text-slate-400 mb-3 font-semibold">Project Description</div>
                    <div className="text-slate-300 leading-relaxed">{currentProject.result.project_plan.description}</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;

