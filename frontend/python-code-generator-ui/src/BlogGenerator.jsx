import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  PenTool, 
  Brain, 
  Search, 
  Sparkles, 
  Plus,
  Check,
  X,
  Loader2,
  BookOpen,
  Edit3,
  Save,
  Download,
  Share,
  Eye
} from 'lucide-react';

const BlogGenerator = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [blogTopic, setBlogTopic] = useState('');
  const [customTopics, setCustomTopics] = useState([]);
  const [newCustomTopic, setNewCustomTopic] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [generatedBlog, setGeneratedBlog] = useState('');
  const [blogTitle, setBlogTitle] = useState('');
  const [selectedTopics, setSelectedTopics] = useState([]);

  const API_BASE_URL = 'http://localhost:5000';

  // Step 1: Plan blog topics based on user input
  const handlePlanBlog = async () => {
    if (!blogTopic.trim()) {
      alert('Please enter a blog topic');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/blog/plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: blogTopic })
      });

      const data = await response.json();
      if (data.success) {
        setSelectedTopics(data.subtopics);
        setBlogTitle(data.title);
        setCurrentStep(2);
      } else {
        alert('Error planning blog: ' + data.error);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error connecting to server');
    } finally {
      setIsLoading(false);
    }
  };

  // Add custom topic
  const handleAddCustomTopic = () => {
    if (newCustomTopic.trim() && !customTopics.includes(newCustomTopic.trim())) {
      const newTopic = newCustomTopic.trim();
      setCustomTopics([...customTopics, newTopic]);
      setSelectedTopics([...selectedTopics, newTopic]);
      setNewCustomTopic('');
    }
  };

  // Remove topic from selected
  const handleRemoveTopic = (topicToRemove) => {
    setSelectedTopics(selectedTopics.filter(topic => topic !== topicToRemove));
    setCustomTopics(customTopics.filter(topic => topic !== topicToRemove));
  };

  // Generate blog content
  const handleGenerateBlog = async () => {
    if (selectedTopics.length === 0) {
      alert('Please select at least one topic');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/blog/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          mainTopic: blogTopic,
          subtopics: selectedTopics,
          title: blogTitle
        })
      });

      const data = await response.json();
      if (data.success) {
        setGeneratedBlog(data.blog);
        setCurrentStep(3);
      } else {
        alert('Error generating blog: ' + data.error);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error connecting to server');
    } finally {
      setIsLoading(false);
    }
  };

  // Copy blog content
  const handleCopyBlog = () => {
    navigator.clipboard.writeText(generatedBlog);
    alert('Blog content copied to clipboard!');
  };

  // Download blog as text file
  const handleDownloadBlog = () => {
    const element = document.createElement('a');
    const file = new Blob([generatedBlog], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `${blogTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => navigate('/')}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
                  <PenTool className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">BlogBot</h1>
                  <p className="text-sm text-gray-400">AI-Powered Blog Generator</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {[1, 2, 3].map((step) => (
                <div
                  key={step}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                    currentStep >= step
                      ? 'bg-orange-500 text-white'
                      : 'bg-white/10 text-gray-400'
                  }`}
                >
                  {step}
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Step 1: Topic Input */}
        {currentStep === 1 && (
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center mx-auto">
                <Brain className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-3xl font-bold">What would you like to write about?</h2>
              <p className="text-gray-400 max-w-2xl mx-auto">
                Enter your main blog topic and our AI will help you plan the perfect structure with relevant subtopics.
              </p>
            </div>

            <div className="max-w-2xl mx-auto space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">Blog Topic</label>
                <textarea
                  value={blogTopic}
                  onChange={(e) => setBlogTopic(e.target.value)}
                  placeholder="e.g., The Future of Artificial Intelligence in Healthcare"
                  className="w-full h-32 p-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-orange-500 resize-none"
                />
              </div>

              <button
                onClick={handlePlanBlog}
                disabled={isLoading || !blogTopic.trim()}
                className="w-full bg-gradient-to-r from-orange-500 to-red-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg hover:shadow-orange-500/25 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Planning your blog...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Plan My Blog</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Topic Selection */}
        {currentStep === 2 && (
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto">
                <Edit3 className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-3xl font-bold">Review & Customize Your Blog Structure</h2>
              <p className="text-gray-400 max-w-2xl mx-auto">
                Here are the suggested subtopics for your blog. You can remove any you don't want or add additional ones.
              </p>
            </div>

            <div className="max-w-4xl mx-auto space-y-6">
              {/* Blog Title */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-3">Blog Title</h3>
                <input
                  value={blogTitle}
                  onChange={(e) => setBlogTitle(e.target.value)}
                  className="w-full p-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-orange-500"
                />
              </div>

              {/* Selected Topics */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4">Selected Subtopics ({selectedTopics.length})</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {selectedTopics.map((topic, index) => (
                    <div key={index} className="flex items-center justify-between bg-white/5 border border-white/10 rounded-lg p-3">
                      <span className="text-sm">{topic}</span>
                      <button
                        onClick={() => handleRemoveTopic(topic)}
                        className="text-red-400 hover:text-red-300"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Add Custom Topic */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4">Add Custom Subtopic</h3>
                <div className="flex space-x-3">
                  <input
                    value={newCustomTopic}
                    onChange={(e) => setNewCustomTopic(e.target.value)}
                    placeholder="Enter additional subtopic..."
                    className="flex-1 p-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-orange-500"
                    onKeyPress={(e) => e.key === 'Enter' && handleAddCustomTopic()}
                  />
                  <button
                    onClick={handleAddCustomTopic}
                    className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors flex items-center space-x-2"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add</span>
                  </button>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={() => setCurrentStep(1)}
                  className="flex-1 bg-white/10 text-white py-4 rounded-xl font-semibold hover:bg-white/20 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleGenerateBlog}
                  disabled={isLoading || selectedTopics.length === 0}
                  className="flex-1 bg-gradient-to-r from-orange-500 to-red-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg hover:shadow-orange-500/25 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Generating Blog...</span>
                    </>
                  ) : (
                    <>
                      <BookOpen className="w-5 h-5" />
                      <span>Generate Blog</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Generated Blog */}
        {currentStep === 3 && (
          <div className="space-y-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto">
                <Check className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-3xl font-bold">Your Blog is Ready!</h2>
              <p className="text-gray-400 max-w-2xl mx-auto">
                Here's your AI-generated blog post. You can copy, download, or share it.
              </p>
            </div>

            <div className="max-w-4xl mx-auto space-y-6">
              {/* Action Buttons */}
              <div className="flex flex-wrap gap-4 justify-center">
                <button
                  onClick={handleCopyBlog}
                  className="flex items-center space-x-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <Save className="w-4 h-4" />
                  <span>Copy</span>
                </button>
                <button
                  onClick={handleDownloadBlog}
                  className="flex items-center space-x-2 px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
                <button
                  onClick={() => {
                    setBlogTopic('');
                    setSelectedTopics([]);
                    setCustomTopics([]);
                    setGeneratedBlog('');
                    setBlogTitle('');
                    setCurrentStep(1);
                  }}
                  className="flex items-center space-x-2 px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>New Blog</span>
                </button>
              </div>

              {/* Blog Content */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-8">
                <div 
                  className="prose prose-invert max-w-none"
                  style={{ 
                    color: '#ffffff',
                    lineHeight: '1.7',
                    fontSize: '16px'
                  }}
                  dangerouslySetInnerHTML={{ 
                    __html: generatedBlog.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>')
                  }}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BlogGenerator;
