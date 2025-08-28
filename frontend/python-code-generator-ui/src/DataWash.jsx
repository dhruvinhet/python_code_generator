import React, { useState, useRef, useEffect } from 'react';
import { 
  Upload, 
  Download, 
  FileSpreadsheet, 
  AlertTriangle, 
  CheckCircle, 
  BarChart3, 
  Settings, 
  Trash2, 
  Filter, 
  Search,
  Zap,
  Brain,
  Eye,
  Wand2,
  TrendingUp,
  Database,
  ArrowLeft,
  Play,
  Loader2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const DataWash = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  const [uploadedFile, setUploadedFile] = useState(null);
  const [dataPreview, setDataPreview] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [dataGraphs, setDataGraphs] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGeneratingGraphs, setIsGeneratingGraphs] = useState(false);
  const [cleaningOptions, setCleaningOptions] = useState({
    removeDuplicates: true,
    handleMissingValues: true,
    standardizeFormats: true,
    detectOutliers: true,
    validateDataTypes: true
  });
  const [activeTab, setActiveTab] = useState('upload');
  const [showManualTools, setShowManualTools] = useState(false);
  const [manualOperation, setManualOperation] = useState('');
  const [selectedGraphModal, setSelectedGraphModal] = useState(null);

  // ESC key handler for modal
  useEffect(() => {
    const handleEscKey = (event) => {
      if (event.key === 'Escape' && selectedGraphModal) {
        setSelectedGraphModal(null);
      }
    };

    document.addEventListener('keydown', handleEscKey);
    return () => {
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [selectedGraphModal]);
  const [manualParams, setManualParams] = useState({});

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadedFile(file);
    setActiveTab('preview');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:5000/api/data/upload', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        setDataPreview({
          filename: result.filename,
          size: result.size,
          rows: result.rows,
          columns: result.columns,
          columnNames: result.column_names,
          sampleData: result.sample_data
        });
        
        // Automatically generate graphs when file is uploaded
        generateDataGraphs();
      } else {
        alert('Error processing file: ' + result.error);
      }
    } catch (error) {
      console.error('Error processing file:', error);
      alert('Error uploading file: ' + error.message);
    }
  };

  const runAIAnalysis = async () => {
    if (!uploadedFile) return;
    
    setIsAnalyzing(true);
    setActiveTab('analysis');
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      
      const response = await fetch('http://localhost:5000/api/data/analyze', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        setAnalysisResults({
          issues: result.issues,
          qualityScore: result.quality_score,
          recommendations: result.recommendations
        });
      } else {
        alert('Error analyzing data: ' + result.error);
      }
    } catch (error) {
      console.error('Error analyzing data:', error);
      alert('Error analyzing data: ' + error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const generateDataGraphs = async () => {
    if (!uploadedFile) return;
    
    setIsGeneratingGraphs(true);
    console.log('Starting graph generation...');
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      
      const response = await fetch('http://localhost:5000/api/data/graphs', {
        method: 'POST',
        body: formData
      });
      
      console.log('Graph response status:', response.status);
      const result = await response.json();
      console.log('Graph result:', result);
      
      if (result.success) {
        setDataGraphs(result.graphs);
        console.log('Graphs set successfully:', Object.keys(result.graphs));
      } else {
        console.error('Graph generation failed:', result.error);
        alert('Error generating graphs: ' + result.error);
      }
    } catch (error) {
      console.error('Error generating graphs:', error);
      alert('Error generating graphs: ' + error.message);
    } finally {
      setIsGeneratingGraphs(false);
    }
  };

  const downloadCleanedData = async () => {
    if (!uploadedFile) return;
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      
      // Add cleaning options
      Object.entries(cleaningOptions).forEach(([key, value]) => {
        formData.append(key, value.toString());
      });
      
      const response = await fetch('http://localhost:5000/api/data/clean', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Create and download the cleaned file
        const blob = new Blob([result.cleaned_data], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = result.filename || 'cleaned_data.csv';
        a.click();
        URL.revokeObjectURL(url);
        
        alert('Data cleaned and downloaded successfully!');
      } else {
        alert('Error cleaning data: ' + result.error);
      }
    } catch (error) {
      console.error('Error cleaning data:', error);
      alert('Error cleaning data: ' + error.message);
    }
  };

  const handleManualCleaning = async (operation, params) => {
    if (!uploadedFile) return;
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('operation', operation);
      
      // Add operation-specific parameters
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          formData.append(key, value.join(','));
        } else {
          formData.append(key, value.toString());
        }
      });
      
      const response = await fetch('http://localhost:5000/api/data/manual-clean', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Create and download the manually cleaned file
        const blob = new Blob([result.cleaned_data], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = result.filename || 'manually_cleaned_data.csv';
        a.click();
        URL.revokeObjectURL(url);
        
        alert('Manual cleaning completed successfully!\n\nChanges made:\n' + result.cleaning_log.join('\n'));
      } else {
        alert('Error in manual cleaning: ' + result.error);
      }
    } catch (error) {
      console.error('Error in manual cleaning:', error);
      alert('Error in manual cleaning: ' + error.message);
    }
  };

  const showManualToolDialog = (tool) => {
    setManualOperation(tool);
    setShowManualTools(true);
  };

  const executeManualOperation = () => {
    if (!manualOperation) return;
    
    let params = {};
    
    switch (manualOperation) {
      case 'filter_rows': {
        const column = prompt('Enter column name:');
        const condition = prompt('Enter condition (equals, not_equals, contains, greater_than, less_than):');
        const value = prompt('Enter value:');
        if (column && condition && value !== null) {
          params = { column, condition, value };
        }
        break;
      }
        
      case 'find_replace': {
        const col = prompt('Enter column name:');
        const findValue = prompt('Enter value to find:');
        const replaceValue = prompt('Enter replacement value:');
        if (col && findValue !== null && replaceValue !== null) {
          params = { column: col, find_value: findValue, replace_value: replaceValue };
        }
        break;
      }
        
      case 'remove_columns': {
        const columnsToRemove = prompt('Enter column names to remove (comma-separated):');
        if (columnsToRemove) {
          params = { columns: columnsToRemove.split(',').map(c => c.trim()) };
        }
        break;
      }
        
      case 'transform_data': {
        const transformColumn = prompt('Enter column name:');
        const transformation = prompt('Enter transformation (uppercase, lowercase, trim_whitespace, to_numeric, to_datetime):');
        if (transformColumn && transformation) {
          params = { column: transformColumn, transformation };
        }
        break;
      }
        
      default:
        alert('Unknown operation');
        return;
    }
    
    if (Object.keys(params).length > 0) {
      handleManualCleaning(manualOperation, params);
    }
    
    setShowManualTools(false);
    setManualOperation('');
    setManualParams({});
  };

  const QualityChart = ({ score }) => {
    const radius = 45;
    const circumference = 2 * Math.PI * radius;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (score / 100) * circumference;
    
    return (
      <div className="relative w-32 h-32">
        <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r={radius}
            stroke="rgb(75 85 99)"
            strokeWidth="8"
            fill="transparent"
            className="opacity-20"
          />
          <circle
            cx="50"
            cy="50"
            r={radius}
            stroke={score >= 80 ? "#10b981" : score >= 60 ? "#f59e0b" : "#ef4444"}
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-white">{score}%</span>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => navigate('/')}
                className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl flex items-center justify-center">
                  <Database className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold">DataWash</h1>
                  <p className="text-sm text-gray-400">AI-Powered Data Cleaning Platform</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium transition-colors">
                Export Report
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Progress Tabs */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center space-x-4">
            {[
              { id: 'upload', label: 'Upload Data', icon: Upload },
              { id: 'preview', label: 'Preview & Analysis', icon: Eye },
              { id: 'analysis', label: 'AI Analysis', icon: Brain },
              { id: 'clean', label: 'Clean Data', icon: Wand2 }
            ].map((tab, index) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              const isCompleted = ['upload', 'preview'].includes(tab.id) && dataPreview;
              const isClickable = tab.id === 'upload' || (tab.id === 'preview' && uploadedFile) || 
                                 (tab.id === 'analysis' && dataPreview) || (tab.id === 'clean' && dataPreview);
              
              return (
                <div key={tab.id} className="flex items-center">
                  <div 
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                      isActive ? 'bg-purple-600' : isCompleted ? 'bg-green-600' : 'bg-gray-800'
                    } ${isClickable ? 'cursor-pointer hover:bg-purple-500' : 'cursor-not-allowed opacity-50'}`}
                    onClick={() => isClickable && setActiveTab(tab.id)}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm font-medium">{tab.label}</span>
                  </div>
                  {index < 3 && (
                    <div className={`w-8 h-0.5 mx-2 ${isCompleted ? 'bg-green-500' : 'bg-gray-700'}`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Upload Section */}
        {activeTab === 'upload' && (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">Upload Your Dataset</h2>
              <p className="text-gray-400">
                Upload your CSV, Excel, or JSON file to start the data cleaning process
              </p>
            </div>

            <div 
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-600 rounded-2xl p-12 text-center hover:border-purple-500 transition-colors cursor-pointer bg-gray-900/30"
            >
              <Upload className="w-16 h-16 mx-auto mb-4 text-purple-400" />
              <h3 className="text-xl font-semibold mb-2">Drop your file here</h3>
              <p className="text-gray-400 mb-4">or click to browse files</p>
              <p className="text-sm text-gray-500">Supports CSV, XLSX, JSON files up to 100MB</p>
              
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileUpload}
                accept=".csv,.xlsx,.xls,.json"
                className="hidden"
              />
            </div>

            {uploadedFile && (
              <div className="mt-6 p-4 bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-3">
                  <FileSpreadsheet className="w-8 h-8 text-green-400" />
                  <div>
                    <p className="font-medium">{uploadedFile.name}</p>
                    <p className="text-sm text-gray-400">
                      {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Preview Section */}
        {activeTab === 'preview' && dataPreview && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">Data Preview</h2>
              <p className="text-gray-400">
                Review your data structure and run AI analysis to identify issues
              </p>
            </div>

            {/* File Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <FileSpreadsheet className="w-5 h-5 text-blue-400" />
                  <span className="text-sm text-gray-400">Rows</span>
                </div>
                <p className="text-2xl font-bold">{dataPreview.rows.toLocaleString()}</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <BarChart3 className="w-5 h-5 text-green-400" />
                  <span className="text-sm text-gray-400">Columns</span>
                </div>
                <p className="text-2xl font-bold">{dataPreview.columns}</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <Database className="w-5 h-5 text-purple-400" />
                  <span className="text-sm text-gray-400">Size</span>
                </div>
                <p className="text-2xl font-bold">{(dataPreview.size / 1024 / 1024).toFixed(1)}MB</p>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-orange-400" />
                  <span className="text-sm text-gray-400">Quality</span>
                </div>
                <p className="text-2xl font-bold">Unknown</p>
              </div>
            </div>

            {/* Data Table Preview */}
            <div className="bg-gray-800 rounded-lg overflow-hidden">
              <div className="p-4 border-b border-gray-700">
                <h3 className="text-lg font-semibold">Sample Data (First 5 rows)</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-700">
                    <tr>
                      {dataPreview.columnNames.map((col, index) => (
                        <th key={index} className="px-4 py-3 text-left text-sm font-medium">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {dataPreview.sampleData.map((row, rowIndex) => (
                      <tr key={rowIndex} className="border-b border-gray-700">
                        {row.map((cell, cellIndex) => (
                          <td key={cellIndex} className="px-4 py-3 text-sm">
                            {cell || <span className="text-gray-500 italic">empty</span>}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-center space-x-4">
              <button
                onClick={runAIAnalysis}
                className="flex items-center space-x-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium transition-colors"
              >
                <Brain className="w-5 h-5" />
                <span>Run AI Analysis</span>
              </button>
              
              <button
                onClick={generateDataGraphs}
                disabled={!uploadedFile || isGeneratingGraphs}
                className="flex items-center space-x-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
              >
                {isGeneratingGraphs ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <BarChart3 className="w-5 h-5" />
                )}
                <span>{isGeneratingGraphs ? 'Generating...' : 'Generate Graphs'}</span>
              </button>
              
              <button 
                onClick={() => setActiveTab('clean')}
                className="flex items-center space-x-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg font-medium transition-colors"
              >
                <Settings className="w-5 h-5" />
                <span>Manual Review</span>
              </button>
            </div>

            {/* Data Quality Graphs */}
            <div className="mt-8">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Data Quality Visualizations</h3>
                <div className="text-xs text-gray-500">
                  {dataGraphs ? `${Object.keys(dataGraphs).length} graphs available` : 'No graphs generated'}
                </div>
              </div>
              
              {isGeneratingGraphs ? (
                <div className="text-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
                  <p className="text-gray-400">Generating matplotlib & seaborn graphs...</p>
                </div>
              ) : dataGraphs && Object.keys(dataGraphs).length > 0 ? (
                <div className="space-y-6">
                  {/* Row 1: Small graphs in 4 columns */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Missing Values Heatmap */}
                    {dataGraphs.missing_values_heatmap && (
                      <div className="bg-gray-800 rounded-lg p-3 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Missing Values Heatmap',
                             image: dataGraphs.missing_values_heatmap
                           })}>
                        <h4 className="text-xs font-medium mb-2 text-gray-400">Missing Values Heatmap</h4>
                        <div className="h-40 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.missing_values_heatmap}`} 
                            alt="Missing Values Heatmap"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-center">Click to view full size</p>
                      </div>
                    )}
                    
                    {/* Data Types Distribution */}
                    {dataGraphs.data_types_distribution && (
                      <div className="bg-gray-800 rounded-lg p-3 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Data Types Distribution',
                             image: dataGraphs.data_types_distribution
                           })}>
                        <h4 className="text-xs font-medium mb-2 text-gray-400">Data Types Distribution</h4>
                        <div className="h-40 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.data_types_distribution}`} 
                            alt="Data Types Distribution"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-center">Click to view full size</p>
                      </div>
                    )}
                    
                    {/* Data Completeness */}
                    {dataGraphs.data_completeness && (
                      <div className="bg-gray-800 rounded-lg p-3 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Overall Data Completeness',
                             image: dataGraphs.data_completeness
                           })}>
                        <h4 className="text-xs font-medium mb-2 text-gray-400">Overall Data Completeness</h4>
                        <div className="h-40 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.data_completeness}`} 
                            alt="Data Completeness"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-center">Click to view full size</p>
                      </div>
                    )}
                    
                    {/* Data Quality Heatmap */}
                    {dataGraphs.quality_heatmap && (
                      <div className="bg-gray-800 rounded-lg p-3 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Data Quality Heatmap',
                             image: dataGraphs.quality_heatmap
                           })}>
                        <h4 className="text-xs font-medium mb-2 text-gray-400">Data Quality Heatmap</h4>
                        <div className="h-40 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.quality_heatmap}`} 
                            alt="Data Quality Heatmap"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-center">Click to view full size</p>
                      </div>
                    )}
                  </div>

                  {/* Row 2: Medium graphs in 3 columns */}
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {/* Missing Values Bar Chart */}
                    {dataGraphs.missing_values_bar && (
                      <div className="bg-gray-800 rounded-lg p-3 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Missing Values by Column',
                             image: dataGraphs.missing_values_bar
                           })}>
                        <h4 className="text-xs font-medium mb-2 text-gray-400">Missing Values by Column</h4>
                        <div className="h-48 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.missing_values_bar}`} 
                            alt="Missing Values Bar Chart"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-center">Click to view full size</p>
                      </div>
                    )}
                    
                    {/* Text Data Analysis */}
                    {dataGraphs.text_analysis && (
                      <div className="bg-gray-800 rounded-lg p-3 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Text Data Length Distribution',
                             image: dataGraphs.text_analysis
                           })}>
                        <h4 className="text-xs font-medium mb-2 text-gray-400">Text Data Length Distribution</h4>
                        <div className="h-48 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.text_analysis}`} 
                            alt="Text Data Analysis"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-center">Click to view full size</p>
                      </div>
                    )}
                    
                    {/* Categorical Counts */}
                    {dataGraphs.categorical_counts && (
                      <div className="bg-gray-800 rounded-lg p-3 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Top Categorical Values',
                             image: dataGraphs.categorical_counts
                           })}>
                        <h4 className="text-xs font-medium mb-2 text-gray-400">Top Categorical Values</h4>
                        <div className="h-48 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.categorical_counts}`} 
                            alt="Categorical Value Counts"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1 text-center">Click to view full size</p>
                      </div>
                    )}
                  </div>

                  {/* Row 3: Wide graphs in 2 columns for better space usage */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {/* Numeric Distributions */}
                    {dataGraphs.numeric_distributions && (
                      <div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Numeric Columns Distribution',
                             image: dataGraphs.numeric_distributions
                           })}>
                        <h4 className="text-sm font-medium mb-3 text-gray-400">Numeric Columns Distribution</h4>
                        <div className="h-64 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.numeric_distributions}`} 
                            alt="Numeric Distributions"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-2 text-center">Click to view full size</p>
                      </div>
                    )}
                    
                    {/* Correlation Matrix */}
                    {dataGraphs.correlation_matrix && (
                      <div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Correlation Matrix',
                             image: dataGraphs.correlation_matrix
                           })}>
                        <h4 className="text-sm font-medium mb-3 text-gray-400">Correlation Matrix</h4>
                        <div className="h-64 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.correlation_matrix}`} 
                            alt="Correlation Matrix"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-2 text-center">Click to view full size</p>
                      </div>
                    )}
                  </div>

                  {/* Row 4: Single wide graph if it exists alone */}
                  {dataGraphs.outliers_detection && (
                    <div className="grid grid-cols-1 gap-4">
                      <div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 cursor-pointer transition-colors"
                           onClick={() => setSelectedGraphModal({
                             title: 'Outliers Detection (Box Plots)',
                             image: dataGraphs.outliers_detection
                           })}>
                        <h4 className="text-sm font-medium mb-3 text-gray-400">Outliers Detection (Box Plots)</h4>
                        <div className="h-64 flex items-center justify-center bg-gray-900 rounded">
                          <img 
                            src={`data:image/png;base64,${dataGraphs.outliers_detection}`} 
                            alt="Outliers Detection"
                            className="max-w-full max-h-full object-contain rounded"
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-2 text-center">Click to view full size</p>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8 bg-gray-800 rounded-lg">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-600" />
                  <p className="text-gray-400">Upload a file to see data quality graphs</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analysis Section */}
        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">AI Analysis Results</h2>
              <p className="text-gray-400">
                Our AI has identified potential data quality issues
              </p>
            </div>

            {isAnalyzing ? (
              <div className="text-center py-12">
                <Loader2 className="w-12 h-12 mx-auto mb-4 animate-spin text-purple-400" />
                <h3 className="text-xl font-semibold mb-2">Analyzing Your Data...</h3>
                <p className="text-gray-400">This may take a few moments</p>
              </div>
            ) : analysisResults && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Quality Score */}
                <div className="bg-gray-800 rounded-lg p-6 text-center">
                  <h3 className="text-lg font-semibold mb-4">Data Quality Score</h3>
                  <QualityChart score={analysisResults.qualityScore} />
                  <p className="text-sm text-gray-400 mt-4">
                    {analysisResults.qualityScore >= 80 ? 'Excellent' : 
                     analysisResults.qualityScore >= 60 ? 'Good' : 'Needs Improvement'}
                  </p>
                </div>

                {/* Issues Found */}
                <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Issues Detected</h3>
                  <div className="space-y-3">
                    {analysisResults.issues.map((issue, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-gray-700">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          issue.severity === 'high' ? 'bg-red-500' :
                          issue.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                        }`} />
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <h4 className="font-medium">{issue.type}</h4>
                            <span className={`text-xs px-2 py-1 rounded ${
                              issue.severity === 'high' ? 'bg-red-500/20 text-red-400' :
                              issue.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' : 
                              'bg-blue-500/20 text-blue-400'
                            }`}>
                              {issue.severity.toUpperCase()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-400 mt-1">{issue.description}</p>
                          {issue.column && issue.column !== 'general' && (
                            <p className="text-xs text-purple-400 mt-1">Column: {issue.column}</p>
                          )}
                          {issue.examples && issue.examples.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs text-gray-500 mb-1">Examples of problematic data:</p>
                              <div className="flex flex-wrap gap-1">
                                {issue.examples.slice(0, 3).map((example, idx) => (
                                  <span key={idx} className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded">
                                    "{example}"
                                  </span>
                                ))}
                                {issue.examples.length > 3 && (
                                  <span className="text-xs text-gray-500">+{issue.examples.length - 3} more</span>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recommendations */}
                <div className="lg:col-span-3 bg-gray-800 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">AI Recommendations</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {analysisResults.recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                        <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
                        <p className="text-sm">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="lg:col-span-3 flex justify-center">
                  <button
                    onClick={() => setActiveTab('clean')}
                    className="flex items-center space-x-2 px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
                  >
                    <Wand2 className="w-5 h-5" />
                    <span>Proceed to Cleaning</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Cleaning Section */}
        {activeTab === 'clean' && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">Data Cleaning Options</h2>
              <p className="text-gray-400">
                Choose your cleaning preferences and download the cleaned dataset
              </p>
            </div>

            {/* Cleaning Options */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Automated Cleaning</h3>
                <div className="space-y-3">
                  {Object.entries(cleaningOptions).map(([key, value]) => (
                    <label key={key} className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) => setCleaningOptions({
                          ...cleaningOptions,
                          [key]: e.target.checked
                        })}
                        className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
                      />
                      <span className="text-sm">
                        {key.replace(/([A-Z])/g, ' $1').toLowerCase().replace(/^./, str => str.toUpperCase())}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Manual Tools</h3>
                <div className="space-y-2">
                  <button 
                    onClick={() => showManualToolDialog('filter_rows')}
                    className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <Filter className="w-5 h-5 text-blue-400" />
                    <span>Filter Rows ({dataPreview?.rows ? dataPreview.rows.toLocaleString() : 0} total)</span>
                  </button>
                  <button 
                    onClick={() => showManualToolDialog('find_replace')}
                    className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <Search className="w-5 h-5 text-green-400" />
                    <span>Find & Replace in {dataPreview?.columns || 0} columns</span>
                  </button>
                  <button 
                    onClick={() => showManualToolDialog('remove_columns')}
                    className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-5 h-5 text-red-400" />
                    <span>Remove Columns (Select from {dataPreview?.columnNames?.length || 0})</span>
                  </button>
                  <button 
                    onClick={() => showManualToolDialog('transform_data')}
                    className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <Zap className="w-5 h-5 text-yellow-400" />
                    <span>Data Transformation</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Real Data Quality Comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 text-red-400">Current Data Status</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Data Quality Score:</span>
                    <span className="text-red-400">
                      {analysisResults ? `${analysisResults.qualityScore}%` : 'Not analyzed'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Missing Values:</span>
                    <span className="text-red-400">
                      {dataPreview ? dataPreview.sampleData.flat().filter(cell => !cell || cell === '').length : 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Rows:</span>
                    <span className="text-yellow-400">{dataPreview?.rows?.toLocaleString() || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Columns:</span>
                    <span className="text-blue-400">{dataPreview?.columns || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Issues Found:</span>
                    <span className="text-red-400">
                      {analysisResults ? analysisResults.issues.length : 'Run AI analysis'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4 text-green-400">After Cleaning (Preview)</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Expected Quality Score:</span>
                    <span className="text-green-400">95%+</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Missing Values:</span>
                    <span className="text-green-400">
                      {cleaningOptions.handleMissingValues ? '0' : 'Will remain'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Duplicate Rows:</span>
                    <span className="text-green-400">
                      {cleaningOptions.removeDuplicates ? 'Removed' : 'Will remain'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Data Types:</span>
                    <span className="text-green-400">
                      {cleaningOptions.validateDataTypes ? 'Validated' : 'Not validated'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Format Issues:</span>
                    <span className="text-green-400">
                      {cleaningOptions.standardizeFormats ? 'Fixed' : 'Will remain'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Download Section */}
            <div className="text-center">
              <button
                onClick={downloadCleanedData}
                className="flex items-center space-x-2 px-8 py-4 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors mx-auto"
              >
                <Download className="w-5 h-5" />
                <span>Download Cleaned Data</span>
              </button>
              <p className="text-sm text-gray-400 mt-2">
                Data will be downloaded as a CSV file with all issues resolved
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Manual Tools Dialog */}
      {showManualTools && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Execute Manual Operation</h3>
            <p className="text-gray-400 mb-4">
              Operation: <span className="text-white font-medium">{manualOperation}</span>
            </p>
            <p className="text-sm text-gray-400 mb-6">
              This will open prompts to collect the necessary parameters for the operation.
            </p>
            
            <div className="flex space-x-3">
              <button
                onClick={executeManualOperation}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Execute
              </button>
              <button
                onClick={() => {
                  setShowManualTools(false);
                  setManualOperation('');
                }}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Graph Modal for Full Size View */}
      {selectedGraphModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-lg max-w-6xl max-h-[90vh] w-full overflow-hidden">
            {/* Modal Header */}
            <div className="flex justify-between items-center p-4 border-b border-gray-700">
              <h3 className="text-lg font-semibold text-white">{selectedGraphModal.title}</h3>
              <button
                onClick={() => setSelectedGraphModal(null)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* Modal Content */}
            <div className="p-4 overflow-auto max-h-[calc(90vh-80px)]">
              <div className="flex justify-center">
                <img 
                  src={`data:image/png;base64,${selectedGraphModal.image}`} 
                  alt={selectedGraphModal.title}
                  className="max-w-full h-auto rounded"
                  style={{ maxHeight: 'calc(90vh - 120px)' }}
                />
              </div>
            </div>
            
            {/* Modal Footer */}
            <div className="p-4 border-t border-gray-700 text-center">
              <p className="text-sm text-gray-400">
                Right-click to save image • Press ESC to close
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataWash;
