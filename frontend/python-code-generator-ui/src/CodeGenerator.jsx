import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { io } from 'socket.io-client';
import axios from 'axios';
import config from './config';
import './App.css';

const API_BASE_URL = config.API_BASE_URL;

function CodeGenerator() {
  const navigate = useNavigate();
  const [socket, setSocket] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('generator');
  const [projectHistory, setProjectHistory] = useState([]);
  const [mode, setMode] = useState('simple'); // 'simple' or 'multi_agent'
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
  const [isConnected, setIsConnected] = useState(false);

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
      <div className="space-y-1 file-explorer-bw">
        {Object.entries(files).map(([name, item]) => {
          const currentPath = path ? `${path}/${name}` : name;
          
          if (item.type === 'folder') {
            const isExpanded = expandedFolders.has(currentPath);
            return (
              <div key={currentPath}>
                <div
                  onClick={() => toggleFolder(currentPath)}
                  className="flex items-center space-x-3 p-2 rounded-lg cursor-pointer hover:bg-white/20 transition-bw file-item-bw"
                >
                  <span className="text-bw-secondary text-sm w-4 flex justify-center">
                    {isExpanded ? '▼' : '▶'}
                  </span>
                  <span className="text-bw-accent text-sm">📁</span>
                  <span className="folder-name-bw flex-1">{name}</span>
                </div>
                {isExpanded && (
                  <div className="ml-6 border-l border-white/20 pl-3 mt-1">
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
                className={`flex items-center space-x-3 p-2 rounded-lg cursor-pointer transition-bw file-item-bw ${
                  selectedFile?.path === item.path
                    ? 'selected bg-white/20 border border-white/30 shadow-bw'
                    : 'hover:bg-white/15'
                }`}
              >
                <span className="text-bw-secondary text-sm w-4 flex justify-center">◦</span>
                <span className="text-bw-accent text-sm">{getFileIcon(name)}</span>
                <span className="file-name-bw flex-1">{name}</span>
                <span className="file-size-bw">
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
      setIsConnected(true);
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

    // Advanced pipeline structured logs
    newSocket.on('agent_log', (log) => {
      console.log('Agent log:', log);
      // Append structured advanced logs separately with agent-specific formatting
      const agentIcon = {
        'System': '⚙️',
        'Planner': '🎯',
        'Research': '🔍',
        'Data Engineer': '📊',
        'ML Engineer': '🤖',
        'Reviewer': '🔍',
        'Documentation': '📚'
      }[log.agent] || '🔧';
      
      addLog(`${agentIcon} [${log.agent}] ${log.message}`, log.type || 'info', log);
      setShowAdvancedLogs(true);
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
      setIsConnected(false);
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
    // Generate a more unique ID using timestamp + random number
    const uniqueId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setLogs(prev => [...prev, { message, type, timestamp, details, id: uniqueId }]);
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
        prompt: prompt.trim(),
        mode: mode
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
      } else if (response.data.run_method === 'web') {
        addLog('🌍 Web application will be available at http://localhost:8080', 'info');
        addLog('🖥️ Full-stack web application with Flask backend and HTML/CSS/JS frontend', 'info');
      } else {
        addLog('🐍 Running Python script...', 'info');
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
    <div className="generator-bw min-h-screen relative overflow-hidden">
      {/* Black & White Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-10 left-10 w-72 h-72 bg-gradient-to-r from-black to-gray-800 rounded-full mix-blend-multiply filter blur-xl opacity-5 animate-pulse"></div>
        <div className="absolute top-20 right-20 w-96 h-96 bg-gradient-to-r from-gray-900 to-black rounded-full mix-blend-multiply filter blur-xl opacity-5 animate-pulse animation-delay-2000"></div>
        <div className="absolute bottom-20 left-20 w-80 h-80 bg-gradient-to-r from-gray-700 to-black rounded-full mix-blend-multiply filter blur-xl opacity-5 animate-pulse animation-delay-4000"></div>
      </div>
      
      {/* Black & White Geometric Pattern */}
      <div 
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}
      ></div>
      
      <div className="relative z-10 min-h-screen">
        {/* Black & White Header */}
        <header className="glass-bw-strong border-b border-white/20 shadow-bw-lg">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {/* Back Button */}
                <button
                  onClick={() => navigate('/')}
                  className="btn-bw-secondary px-4 py-2 rounded-xl text-sm font-semibold flex items-center space-x-2 shadow-bw hover:shadow-bw-lg transition-bw"
                >
                  <span>←</span>
                  <span>Home</span>
                </button>
                
                <div className="relative floating-bw">
                  <div className="w-12 h-12 bg-gradient-to-br from-white to-gray-300 rounded-xl flex items-center justify-center shadow-bw border border-white/20">
                    <div className="text-black text-lg font-bold font-mono">{'</>'}</div>
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-gradient-to-r from-white to-gray-200 rounded-full border-2 border-black shadow-bw pulse-bw"></div>
                </div>
                <div>
                  <h1 className="text-2xl font-bold gradient-text-bw tracking-tight">
                    CodeCrafter
                  </h1>
                  <div className="flex items-center space-x-3">
                    <p className="text-bw-secondary text-sm font-medium">
                      ✨ Premium AI Development Platform
                    </p>
                    <div className={`flex items-center space-x-1 text-xs px-2 py-1 rounded-full ${
                      isConnected 
                        ? 'bg-white/20 text-white border border-white/30' 
                        : 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
                    }`}>
                      <div className={`w-2 h-2 rounded-full ${
                        isConnected ? 'bg-white' : 'bg-gray-400'
                      } ${isConnected ? 'animate-pulse' : ''}`}></div>
                      <span className="font-medium">
                        {isConnected ? 'Connected' : 'Disconnected'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Black & White Navigation */}
              <nav className="flex space-x-2 glass-bw rounded-lg p-2 border border-white/20">
                <button
                  onClick={() => setActiveTab('generator')}
                  className={`px-4 py-2 rounded-lg transition-bw font-semibold text-sm relative overflow-hidden ${
                    activeTab === 'generator'
                      ? 'btn-bw-primary text-black shadow-bw'
                      : 'text-bw-secondary hover:text-bw-primary hover:bg-white/30'
                  }`}
                >
                  🚀 Generator
                </button>
                <button
                  onClick={() => setActiveTab('run')}
                  className={`px-4 py-2 rounded-lg transition-bw font-semibold text-sm relative overflow-hidden ${
                    activeTab === 'run'
                      ? 'btn-bw-primary text-black shadow-bw'
                      : 'text-bw-secondary hover:text-bw-primary hover:bg-white/30'
                  }`}
                >
                  ⚡ Run & Test
                  {runningProjects.length > 0 && (
                    <span className="absolute -top-1 -right-1 status-bw-success text-black text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
                      {runningProjects.length}
                    </span>
                  )}
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`px-4 py-2 rounded-lg transition-bw font-semibold text-sm relative overflow-hidden ${
                    activeTab === 'history'
                      ? 'btn-bw-primary text-black shadow-bw'
                      : 'text-bw-secondary hover:text-bw-primary hover:bg-white/30'
                  }`}
                >
                  📚 Archive
                </button>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-8">
          {activeTab === 'generator' && (
            <div className="grid grid-cols-3 xl:grid-cols-3 gap-8 generator-bw">
              {/* Premium Black & White Input Section */}
              <div className="xl:col-span-1">
                <div className="card-bw-glow p-6 shadow-bw-xl hover:shadow-bw-xl transition-bw">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-10 h-10 bg-gradient-to-br from-white to-gray-300 rounded-xl flex items-center justify-center shadow-bw floating-bw">
                      <span className="text-black text-lg">✨</span>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-bw-primary">Project Specification</h2>
                      <p className="text-bw-secondary text-sm">Define your dream project</p>
                    </div>
                  </div>
                  
                  <div className="space-y-6">
                    <div className="relative">
                      <label className="block text-sm font-semibold text-bw-primary mb-3">
                        💭 Project Description
                      </label>
                      <textarea
                        className="input-bw w-full h-40 p-4 resize-none focus-bw text-sm leading-relaxed"
                        placeholder="🚀 Describe your Python project in detail...

💡 Example: Create a web scraping application that extracts product information from e-commerce websites, stores data in PostgreSQL database, and generates beautiful analytical reports with interactive data visualization charts."
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        disabled={isGenerating}
                      />
                      <div className="absolute bottom-3 right-3 text-xs text-bw-muted bg-black/70 px-2 py-1 rounded-lg backdrop-blur-sm">
                        {prompt.length}/2000
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      {/* Mode Selection - Enhanced Slider */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <label className="block text-sm font-semibold text-bw-primary">
                            🚀 Generation Mode
                          </label>
                          <div className="text-xs text-bw-secondary">
                            {mode === 'simple' ? 'Quick & Easy' : 'Full-Stack Multi-Agent System'}
                          </div>
                        </div>
                        
                        {/* Toggle Switch */}
                        <div className="relative">
                          <div className="flex items-center space-x-1 bg-black/30 rounded-xl p-1 border border-white/20">
                            <button
                              type="button"
                              onClick={() => setMode('simple')}
                              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                                mode === 'simple'
                                  ? 'bg-white text-black shadow-lg'
                                  : 'text-bw-secondary hover:text-bw-primary'
                              }`}
                            >
                              ⚡ Simple
                            </button>
                            <button
                              type="button"
                              onClick={() => setMode('multi_agent')}
                              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                                mode === 'multi_agent'
                                  ? 'bg-white text-black shadow-lg'
                                  : 'text-bw-secondary hover:text-bw-primary'
                              }`}
                            >
                              🧠 Multi-Agent
                            </button>
                          </div>
                        </div>
                        
                        {/* Mode Description */}
                        <div className="text-xs text-bw-secondary leading-relaxed">
                          {mode === 'simple' ? (
                            <p>
                              <span className="text-white font-medium">⚡ Simple Mode:</span><br/>
                              Quick project generation with basic agents. Ideal for standard applications, scripts, and prototypes.
                            </p>
                          ) : (
                            <p>
                              <span className="text-white font-medium"> Multi-Agent System:</span><br/>
                              Complete full-stack project generation with 8 specialized agents: Project Planner → Domain Expert → Model Selector → Backend Developer → Frontend Developer → Main File Creator → Code Checker → Documentation Agent. Builds complete React + Python applications with AI models.
                            </p>
                          )}
                        </div>
                        
                        {/* Example Prompts */}
                        {mode === 'multi_agent' && (
                          <div className="space-y-3">
                            <div className="text-xs font-medium text-bw-primary">
                              💡 Example Projects for Multi-Agent System:
                            </div>
                            <div className="grid grid-cols-1 gap-2">
                              {[
                                {
                                  title: "🎨 Text-to-Image Generator",
                                  prompt: "Build a text-to-image generator using AI models like Stable Diffusion"
                                },
                                {
                                  title: "📝 AI Content Writer",
                                  prompt: "Create an AI-powered content writing platform with multiple writing styles"
                                },
                                {
                                  title: "🗣️ Voice Assistant System",
                                  prompt: "Build a voice assistant with speech recognition and text-to-speech capabilities"
                                },
                                {
                                  title: "📊 Data Analytics Dashboard",
                                  prompt: "Create a data analytics dashboard with AI-powered insights and predictions"
                                },
                                {
                                  title: "🔍 Document Search Engine",
                                  prompt: "Build an intelligent document search engine with semantic search capabilities"
                                },
                                {
                                  title: "🎵 Music Generation App",
                                  prompt: "Create a music generation application using AI models"
                                }
                              ].map((example, index) => (
                                <button
                                  key={index}
                                  onClick={() => setPrompt(example.prompt)}
                                  className="text-left p-3 bg-black/20 border border-white/20 rounded-lg hover:bg-black/30 hover:border-white/30 transition-all duration-200 group"
                                  disabled={isGenerating}
                                >
                                  <div className="text-xs font-medium text-white group-hover:text-gray-200">
                                    {example.title}
                                  </div>
                                  <div className="text-xs text-bw-secondary mt-1 group-hover:text-bw-primary">
                                    Click to use this example
                                  </div>
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      <button 
                        onClick={handleGenerate}
                        disabled={isGenerating || !prompt.trim()}
                        className="btn-bw-primary w-full py-3 px-6 rounded-xl font-semibold transition-bw shadow-bw hover:shadow-bw-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-3"
                      >
                        {isGenerating ? (
                          <>
                            <div className="spinner-bw"></div>
                            <span>Creating Magic...</span>
                          </>
                        ) : (
                          <>
                            <span>🚀</span>
                            <span>Generate Project</span>
                          </>
                        )}
                      </button>

                      {currentProject?.result?.success && (
                        <button 
                          onClick={handleDownload}
                          className="btn-bw-success w-full py-3 px-6 rounded-xl font-semibold transition-bw shadow-bw hover:shadow-bw-lg flex items-center justify-center space-x-3"
                        >
                          <span>📦</span>
                          <span>Download Project</span>
                        </button>
                      )}
                    </div>

                    {/* Premium Black & White Templates */}
                    <div className="border-t border-white/20 pt-5">
                      <h3 className="text-sm font-bold text-bw-primary mb-4">🎯 Quick Templates</h3>
                      <div className="grid grid-cols-1 gap-2">
                        {[
                          { icon: "🔐", text: "Web API with authentication system" },
                          { icon: "🤖", text: "Data analysis with machine learning" }, 
                          { icon: "🖥️", text: "Desktop application with GUI" },
                          { icon: "⚡", text: "Automation script with scheduling" }
                        ].map((template, idx) => (
                          <button
                            key={idx}
                            onClick={() => setPrompt(template.text)}
                            className="text-left p-3 bg-black/40 hover:bg-black/60 rounded-lg text-sm text-bw-secondary hover:text-bw-primary transition-bw border border-white/20 hover:border-white/40 shadow-bw hover:shadow-bw-lg"
                          >
                            <div className="flex items-center space-x-2">
                              <span className="text-base">{template.icon}</span>
                              <span className="font-medium">{template.text}</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Premium Black & White Logs Section */}
              <div className="xl:col-span-2">
                <div className="card-bw-glow p-6 h-[700px] flex flex-col shadow-bw-xl">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-white to-gray-300 rounded-xl flex items-center justify-center shadow-bw floating-bw">
                        <span className="text-black text-lg">🎯</span>
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-bw-primary">Development Console</h2>
                        <p className="text-bw-secondary text-sm">Real-time AI agent collaboration ✨</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setShowAdvancedLogs(!showAdvancedLogs)}
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-bw border ${
                          showAdvancedLogs 
                            ? 'btn-bw-primary text-black' 
                            : 'btn-bw-secondary'
                        }`}
                      >
                        {showAdvancedLogs ? '🔍 Advanced' : '📋 Simple'}
                      </button>
                      {logs.length > 0 && (
                        <button
                          onClick={() => setLogs([])}
                          className="text-bw-muted hover:text-bw-primary px-4 py-3 rounded-xl hover:bg-white/20 transition-bw border border-white/20 text-sm font-medium"
                        >
                          🗑️ Clear
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Black & White Generation Statistics */}
                  {(isGenerating || generationStats) && (
                    <div className="mb-8 p-6 glass-bw-strong rounded-xl border border-white/20">
                      <h3 className="text-lg font-bold text-bw-primary mb-4">📊 Generation Metrics</h3>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div className="bg-black/50 p-4 rounded-xl border border-white/20">
                          <div className="text-bw-muted font-medium">🤖 Agent Calls</div>
                          <div className="text-bw-primary font-bold text-xl font-mono">{generationStats?.agentCalls || (isGenerating ? '...' : '0')}</div>
                        </div>
                        <div className="bg-black/50 p-4 rounded-xl border border-white/20">
                          <div className="text-bw-muted font-medium">📁 Files Created</div>
                          <div className="text-bw-primary font-bold text-xl font-mono">{generationStats?.filesCreated || (isGenerating ? '...' : '0')}</div>
                        </div>
                        <div className="bg-black/50 p-4 rounded-xl border border-white/20">
                          <div className="text-bw-muted font-medium">⏱️ Duration</div>
                          <div className="text-bw-primary font-bold text-xl font-mono">{generationStats?.duration || (isGenerating ? 'Active' : '0s')}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Black & White Execution Results */}
                  {executionResult && (
                    <div className="mb-8 p-6 glass-bw-strong rounded-xl border border-white/20">
                      <h3 className="text-lg font-bold text-bw-primary mb-4 flex items-center space-x-3">
                        <span>🚀 Execution Result</span>
                        <span className={`text-sm px-3 py-1 rounded-lg font-semibold ${
                          executionResult.success 
                            ? 'status-bw-success text-black' 
                            : 'status-bw-error text-white'
                        }`}>
                          {executionResult.method}
                        </span>
                      </h3>
                      
                      {executionResult.method === 'streamlit' && executionResult.success ? (
                        <div className="bg-black/20 border border-white/30 rounded p-3 text-sm">
                          <div className="text-white font-medium mb-2 flex items-center space-x-2">
                            <span>🌐 Streamlit App Running</span>
                            {executionResult.auto_opened && (
                              <span className="text-xs bg-white/20 px-2 py-1 rounded">Auto-opened</span>
                            )}
                          </div>
                          <div className="text-bw-secondary text-xs mb-3">
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
                              className="text-white underline hover:text-gray-300 font-mono text-xs flex items-center space-x-1"
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
                              className="px-3 py-1.5 bg-white/20 text-white rounded text-xs hover:bg-white/30 transition-colors border border-white/50 flex items-center space-x-1"
                            >
                              <span>🛑</span>
                              <span>Stop Server</span>
                            </button>
                            <button
                              onClick={() => window.open('http://localhost:8501', '_blank')}
                              className="px-3 py-1.5 bg-white/10 text-white rounded text-xs hover:bg-white/20 transition-colors border border-white/50 flex items-center space-x-1"
                            >
                              <span>🔗</span>
                              <span>Open in New Tab</span>
                            </button>
                          </div>
                        </div>
                      ) : executionResult.method === 'web' && executionResult.success ? (
                        <div className="bg-black/20 border border-white/30 rounded p-3 text-sm">
                          <div className="text-white font-medium mb-2 flex items-center space-x-2">
                            <span>🌐 Web Application Running</span>
                            {executionResult.auto_opened && (
                              <span className="text-xs bg-white/20 px-2 py-1 rounded">Auto-opened</span>
                            )}
                          </div>
                          <div className="text-bw-secondary text-xs mb-3">
                            {executionResult.auto_opened ? 
                              'Web application opened automatically in your browser' : 
                              'Access your web application at:'
                            }
                          </div>
                          <div className="flex items-center space-x-3 mb-3">
                            <a 
                              href="http://localhost:8080" 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-white underline hover:text-gray-300 font-mono text-xs flex items-center space-x-1"
                            >
                              <span>🔗</span>
                              <span>http://localhost:8080</span>
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
                              className="px-3 py-1.5 bg-white/20 text-white rounded text-xs hover:bg-white/30 transition-colors border border-white/50 flex items-center space-x-1"
                            >
                              <span>🛑</span>
                              <span>Stop Server</span>
                            </button>
                            <button
                              onClick={() => window.open('http://localhost:8080', '_blank')}
                              className="px-3 py-1.5 bg-white/10 text-white rounded text-xs hover:bg-white/20 transition-colors border border-white/50 flex items-center space-x-1"
                            >
                              <span>🔗</span>
                              <span>Open in New Tab</span>
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="text-xs">
                          {executionResult.output && (
                            <pre className="glass-bw-strong p-3 rounded border border-white/20 text-bw-primary overflow-x-auto whitespace-pre-wrap font-mono text-sm">
                              {executionResult.output}
                            </pre>
                          )}
                          {executionResult.error && (
                            <div className="mt-2 bg-white/10 border border-white/30 rounded p-3 text-bw-primary">
                              {executionResult.error}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className="flex-1 overflow-y-auto glass-bw-strong rounded-xl p-6 border border-white/20 backdrop-blur-md">
                    {/* Advanced/Multi-Agent Mode Progress */}
                    {(mode === 'advanced' || mode === 'multi_agent') && isGenerating && (
                      <div className="mb-6 p-4 bg-gradient-to-r from-black/30 to-black/20 border border-white/30 rounded-xl">
                        <div className="flex items-center space-x-3 mb-3">
                          <div className="w-8 h-8 bg-gradient-to-br from-white to-gray-300 rounded-lg flex items-center justify-center animate-pulse">
                            <span className="text-black text-sm">{mode === 'multi_agent' ? '�' : '�🤖'}</span>
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-white">
                              {mode === 'multi_agent' ? 'Multi-Agent Full-Stack System' : 'Advanced AI Agents System'}
                            </h3>
                            <p className="text-sm text-bw-secondary">
                              {mode === 'multi_agent' 
                                ? '8-agent pipeline building complete full-stack application...' 
                                : 'Multi-agent collaboration in progress...'}
                            </p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                          {[
                            { name: 'Planner', icon: '🎯', desc: 'Project Planning' },
                            { name: 'Domain Expert', icon: '🔬', desc: 'Research & Analysis' },
                            { name: 'Model Selector', icon: '🤖', desc: 'AI Model Selection' },
                            { name: 'Backend Dev', icon: '⚙️', desc: 'Python Backend' },
                            { name: 'Frontend Dev', icon: '🎨', desc: 'React Frontend' },
                            { name: 'Main Creator', icon: '🚀', desc: 'Runner & Setup' },
                            { name: 'Code Checker', icon: '🔍', desc: 'Quality Check' },
                            { name: 'Docs Agent', icon: '📚', desc: 'Documentation' }
                          ].map((agent) => {
                            const isActive = logs.some(log => log.message.includes(`[${agent.name}]`)) && 
                                           !logs.some(log => log.message.includes(`[${agent.name}]`) && log.message.includes('✅'));
                            const isCompleted = logs.some(log => log.message.includes(`[${agent.name}]`) && log.message.includes('✅'));
                            
                            return (
                              <div key={agent.name} className={`p-2 rounded-lg border transition-all duration-300 ${
                                isCompleted ? 'bg-green-500/20 border-green-400/50' :
                                isActive ? 'bg-blue-500/20 border-blue-400/50 animate-pulse' :
                                'bg-black/20 border-white/20'
                              }`}>
                                <div className="flex items-center space-x-2">
                                  <span className="text-sm">{agent.icon}</span>
                                  <div className="flex-1 min-w-0">
                                    <div className="text-xs font-medium text-white truncate">{agent.name}</div>
                                    <div className="text-xs text-bw-secondary truncate">{agent.desc}</div>
                                  </div>
                                  {isCompleted && <span className="text-green-400 text-xs">✅</span>}
                                  {isActive && <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    
                    {logs.length === 0 ? (
                      <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                          <div className="w-16 h-16 bg-gradient-to-br from-white to-gray-300 rounded-xl flex items-center justify-center mx-auto mb-6 shadow-bw floating-bw">
                            <span className="text-black text-2xl">🚀</span>
                          </div>
                          <h3 className="text-xl font-bold text-bw-primary mb-3">Ready for Development</h3>
                          <p className="text-bw-secondary mb-6">Enter project specifications to begin AI-powered code generation ✨</p>
                          <div className="text-sm text-bw-muted glass-bw rounded-lg p-4 border border-white/20">
                            🤖 Multi-agent system: Planning → Development → Testing → Optimization
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {logs.map((log, index) => (
                          <div 
                            key={log.id} 
                            className={`p-4 rounded-lg border-l-4 transition-bw shadow-bw ${
                              log.type === 'success' ? 'bg-black/30 border-white text-white' :
                              log.type === 'warning' ? 'bg-black/40 border-gray-300 text-gray-200' :
                              log.type === 'error' ? 'bg-black/50 border-gray-100 text-gray-100' :
                              'bg-black/20 border-gray-400 text-gray-300'
                            }`}
                            style={{
                              animation: `slideInRight 0.5s ease-out ${index * 0.05}s both`
                            }}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <span className="font-semibold text-sm pr-4">{log.message}</span>
                                {showAdvancedLogs && log.details && (
                                  <div className="mt-2 text-xs bg-black/30 p-3 rounded-lg border border-white/20 font-mono">
                                    {typeof log.details === 'string' ? log.details : JSON.stringify(log.details, null, 2)}
                                  </div>
                                )}
                              </div>
                              <span className="text-xs flex-shrink-0 bg-black/50 text-white px-2 py-1 rounded-lg font-mono font-medium">
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

          {/* Black & White Run & Test Tab */}
          {activeTab === 'run' && (
            <div className="space-y-12">
              {/* Black & White Running Projects Status */}
              {runningProjects.length > 0 && (
                <div className="card-bw p-10 shadow-bw-xl">
                  <div className="flex items-center space-x-4 mb-8">
                    <div className="w-14 h-14 bg-black border border-white/30 rounded-2xl flex items-center justify-center shadow-bw-lg">
                      <span className="text-white text-2xl">⚡</span>
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-bw-primary">✨ Currently Running Projects</h3>
                      <p className="text-bw-secondary text-lg">{runningProjects.length} project{runningProjects.length > 1 ? 's' : ''} actively running</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {runningProjects.map((project) => (
                      <div key={project.project_id} className="glass-bw-strong border border-white/30 rounded-2xl p-6 shadow-bw hover:shadow-bw-lg transition-bw">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h4 className="text-bw-primary font-bold text-lg">🚀 Active Project</h4>
                            <p className="text-bw-muted font-mono text-sm bg-white/20 px-3 py-1 rounded-lg inline-block">{project.project_id.substring(0, 8)}...</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-white rounded-full animate-pulse shadow-bw"></div>
                            <span className="text-bw-primary text-sm font-semibold">Running</span>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => window.open('http://localhost:8501', '_blank')}
                            className="btn-bw-primary flex-1 py-3 px-4 rounded-xl text-sm font-semibold flex items-center justify-center space-x-2"
                          >
                            <span>🌐</span>
                            <span>Open App</span>
                          </button>
                          <button
                            onClick={() => stopProject(project.project_id)}
                            className="btn-bw-secondary px-4 py-3 text-white border-white/30 hover:border-white/50 rounded-xl text-sm font-semibold flex items-center space-x-2"
                          >
                            <span>🛑</span>
                            <span>Stop</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="card-bw p-6 shadow-bw-xl">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="w-10 h-10 bg-black border border-white/30 rounded-xl flex items-center justify-center shadow-bw">
                    <span className="text-white text-lg">⚡</span>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-bw-primary">Project Execution Center</h2>
                    <p className="text-bw-secondary text-sm">Run and test your generated Python projects ✨</p>
                  </div>
                </div>

                {projectHistory.length === 0 ? (
                  <div className="text-center py-16">
                    <div className="w-16 h-16 bg-black border border-white/30 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-bw">
                      <span className="text-white text-2xl">⚡</span>
                    </div>
                    <h3 className="text-xl font-bold text-bw-primary mb-3">No Projects Available</h3>
                    <p className="text-bw-secondary mb-6">Generate your first Python project to get started ✨</p>
                    <button
                      onClick={() => setActiveTab('generator')}
                      className="btn-bw-primary px-6 py-3 rounded-xl font-semibold flex items-center space-x-2 shadow-bw mx-auto"
                    >
                      <span>🚀</span>
                      <span>Go to Generator</span>
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-3 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {projectHistory.filter(p => p.status === 'completed').map((project, index) => (
                      <div
                        key={project.id}
                        className="card-bw p-6 hover:scale-105 transition-bw shadow-bw-lg hover:shadow-bw-xl"
                        style={{
                          animation: `scaleIn 0.5s ease-out ${index * 0.1}s both`
                        }}
                      >
                        <div className="flex items-start justify-between mb-4">
                          <h3 className="text-bw-primary font-bold text-lg truncate pr-2">{project.name}</h3>
                          <span className="badge-bw-status">
                            ✅ Ready
                          </span>
                        </div>
                        
                        <p className="text-bw-secondary text-sm mb-6 line-clamp-2">{project.description}</p>
                        
                        <div className="space-y-3">
                          <button
                            onClick={() => runProject(project.id)}
                            disabled={isExecuting}
                            className="btn-bw-success w-full py-2 px-3 rounded-xl font-medium transition-bw shadow-bw hover:shadow-bw-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-sm"
                          >
                            {isExecuting ? (
                              <>
                                <div className="spinner-bw"></div>
                                <span>Running...</span>
                              </>
                            ) : (
                              <>
                                <span>▶️</span>
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
                              className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 glass-bw text-bw-primary rounded-lg hover:bg-white/30 transition-bw border border-white/20 text-sm font-medium shadow-bw"
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
                              className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 glass-bw text-bw-primary rounded-lg hover:bg-white/30 transition-bw border border-white/20 text-sm font-medium shadow-bw"
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
                          <div className="mt-4 pt-4 border-t border-white/20">
                            <div className="text-xs text-bw-muted mb-2 font-medium">Last Execution</div>
                            <div className={`text-sm p-3 rounded-lg border ${
                              executionResult.success
                                ? 'bg-white/10 border-white/30 text-bw-primary'
                                : 'bg-white/5 border-white/20 text-white'
                            }`}>
                              {executionResult.method === 'streamlit' && executionResult.success ? (
                                <div>
                                  <div className="font-medium mb-1">Streamlit Running</div>
                                  <a href="http://localhost:8501" target="_blank" rel="noopener noreferrer" className="underline text-xs">
                                    http://localhost:8501
                                  </a>
                                </div>
                              ) : executionResult.method === 'web' && executionResult.success ? (
                                <div>
                                  <div className="font-medium mb-1">Web Application Running</div>
                                  <a href="http://localhost:8080" target="_blank" rel="noopener noreferrer" className="underline text-xs">
                                    http://localhost:8080
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
            <div className="grid grid-cols-3 lg:grid-cols-3 gap-8">
              {/* Black & White Project List */}
              <div className="lg:col-span-1">
                <div className="card-bw-glow p-6 shadow-bw-xl">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-black border border-white/30 rounded-xl flex items-center justify-center shadow-bw floating-bw">
                        <span className="text-white text-lg">📚</span>
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-bw-primary">Project Archive</h2>
                        <p className="text-bw-secondary text-sm">{projectHistory.length} total projects</p>
                      </div>
                    </div>
                    <button
                      onClick={fetchProjectHistory}
                      className="flex items-center space-x-2 btn-bw-primary px-3 py-2 rounded-lg transition-bw shadow-bw hover:shadow-bw-lg active:scale-95"
                      title="Refresh Projects"
                    >
                      <span className="text-sm">🔄</span>
                      <span className="text-xs font-medium">Refresh</span>
                    </button>
                  </div>
                  
                  <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                    {projectHistory.length === 0 ? (
                      <div className="text-center py-12">
                        <div className="w-16 h-16 bg-black border border-white/30 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-bw">
                          <span className="text-white text-2xl">📚</span>
                        </div>
                        <h3 className="text-lg font-semibold text-bw-primary mb-2">No Projects Available</h3>
                        <p className="text-bw-secondary">Generated projects will be archived here</p>
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
                          className={`p-4 rounded-xl border cursor-pointer transition-bw relative overflow-hidden ${
                            selectedProject?.id === project.id
                              ? 'bg-white/20 border-white/40 shadow-bw-lg card-bw-glow'
                              : 'bg-white/5 border-white/20 hover:border-white/40 hover:bg-white/15 hover:shadow-bw'
                          }`}
                          style={{
                            animation: `slideInLeft 0.3s ease-out ${index * 0.05}s both`
                          }}
                        >
                          
                          <div className="flex items-start justify-between mb-3 pr-10">
                            <div className="flex items-center space-x-2">
                              <div className="w-6 h-6 bg-white border border-black rounded-lg flex items-center justify-center shadow-bw">
                                <span className="text-black text-xs">🗂️</span>
                              </div>
                              <h3 className="text-bw-primary font-semibold text-base truncate">{project.name}</h3>
                            </div>
                          </div>
                          <p className="text-bw-secondary text-sm mb-4 line-clamp-2">{project.description}</p>
                          <div className="flex items-center justify-between text-xs mb-3">
                            <div className="flex items-center space-x-4">
                              <span className="text-bw-muted flex items-center space-x-1 font-medium">
                                <span>📄</span>
                                <span>{project.file_count} files</span>
                              </span>
                            </div>
                            <span className="text-bw-muted font-mono text-xs bg-white/20 px-2 py-1 rounded-lg">
                              {project.created_at}
                            </span>
                          </div>
                          
                          {/* Project Actions */}
                          {project.status === 'completed' && (
                            <div className="flex items-center space-x-2 pt-3 border-t border-white/20">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  runProject(project.id);
                                }}
                                disabled={isExecuting}
                                className="btn-bw-success flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                <span>▶️</span>
                                <span>Run</span>
                              </button>
                              
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  // Download functionality
                                }}
                                className="btn-bw-secondary flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium"
                              >
                                <span>📦</span>
                                <span>Download</span>
                              </button>
                              
                              {executionResult && selectedProject?.id === project.id && (
                                <div className="ml-2">
                                  <span className={`text-xs px-2 py-1 rounded-lg font-medium ${
                                    executionResult.success 
                                      ? 'status-bw-success text-black'
                                      : 'status-bw-error text-white'
                                  }`}>
                                    {executionResult.method === 'streamlit' && executionResult.success ? 'Running' : 
                                     executionResult.method === 'web' && executionResult.success ? 'Running' :
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
                    {/* Black & White File Explorer */}
                    <div className="card-bw-glow p-6 shadow-bw-xl">
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-black border border-white/30 rounded-xl flex items-center justify-center shadow-bw floating-bw">
                            <span className="text-white text-lg">📁</span>
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-bw-primary">File Structure</h3>
                            <p className="text-bw-secondary text-sm">{selectedProject.name}</p>
                          </div>
                        </div>
                      </div>
                      
                      <div className="max-h-[400px] overflow-y-auto pr-2 glass-bw-strong rounded-lg p-4 border border-white/20">
                        <FileExplorer files={projectFiles} />
                      </div>
                    </div>

                    {/* Black & White File Viewer */}
                    <div className="card-bw-glow p-6 shadow-bw-xl">
                      <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-black border border-white/30 rounded-xl flex items-center justify-center shadow-bw floating-bw">
                            <span className="text-white text-lg">👁️</span>
                          </div>
                          <div>
                            <h3 className="text-lg font-bold text-bw-primary">
                              {selectedFile ? selectedFile.name : 'Code Viewer'}
                            </h3>
                            {selectedFile && (
                              <p className="text-bw-muted text-sm font-mono">{selectedFile.path}</p>
                            )}
                          </div>
                        </div>
                        {selectedFile && (
                          <span className="text-xs text-bw-muted bg-white/20 px-3 py-1 rounded border border-white/20 font-mono">
                            {Math.round(selectedFile.size / 1024 * 10) / 10}KB
                          </span>
                        )}
                      </div>
                      
                      <div className="glass-bw rounded-lg p-6 border border-white/20 h-[400px] overflow-auto backdrop-blur-md">
                        {selectedFile ? (
                          <pre className="text-sm text-bw-primary font-mono whitespace-pre-wrap leading-relaxed">
                            {fileContent || (
                              <div className="flex items-center justify-center h-full">
                                <div className="text-center">
                                  <div className="w-8 h-8 border-2 border-white border-t-white/50 rounded-full animate-spin mb-4 mx-auto"></div>
                                  <p className="text-bw-muted">Loading file content...</p>
                                </div>
                              </div>
                            )}
                          </pre>
                        ) : (
                          <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                              <div className="w-16 h-16 bg-black border border-white/30 rounded-lg flex items-center justify-center mx-auto mb-4 shadow-bw">
                                <div className="w-8 h-8">
                                  <svg fill="currentColor" viewBox="0 0 24 24" className="text-bw-muted">
                                    <path d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"/>
                                  </svg>
                                </div>
                              </div>
                              <h4 className="text-lg font-semibold text-bw-primary mb-2">Select File</h4>
                              <p className="text-bw-muted">Choose a file from the structure to view its content</p>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="card-bw-glow backdrop-blur-xl rounded-lg border border-white/20 p-8 shadow-bw-xl">
                    <div className="flex items-center justify-center h-[500px]">
                      <div className="text-center">
                        <div className="w-20 h-20 bg-black border border-white/30 rounded-lg flex items-center justify-center mx-auto mb-6 shadow-bw floating-bw">
                          <div className="w-10 h-10">
                            <svg fill="currentColor" viewBox="0 0 24 24" className="text-white">
                              <path d="M10,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V8C22,6.89 21.1,6 20,6H12L10,4Z"/>
                            </svg>
                          </div>
                        </div>
                        <h3 className="text-xl font-bold text-bw-primary mb-3">Select Project</h3>
                        <p className="text-bw-muted text-base">Choose a project from the archive to explore its structure and code</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Project Results - Black & White Display */}
          {activeTab === 'generator' && currentProject?.result?.success && (
            <div className="mt-10">
              <div className="card-bw backdrop-blur-xl rounded-lg border border-white/30 p-8 shadow-bw-lg bg-white/10">
                <div className="flex items-center space-x-3 mb-8">
                  <div className="w-10 h-10 bg-white border border-black rounded-lg flex items-center justify-center shadow-bw">
                    <div className="w-5 h-5">
                      <svg fill="currentColor" viewBox="0 0 24 24" className="text-black">
                        <path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/>
                      </svg>
                    </div>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-bw-primary">Project Generated Successfully</h2>
                    <p className="text-bw-muted text-sm">Code generation completed and ready for download</p>
                  </div>
                </div>
                
                {currentProject.result.project_plan && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="glass-premium p-4 rounded-lg border border-white/20">
                      <div className="text-sm text-premium-muted mb-2 font-medium">Project Name</div>
                      <div className="text-premium-primary font-semibold">{currentProject.result.project_plan.project_name}</div>
                    </div>
                    <div className="glass-premium p-4 rounded-lg border border-white/20">
                      <div className="text-sm text-premium-muted mb-2 font-medium">Files Generated</div>
                      <div className="text-premium-primary font-semibold">{currentProject.result.project_plan.files?.length || 0}</div>
                    </div>
                    <div className="glass-premium p-4 rounded-lg border border-white/20">
                      <div className="text-sm text-premium-muted mb-2 font-medium">Runtime Test</div>
                      <div className={`font-semibold ${currentProject.result.runtime_success ? 'text-emerald-600' : 'text-red-600'}`}>
                        {currentProject.result.runtime_success ? 'PASSED' : 'FAILED'}
                      </div>
                    </div>
                    <div className="glass-premium p-4 rounded-lg border border-white/20">
                      <div className="text-sm text-premium-muted mb-2 font-medium">Project ID</div>
                      <div className="text-premium-primary font-mono text-sm">{currentProject.project_id?.substring(0, 8)}...</div>
                    </div>
                  </div>
                )}
                
                {currentProject.result.project_plan?.description && (
                  <div className="mt-6 glass-premium p-6 rounded-lg border border-white/20">
                    <div className="text-sm text-premium-muted mb-3 font-semibold">Project Description</div>
                    <div className="text-premium-secondary leading-relaxed">{currentProject.result.project_plan.description}</div>
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

export default CodeGenerator;