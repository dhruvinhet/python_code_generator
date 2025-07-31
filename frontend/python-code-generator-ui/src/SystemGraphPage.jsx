import React, { useState, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  ArrowLeft,
  Users,
  Globe,
  Server,
  Brain,
  Code,
  FileText,
  Download,
  CheckCircle,
  Zap,
  Play,
  Pause,
  RotateCcw,
  Layers,
  Database,
  Monitor
} from 'lucide-react';

// Custom Node Components
const UserInterfaceNode = ({ data }) => {
  const IconComponent = data.icon;
  const isActive = data.isActive;
  
  return (
    <div className={`px-6 py-4 shadow-xl rounded-xl border-2 transition-all duration-500 min-w-[300px] ${
      isActive 
        ? 'bg-gradient-to-br from-blue-500 to-blue-600 border-blue-700 scale-105 shadow-2xl' 
        : 'bg-gradient-to-br from-gray-400 to-gray-500 border-gray-600'
    }`}>
      <Handle type="source" position={Position.Bottom} className="w-4 h-4" />
      <div className="text-center">
        <div className={`inline-flex p-3 rounded-full mb-3 ${
          isActive ? 'bg-blue-400 animate-pulse' : 'bg-gray-300'
        }`}>
          <IconComponent className={`w-6 h-6 ${
            isActive ? 'text-white' : 'text-gray-600'
          }`} />
        </div>
        <div className="font-bold text-lg text-white mb-2">{data.label}</div>
        <div className="text-sm text-white/90 mb-3">{data.description}</div>
        {data.currentAction && (
          <div className="bg-white/20 rounded-lg p-3 text-xs text-white/90">
            <div className="font-semibold mb-1">Current Action:</div>
            <div>{data.currentAction}</div>
          </div>
        )}
      </div>
    </div>
  );
};

const BackendNode = ({ data }) => {
  const IconComponent = data.icon;
  const isActive = data.isActive;
  
  return (
    <div className={`px-6 py-4 shadow-xl rounded-xl border-2 transition-all duration-500 min-w-[300px] ${
      isActive 
        ? 'bg-gradient-to-br from-green-500 to-green-600 border-green-700 scale-105 shadow-2xl' 
        : 'bg-gradient-to-br from-gray-400 to-gray-500 border-gray-600'
    }`}>
      <Handle type="target" position={Position.Top} className="w-4 h-4" />
      <Handle type="source" position={Position.Bottom} className="w-4 h-4" />
      <div className="text-center">
        <div className={`inline-flex p-3 rounded-full mb-3 ${
          isActive ? 'bg-green-400 animate-pulse' : 'bg-gray-300'
        }`}>
          <IconComponent className={`w-6 h-6 ${
            isActive ? 'text-white' : 'text-gray-600'
          }`} />
        </div>
        <div className="font-bold text-lg text-white mb-2">{data.label}</div>
        <div className="text-sm text-white/90 mb-3">{data.description}</div>
        {data.currentAction && (
          <div className="bg-white/20 rounded-lg p-3 text-xs text-white/90">
            <div className="font-semibold mb-1">Processing:</div>
            <div>{data.currentAction}</div>
          </div>
        )}
      </div>
    </div>
  );
};

const AgentNode = ({ data }) => {
  const IconComponent = data.icon;
  const isActive = data.isActive;
  const currentStep = data.currentStep;
  
  return (
    <div className={`px-6 py-5 shadow-xl rounded-xl border-2 transition-all duration-500 min-w-[350px] ${
      isActive 
        ? 'bg-gradient-to-br from-purple-500 to-purple-600 border-purple-700 scale-105 shadow-2xl' 
        : 'bg-gradient-to-br from-gray-400 to-gray-500 border-gray-600'
    }`}>
      <Handle type="target" position={Position.Top} className="w-4 h-4" />
      <Handle type="source" position={Position.Bottom} className="w-4 h-4" />
      <div className="text-center">
        <div className={`inline-flex p-3 rounded-full mb-3 ${
          isActive ? 'bg-purple-400 animate-pulse' : 'bg-gray-300'
        }`}>
          <IconComponent className={`w-6 h-6 ${
            isActive ? 'text-white' : 'text-gray-600'
          }`} />
        </div>
        <div className="font-bold text-lg text-white mb-2">{data.label}</div>
        <div className="text-sm text-white/90 mb-4">{data.description}</div>
        
        {/* Sub-steps */}
        <div className="bg-white/10 rounded-lg p-4 text-xs text-white/90">
          <div className="font-semibold mb-3">Processing Steps:</div>
          <div className="space-y-2">
            {data.steps?.map((step, index) => (
              <div key={index} className={`flex items-center gap-2 p-2 rounded transition-all duration-300 ${
                currentStep === index 
                  ? 'bg-white/20 border-l-4 border-yellow-300' 
                  : currentStep > index 
                    ? 'bg-white/10 text-green-200' 
                    : 'bg-white/5 text-white/60'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  currentStep === index 
                    ? 'bg-yellow-300 animate-pulse' 
                    : currentStep > index 
                      ? 'bg-green-300' 
                      : 'bg-gray-500'
                }`}></div>
                <span>{step}</span>
                {currentStep === index && (
                  <div className="ml-auto">
                    <div className="w-3 h-3 border-2 border-yellow-300 border-t-transparent rounded-full animate-spin"></div>
                  </div>
                )}
                {currentStep > index && (
                  <CheckCircle className="w-3 h-3 text-green-300 ml-auto" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const DataFlowNode = ({ data }) => {
  const IconComponent = data.icon;
  const isActive = data.isActive;
  
  return (
    <div className={`px-4 py-3 shadow-lg rounded-lg border-2 transition-all duration-300 min-w-[200px] max-w-[250px] ${
      isActive 
        ? 'bg-orange-50 border-orange-400 shadow-orange-200' 
        : 'bg-gray-50 border-gray-300'
    }`}>
      <div className="text-center">
        <div className={`inline-flex p-2 rounded-full mb-2 ${
          isActive ? 'bg-orange-100 animate-pulse' : 'bg-gray-100'
        }`}>
          <IconComponent className={`w-4 h-4 ${
            isActive ? 'text-orange-600' : 'text-gray-600'
          }`} />
        </div>
        <div className="font-bold text-sm text-gray-800">{data.label}</div>
        <div className="text-xs text-gray-600 mt-1 leading-relaxed">{data.description}</div>
        {data.content && (
          <div className={`mt-2 p-2 rounded text-xs transition-colors ${
            isActive ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-700'
          }`}>
            {data.content}
          </div>
        )}
      </div>
    </div>
  );
};

const nodeTypes = {
  ui: UserInterfaceNode,
  backend: BackendNode,
  agent: AgentNode,
  data: DataFlowNode,
};

const SystemGraphPage = () => {
  const navigate = useNavigate();
  const [isSimulating, setIsSimulating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [simulationSpeed, setSimulationSpeed] = useState(2000);

  // Simulation steps
  const simulationSteps = useMemo(() => [
    { node: 'user-interface', description: 'User enters prompt and clicks Generate' },
    { node: 'api-request', description: 'Frontend sends POST request to backend' },
    { node: 'backend', description: 'Flask backend receives request' },
    { node: 'backend-to-agent', description: 'Backend passes prompt to agent' },
    { node: 'agent', step: 0, description: 'Agent starts planning project structure' },
    { node: 'agent', step: 1, description: 'Agent generates code files' },
    { node: 'agent', step: 2, description: 'Agent saves project to directory' },
    { node: 'backend-response', description: 'Backend sends project ID to frontend' },
    { node: 'user-interface', description: 'Frontend displays generated code' },
  ], []);

  const getInitialNodes = () => [
    // User Interface
    {
      id: 'user-interface',
      type: 'ui',
      position: { x: 400, y: 50 },
      data: {
        label: 'React Frontend',
        description: 'User Interface & Code Display',
        icon: Monitor,
        isActive: false,
        currentAction: null
      },
    },

    // API Request Data Flow
    {
      id: 'api-request',
      type: 'data',
      position: { x: 100, y: 200 },
      data: {
        label: 'API Request',
        description: 'POST /generate',
        content: 'User prompt + configuration',
        icon: Zap,
        isActive: false
      },
    },

    // Backend
    {
      id: 'backend',
      type: 'backend',
      position: { x: 400, y: 350 },
      data: {
        label: 'Flask Backend',
        description: 'API Server & Request Handler',
        icon: Server,
        isActive: false,
        currentAction: null
      },
    },

    // Backend to Agent Data Flow
    {
      id: 'backend-to-agent',
      type: 'data',
      position: { x: 700, y: 500 },
      data: {
        label: 'Prompt Transfer',
        description: 'Internal Processing',
        content: 'Parsed user requirements',
        icon: Database,
        isActive: false
      },
    },

    // Code Generation Agent
    {
      id: 'agent',
      type: 'agent',
      position: { x: 400, y: 650 },
      data: {
        label: 'Code Generation Agent',
        description: 'AI-Powered Python Code Generator',
        icon: Brain,
        isActive: false,
        currentStep: -1,
        steps: [
          'Planning project structure',
          'Generating code files',
          'Saving project directory'
        ]
      },
    },

    // Backend Response Data Flow
    {
      id: 'backend-response',
      type: 'data',
      position: { x: 100, y: 800 },
      data: {
        label: 'API Response',
        description: 'Project Created',
        content: 'Project ID + file paths',
        icon: CheckCircle,
        isActive: false
      },
    },

    // Final Result
    {
      id: 'final-result',
      type: 'data',
      position: { x: 400, y: 950 },
      data: {
        label: 'Generated Project',
        description: 'Ready for Download',
        content: 'Complete Python project with all files',
        icon: Download,
        isActive: false
      },
    },
  ];

  const getInitialEdges = () => [
    // Main flow
    { 
      id: 'e1', 
      source: 'user-interface', 
      target: 'backend', 
      type: 'smoothstep', 
      animated: false,
      style: { strokeWidth: 3, stroke: '#94a3b8' },
      label: 'HTTP Request'
    },
    { 
      id: 'e2', 
      source: 'backend', 
      target: 'agent', 
      type: 'smoothstep', 
      animated: false,
      style: { strokeWidth: 3, stroke: '#94a3b8' },
      label: 'Process Prompt'
    },
    { 
      id: 'e3', 
      source: 'agent', 
      target: 'user-interface', 
      type: 'smoothstep', 
      animated: false,
      style: { strokeWidth: 3, stroke: '#94a3b8' },
      label: 'Return Result',
      sourceHandle: 'bottom',
      targetHandle: 'top'
    },

    // Data flow edges
    { 
      id: 'data1', 
      source: 'api-request', 
      target: 'backend', 
      type: 'smoothstep',
      style: { strokeWidth: 2, stroke: '#f59e0b', strokeDasharray: '5,5' },
      animated: false
    },
    { 
      id: 'data2', 
      source: 'backend', 
      target: 'backend-to-agent', 
      type: 'smoothstep',
      style: { strokeWidth: 2, stroke: '#f59e0b', strokeDasharray: '5,5' },
      animated: false
    },
    { 
      id: 'data3', 
      source: 'backend-to-agent', 
      target: 'agent', 
      type: 'smoothstep',
      style: { strokeWidth: 2, stroke: '#f59e0b', strokeDasharray: '5,5' },
      animated: false
    },
    { 
      id: 'data4', 
      source: 'agent', 
      target: 'backend-response', 
      type: 'smoothstep',
      style: { strokeWidth: 2, stroke: '#f59e0b', strokeDasharray: '5,5' },
      animated: false
    },
    { 
      id: 'data5', 
      source: 'backend-response', 
      target: 'user-interface', 
      type: 'smoothstep',
      style: { strokeWidth: 2, stroke: '#f59e0b', strokeDasharray: '5,5' },
      animated: false
    },
    { 
      id: 'final', 
      source: 'agent', 
      target: 'final-result', 
      type: 'smoothstep',
      style: { strokeWidth: 2, stroke: '#22c55e' },
      animated: false,
      label: 'Project Files'
    },
  ];

  const [nodes, setNodes, onNodesChange] = useNodesState(getInitialNodes());
  const [edges, setEdges, onEdgesChange] = useEdgesState(getInitialEdges());

  const updateNodeState = useCallback((nodeId, updates) => {
    setNodes(nodes => nodes.map(node => 
      node.id === nodeId 
        ? { ...node, data: { ...node.data, ...updates } }
        : { ...node, data: { ...node.data, isActive: false, currentAction: null, currentStep: -1 } }
    ));
  }, [setNodes]);

  const updateEdgeState = useCallback((edgeId, animated = false, color = '#94a3b8') => {
    setEdges(edges => edges.map(edge => 
      edge.id === edgeId 
        ? { ...edge, animated, style: { ...edge.style, stroke: color } }
        : { ...edge, animated: false, style: { ...edge.style, stroke: '#94a3b8' } }
    ));
  }, [setEdges]);

  const runSimulation = useCallback(async () => {
    setIsSimulating(true);
    setCurrentStep(0);

    for (let i = 0; i < simulationSteps.length; i++) {
      const step = simulationSteps[i];
      setCurrentStep(i);

      switch (step.node) {
        case 'user-interface':
          updateNodeState('user-interface', { 
            isActive: true, 
            currentAction: i === 0 ? 'User entering prompt...' : 'Displaying generated code'
          });
          if (i === 0) {
            updateEdgeState('data1', false);
          } else {
            updateEdgeState('data5', true, '#22c55e');
          }
          break;

        case 'api-request':
          updateNodeState('api-request', { isActive: true });
          updateEdgeState('data1', true, '#3b82f6');
          break;

        case 'backend':
          updateNodeState('backend', { 
            isActive: true, 
            currentAction: 'Processing incoming request...'
          });
          updateEdgeState('e1', true, '#22c55e');
          break;

        case 'backend-to-agent':
          updateNodeState('backend-to-agent', { isActive: true });
          updateEdgeState('data2', true, '#8b5cf6');
          updateEdgeState('data3', true, '#8b5cf6');
          break;

        case 'agent':
          updateNodeState('agent', { 
            isActive: true, 
            currentStep: step.step !== undefined ? step.step : -1
          });
          updateEdgeState('e2', true, '#8b5cf6');
          break;

        case 'backend-response':
          updateNodeState('backend-response', { isActive: true });
          updateEdgeState('data4', true, '#22c55e');
          updateEdgeState('final', true, '#22c55e');
          break;
      }

      await new Promise(resolve => setTimeout(resolve, simulationSpeed));
    }

    // Final state - show everything complete
    await new Promise(resolve => setTimeout(resolve, 1000));
    updateNodeState('final-result', { isActive: true });
    setIsSimulating(false);
  }, [simulationSpeed, updateNodeState, updateEdgeState, simulationSteps]);

  const resetSimulation = useCallback(() => {
    setIsSimulating(false);
    setCurrentStep(0);
    setNodes(getInitialNodes());
    setEdges(getInitialEdges());
  }, [setNodes, setEdges]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors font-medium"
              >
                <ArrowLeft className="w-5 h-5" />
                Back to Home
              </button>
              <div className="w-px h-6 bg-gray-300"></div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">System Workflow Visualization</h1>
                <p className="text-sm text-gray-600 mt-1">Complete Python code generation process</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">Synexor AI</div>
              <div className="text-xs text-gray-500">Code Generation System</div>
            </div>
          </div>
        </div>
      </header>

      {/* Control Panel */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={runSimulation}
              disabled={isSimulating}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Play className="w-4 h-4" />
              {isSimulating ? 'Running...' : 'Start Simulation'}
            </button>
            <button
              onClick={resetSimulation}
              className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600">Speed:</label>
              <select
                value={simulationSpeed}
                onChange={(e) => setSimulationSpeed(Number(e.target.value))}
                className="px-3 py-1 border border-gray-300 rounded"
              >
                <option value={1000}>Fast (1s)</option>
                <option value={2000}>Normal (2s)</option>
                <option value={3000}>Slow (3s)</option>
              </select>
            </div>
          </div>
          {isSimulating && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
              Step {currentStep + 1} of {simulationSteps.length}: {simulationSteps[currentStep]?.description}
            </div>
          )}
        </div>
      </div>

      {/* Flowchart Container */}
      <div className="h-[calc(100vh-180px)] relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
          className="bg-gradient-to-br from-slate-50 to-blue-50"
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={true}
        >
          <Background 
            color="#e2e8f0" 
            gap={25} 
            size={1}
            variant="dots"
          />
          <Controls 
            className="bg-white shadow-lg rounded-lg border border-gray-200" 
            showInteractive={false}
          />
          <MiniMap 
            className="bg-white shadow-lg rounded-lg border border-gray-200"
            nodeColor={(node) => {
              if (node.data?.isActive) {
                if (node.type === 'ui') return '#3b82f6';
                if (node.type === 'backend') return '#22c55e';
                if (node.type === 'agent') return '#8b5cf6';
                if (node.type === 'data') return '#f59e0b';
              }
              return '#94a3b8';
            }}
            maskColor="rgba(255, 255, 255, 0.9)"
          />
        </ReactFlow>
        
        {/* Process Steps Info */}
        <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm p-6 rounded-xl shadow-lg border border-gray-200 max-w-sm">
          <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-500" />
            Process Steps
          </h3>
          <div className="space-y-2 text-sm max-h-64 overflow-y-auto">
            {simulationSteps.map((step, index) => (
              <div key={index} className={`flex items-start gap-3 p-2 rounded transition-all ${
                currentStep === index && isSimulating
                  ? 'bg-blue-100 border-l-4 border-blue-500'
                  : currentStep > index
                    ? 'bg-green-50 text-green-700'
                    : 'text-gray-600'
              }`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5 ${
                  currentStep === index && isSimulating
                    ? 'bg-blue-500 text-white animate-pulse'
                    : currentStep > index
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-300 text-gray-600'
                }`}>
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="text-xs leading-relaxed">{step.description}</div>
                </div>
                {currentStep === index && isSimulating && (
                  <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin flex-shrink-0"></div>
                )}
                {currentStep > index && (
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm p-4 rounded-xl shadow-lg border border-gray-200 max-w-xs">
          <h3 className="font-bold text-gray-900 mb-3 flex items-center gap-2">
            <Code className="w-4 h-4 text-blue-500" />
            Component Legend
          </h3>
          <div className="space-y-2 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded"></div>
              <span className="text-gray-700">React Frontend</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gradient-to-r from-green-500 to-green-600 rounded"></div>
              <span className="text-gray-700">Flask Backend</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gradient-to-r from-purple-500 to-purple-600 rounded"></div>
              <span className="text-gray-700">AI Agent</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-orange-100 border border-orange-300 rounded"></div>
              <span className="text-gray-700">Data Flow</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-blue-500"></div>
              <span className="text-gray-700">Active Process</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-orange-500" style={{ borderTop: '2px dashed #f59e0b' }}></div>
              <span className="text-gray-700">Data Transfer</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemGraphPage;
