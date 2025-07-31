import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Code, 
  Presentation, 
  Database, 
  PenTool, 
  GraduationCap,
  ArrowRight, 
  Play,
  CheckCircle,
  Zap,
  Brain,
  Shield,
  Download,
  Star,
  Mail,
  Github,
  Linkedin,
  Twitter,
  Sparkles,
  Layers,
  Target,
  Users,
  TrendingUp,
  Award
} from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');

  const handleFeatureClick = (feature) => {
    if (feature === 'codecrafter') {
      navigate('/generator');
    } else {
      alert(`${feature} is coming soon! 🚀`);
    }
  };

  const handleEmailSignup = (e) => {
    e.preventDefault();
    alert(`Thanks for your interest! We'll notify you at ${email} when Synexor One launches.`);
    setEmail('');
  };

  const features = [
    {
      id: 'codecrafter',
      name: 'CodeCrafter',
      icon: Code,
      description: 'Generate production-ready code with AI-powered multi-agent system',
      available: true,
      color: 'from-blue-500 to-indigo-600',
      accent: 'blue'
    },
    {
      id: 'smartslides',
      name: 'SmartSlides',
      icon: Presentation,
      description: 'Create stunning PowerPoint presentations with intelligent design',
      available: false,
      color: 'from-green-500 to-emerald-600',
      accent: 'green'
    },
    {
      id: 'datawash',
      name: 'DataWash',
      icon: Database,
      description: 'Clean and preprocess your data with automated AI workflows',
      available: false,
      color: 'from-purple-500 to-violet-600',
      accent: 'purple'
    },
    {
      id: 'blogbot',
      name: 'BlogBot',
      icon: PenTool,
      description: 'Write engaging blog content with AI-powered research and writing',
      available: false,
      color: 'from-orange-500 to-red-600',
      accent: 'orange'
    },
    {
      id: 'examforge',
      name: 'ExamForge',
      icon: GraduationCap,
      description: 'Generate comprehensive quizzes and exams using advanced RAG',
      available: false,
      color: 'from-pink-500 to-rose-600',
      accent: 'pink'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 relative overflow-hidden">
      {/* Enhanced Modern Background System */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        {/* Primary Background with More Depth */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900/95 via-blue-900/90 to-gray-900/95"></div>
        
        {/* Dynamic Animated Grid */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `
              linear-gradient(rgba(59, 130, 246, 0.2) 1px, transparent 1px),
              linear-gradient(90deg, rgba(59, 130, 246, 0.2) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
            animation: 'grid-drift 30s linear infinite'
          }}
        />

        {/* Floating Geometric Shapes */}
        <div className="absolute inset-0">
          {[...Array(12)].map((_, i) => (
            <div
              key={`geometric-${i}`}
              className="absolute opacity-30"
              style={{
                width: `${30 + Math.random() * 60}px`,
                height: `${30 + Math.random() * 60}px`,
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                background: `linear-gradient(45deg, 
                  ${['rgba(59, 130, 246, 0.3)', 'rgba(139, 92, 246, 0.3)', 'rgba(6, 182, 212, 0.3)', 'rgba(16, 185, 129, 0.3)', 'rgba(245, 158, 11, 0.3)'][Math.floor(Math.random() * 5)]}, 
                  transparent
                )`,
                borderRadius: Math.random() > 0.5 ? '50%' : '20%',
                animation: `geometric-float ${20 + Math.random() * 15}s ease-in-out infinite`,
                animationDelay: `${Math.random() * 10}s`
              }}
            />
          ))}
        </div>

        {/* Enhanced Gradient Orbs with Animation */}
        <div className="absolute top-20 left-20 w-80 h-80 bg-gradient-to-r from-blue-500/25 to-purple-600/25 rounded-full filter blur-3xl animate-pulse-slow"></div>
        <div className="absolute bottom-20 right-20 w-64 h-64 bg-gradient-to-r from-cyan-500/25 to-blue-600/25 rounded-full filter blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-purple-500/20 to-pink-600/20 rounded-full filter blur-3xl animate-pulse-slow" style={{ animationDelay: '4s' }}></div>
        <div className="absolute top-10 right-1/4 w-48 h-48 bg-gradient-to-r from-green-500/20 to-emerald-600/20 rounded-full filter blur-3xl animate-pulse-slow" style={{ animationDelay: '6s' }}></div>
        <div className="absolute bottom-10 left-1/3 w-56 h-56 bg-gradient-to-r from-orange-500/15 to-yellow-600/15 rounded-full filter blur-3xl animate-pulse-slow" style={{ animationDelay: '8s' }}></div>

        {/* Animated Light Rays */}
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-px h-full bg-gradient-to-b from-transparent via-blue-400/20 to-transparent animate-pulse"></div>
          <div className="absolute top-0 right-1/3 w-px h-full bg-gradient-to-b from-transparent via-purple-400/20 to-transparent animate-pulse" style={{ animationDelay: '2s' }}></div>
          <div className="absolute top-0 left-2/3 w-px h-full bg-gradient-to-b from-transparent via-cyan-400/20 to-transparent animate-pulse" style={{ animationDelay: '4s' }}></div>
        </div>

        {/* Diagonal Grid Overlay */}
        <div 
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `
              linear-gradient(45deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px),
              linear-gradient(-45deg, rgba(139, 92, 246, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '80px 80px',
            animation: 'diagonal-drift 45s linear infinite reverse'
          }}
        />
      </div>

      {/* Enhanced Navigation */}
      <nav className="relative z-50 border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-600 to-cyan-500 rounded-2xl flex items-center justify-center shadow-2xl">
                  <Brain className="w-7 h-7 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-pulse"></div>
              </div>
              <div>
                <span className="text-2xl font-bold bg-gradient-to-r from-white via-blue-200 to-purple-200 bg-clip-text text-transparent">
                  Synexor AI
                </span>
                <div className="text-xs text-blue-300 font-medium">Next-Gen AI Suite</div>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-gray-200 hover:text-white font-medium transition-colors relative group">
                Features
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-400 transition-all group-hover:w-full"></span>
              </a>
              <a href="#how-it-works" className="text-gray-200 hover:text-white font-medium transition-colors relative group">
                How It Works
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-400 transition-all group-hover:w-full"></span>
              </a>
              <button 
                onClick={() => navigate('/graph')}
                className="text-gray-200 hover:text-white font-medium transition-colors relative group cursor-pointer"
              >
                System Graph
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-400 transition-all group-hover:w-full"></span>
              </button>
              <a href="#about" className="text-gray-200 hover:text-white font-medium transition-colors relative group">
                About
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-blue-400 transition-all group-hover:w-full"></span>
              </a>
              <button className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all transform hover:scale-105">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="relative z-10">
        {/* Revolutionary Hero Section */}
        <section className="py-12 lg:py-16 relative">
          <div className="max-w-7xl mx-auto px-6">
            <div className="grid lg:grid-cols-2 gap-16 items-center">
              
              {/* Left Column - Content */}
              <div className="space-y-8">
                {/* Status Badge */}
                <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 backdrop-blur-sm">
                  <Sparkles className="w-4 h-4 mr-2 text-blue-400" />
                  <span className="text-blue-200 text-sm font-medium">Powered by Multi-Agent AI</span>
                  <div className="ml-3 w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                </div>
                
                {/* Revolutionary Typography */}
                <div className="space-y-4">
                  <h1 className="text-4xl lg:text-5xl font-black leading-none" style={{ color: '#ffffff' }}>
                    <span className="block bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                      BUILD
                    </span>
                    <span className="block bg-gradient-to-r from-purple-400 via-pink-500 to-orange-400 bg-clip-text text-transparent">
                      ANYTHING
                    </span>
                    <span className="block bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
                      INSTANTLY
                    </span>
                  </h1>
                  
                  <div className="w-24 h-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"></div>
                  
                  <p className="text-lg lg:text-xl text-white leading-relaxed max-w-xl">
                    The world's first <span className="text-blue-300 font-semibold">multi-agent AI workforce</span> that transforms 
                    ideas into production-ready solutions in minutes, not months.
                  </p>
                </div>

                {/* Enhanced CTA Section */}
                <div className="flex flex-col sm:flex-row gap-4 pt-4">
                  <button 
                    onClick={() => handleFeatureClick('codecrafter')}
                    className="group bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 hover:shadow-xl hover:shadow-blue-500/25 transition-all transform hover:scale-105 relative overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <span className="relative z-10">Launch Synexor One</span>
                    <ArrowRight className="w-6 h-6 relative z-10 group-hover:translate-x-1 transition-transform" />
                  </button>
                  
                  <button className="group border-2 border-white/20 text-white px-8 py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 hover:bg-white/10 hover:border-white/40 transition-all backdrop-blur-sm">
                    <Play className="w-6 h-6 group-hover:scale-110 transition-transform" />
                    Watch Demo
                  </button>
                </div>

                {/* Trust Indicators */}
                <div className="flex items-center gap-8 pt-8">
                  <div className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-blue-400" />
                    <span className="text-white text-sm">10,000+ Developers</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-green-400" />
                    <span className="text-white text-sm">99.9% Uptime</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Award className="w-5 h-5 text-yellow-400" />
                    <span className="text-white text-sm">AI Innovation Award</span>
                  </div>
                </div>
              </div>

              {/* Right Column - Interactive Demo */}
              <div className="relative">
                {/* Floating Cards */}
                <div className="relative">
                  {/* Main Console */}
                  <div className="bg-black/40 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-white/10 transform rotate-3 hover:rotate-0 transition-transform duration-500">
                    {/* Console Header */}
                    <div className="bg-gradient-to-r from-gray-800 to-gray-900 px-6 py-4 flex items-center gap-3 border-b border-white/10">
                      <div className="flex gap-2">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      </div>
                      <span className="text-blue-300 font-mono text-sm">Synexor AI Console</span>
                      <div className="ml-auto flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-ping"></div>
                        <span className="text-green-400 text-xs font-medium">LIVE</span>
                      </div>
                    </div>
                    
                    {/* Console Content */}
                    <div className="p-6 font-mono text-sm space-y-3">
                      <div className="flex items-center gap-2">
                        <span className="text-green-400">$</span>
                        <span className="text-white">synexor create --prompt "E-commerce platform"</span>
                      </div>
                      <div className="text-blue-300">🧠 Planning Agent: Analyzing requirements...</div>
                      <div className="text-cyan-400">📐 Architecture Agent: Designing system...</div>
                      <div className="text-yellow-400">⚡ Developer Agent: Generating code...</div>
                      <div className="text-purple-400">🧪 Tester Agent: Running tests...</div>
                      <div className="text-green-400 font-bold">✅ Platform deployed successfully!</div>
                      <div className="text-gray-400">🌐 Live at: https://your-store.synexor.ai</div>
                    </div>
                  </div>

                  {/* Floating Stats Cards */}
                  <div className="absolute -top-8 -left-8 bg-white/10 backdrop-blur-xl rounded-2xl p-4 border border-white/20 transform -rotate-12 hover:rotate-0 transition-transform duration-300">
                    <div className="text-2xl font-bold text-white">99.9%</div>
                    <div className="text-xs text-gray-300">Success Rate</div>
                  </div>

                  <div className="absolute -bottom-8 -right-8 bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-xl rounded-2xl p-4 border border-blue-500/30 transform rotate-12 hover:rotate-0 transition-transform duration-300">
                    <div className="text-2xl font-bold text-white">2.3s</div>
                    <div className="text-xs text-gray-300">Avg Response</div>
                  </div>

                  <div className="absolute top-1/2 -right-12 bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-xl rounded-2xl p-4 border border-green-500/30 transform rotate-6 hover:rotate-0 transition-transform duration-300">
                    <div className="text-2xl font-bold text-white">5M+</div>
                    <div className="text-xs text-gray-300">Lines Generated</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Redesigned Features Section */}
        <section id="features" className="py-12 relative">
          <div className="max-w-7xl mx-auto px-6">
            {/* Section Header */}
            <div className="text-center mb-12">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 backdrop-blur-sm mb-4">
                <Layers className="w-4 h-4 mr-2 text-purple-400" />
                <span className="text-purple-200 text-sm font-medium">Five Powerful Tools</span>
              </div>
              
              <h2 className="text-3xl lg:text-4xl font-black mb-4">
                <span className="block text-white mb-1">ONE PLATFORM</span>
                <span className="block bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">INFINITE POSSIBILITIES</span>
              </h2>
              
              <p className="text-lg text-white max-w-3xl mx-auto leading-relaxed">
                From code generation to content creation, our AI agents work together 
                to deliver professional results across every domain.
              </p>
            </div>

            {/* Asymmetrical Feature Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Featured Tool - CodeCrafter */}
              <div className="lg:col-span-8 group cursor-pointer" onClick={() => handleFeatureClick('codecrafter')}>
                <div className="bg-gradient-to-br from-blue-500/10 to-indigo-500/10 backdrop-blur-xl rounded-3xl p-6 border border-blue-500/20 hover:border-blue-400/40 transition-all duration-500 h-full relative overflow-hidden">
                  {/* Background Pattern */}
                  <div className="absolute inset-0 opacity-10">
                    <div className="absolute inset-0" style={{
                      backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%233b82f6' fill-opacity='0.4'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                      backgroundSize: '30px 30px'
                    }}></div>
                  </div>
                  
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-6">
                      <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-xl group-hover:scale-110 transition-transform">
                        <Code className="w-8 h-8 text-white" />
                      </div>
                      <span className="bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xs px-3 py-1 rounded-full font-bold">
                        AVAILABLE NOW
                      </span>
                    </div>
                    
                    <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-blue-300 transition-colors" style={{ color: '#ffffff' }}>
                      CodeCrafter
                    </h3>
                    
                    <p className="text-white text-lg mb-4 leading-relaxed">
                      Generate production-ready applications with our advanced multi-agent system. 
                      From simple scripts to complex architectures, CodeCrafter delivers clean, 
                      tested, and documented code every time.
                    </p>
                    
                    <div className="flex items-center text-blue-400 font-bold group-hover:text-blue-300 transition-colors">
                      <span>Launch Tool</span>
                      <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-2 transition-transform" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Secondary Tools */}
              <div className="lg:col-span-4 space-y-6">
                {features.slice(1, 3).map((feature) => {
                  const Icon = feature.icon;
                  return (
                    <div 
                      key={feature.id}
                      onClick={() => handleFeatureClick(feature.id)}
                      className="group bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer relative overflow-hidden"
                    >
                      <div className="flex items-center gap-4 mb-4">
                        <div className={`w-12 h-12 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-bold text-white group-hover:text-purple-300 transition-colors" style={{ color: '#ffffff' }}>
                            {feature.name}
                          </h3>
                          <span className="bg-gradient-to-r from-orange-500 to-pink-600 text-white text-xs px-2 py-1 rounded-full font-medium">
                            Coming Soon
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-white text-sm leading-relaxed mb-4">
                        {feature.description}
                      </p>
                      
                      <div className="flex items-center text-purple-400 font-semibold text-sm group-hover:text-purple-300 transition-colors">
                        <span>Get Notified</span>
                        <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Bottom Row */}
              <div className="lg:col-span-12">
                <div className="grid lg:grid-cols-2 gap-6">
                  {features.slice(3).map((feature) => {
                    const Icon = feature.icon;
                    return (
                      <div 
                        key={feature.id}
                        onClick={() => handleFeatureClick(feature.id)}
                        className="group bg-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer"
                      >
                        <div className="flex items-start gap-4">
                          <div className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                            <Icon className="w-7 h-7 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-3">
                              <h3 className="text-xl font-bold text-white group-hover:text-orange-300 transition-colors" style={{ color: '#ffffff' }}>
                                {feature.name}
                              </h3>
                              <span className="bg-gradient-to-r from-orange-500 to-pink-600 text-white text-xs px-2 py-1 rounded-full font-medium">
                                Coming Soon
                              </span>
                            </div>
                            
                            <p className="text-white leading-relaxed mb-4">
                              {feature.description}
                            </p>
                            
                            <div className="flex items-center text-orange-400 font-semibold group-hover:text-orange-300 transition-colors">
                              <span>Get Notified</span>
                              <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Enhanced How It Works Section */}
        <section id="how-it-works" className="py-12 relative">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-12">
              <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 backdrop-blur-sm mb-4">
                <Target className="w-4 h-4 mr-2 text-cyan-400" />
                <span className="text-cyan-200 text-sm font-medium">Multi-Agent System</span>
              </div>
              
              <h2 className="text-3xl lg:text-4xl font-black mb-4">
                <span className="block text-white mb-1">FROM IDEA</span>
                <span className="block bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">TO REALITY</span>
              </h2>
              
              <p className="text-lg text-white max-w-3xl mx-auto leading-relaxed">
                Watch our specialized AI agents collaborate in real-time to transform 
                your vision into production-ready solutions.
              </p>
            </div>

            {/* Process Flow */}
            <div className="relative">
              {/* Connection Lines */}
              <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500/50 via-purple-500/50 to-cyan-500/50 transform -translate-y-1/2"></div>
              
              <div className="grid lg:grid-cols-4 gap-8 relative z-10">
                {[
                  {
                    step: "01",
                    title: "Planning Agent",
                    description: "Analyzes your prompt and creates detailed project architecture with best practices",
                    icon: Brain,
                    color: "from-blue-500 to-indigo-600",
                    accent: "blue"
                  },
                  {
                    step: "02", 
                    title: "Developer Agent",
                    description: "Generates clean, production-ready code following industry standards and patterns",
                    icon: Code,
                    color: "from-green-500 to-emerald-600",
                    accent: "green"
                  },
                  {
                    step: "03",
                    title: "Tester Agent", 
                    description: "Runs comprehensive tests, identifies bugs, and automatically fixes issues",
                    icon: Shield,
                    color: "from-purple-500 to-violet-600",
                    accent: "purple"
                  },
                  {
                    step: "04",
                    title: "Delivery Agent",
                    description: "Packages and delivers verified, ready-to-deploy solutions with documentation",
                    icon: Download,
                    color: "from-orange-500 to-red-600",
                    accent: "orange"
                  }
                ].map((step) => {
                  const Icon = step.icon;
                  return (
                    <div key={step.step} className="group text-center relative">
                      {/* Step Card */}
                      <div className="bg-white/5 backdrop-blur-xl rounded-3xl p-6 border border-white/10 group-hover:border-white/20 transition-all duration-500 relative overflow-hidden">
                        {/* Background Glow */}
                        <div className={`absolute inset-0 bg-gradient-to-br ${step.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}></div>
                        
                        <div className="relative z-10">
                          {/* Step Number */}
                          <div className="absolute -top-4 -right-4 w-8 h-8 bg-gradient-to-br from-gray-700 to-gray-800 text-white rounded-full flex items-center justify-center text-sm font-bold border border-gray-600 shadow-lg">
                            {step.step}
                          </div>
                          
                          {/* Icon */}
                          <div className={`w-20 h-20 bg-gradient-to-br ${step.color} rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-2xl group-hover:scale-110 transition-transform duration-300`}>
                            <Icon className="w-10 h-10 text-white" />
                          </div>
                          
                          <h3 className="text-xl font-bold text-white mb-4 group-hover:text-blue-300 transition-colors" style={{ color: '#ffffff' }}>
                            {step.title}
                          </h3>
                          
                          <p className="text-white leading-relaxed group-hover:text-gray-100 transition-colors">
                            {step.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        {/* Enhanced CTA Section */}
        <section className="py-12 relative">
          <div className="max-w-4xl mx-auto px-6 text-center">
            <div className="bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-cyan-500/10 backdrop-blur-xl rounded-3xl p-8 border border-white/10 relative overflow-hidden">
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-20">
                <div className="absolute inset-0" style={{
                  backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Cpath d='M20 20c0-11.046-8.954-20-20-20v20h20z'/%3E%3C/g%3E%3C/svg%3E")`,
                  backgroundSize: '40px 40px'
                }}></div>
              </div>
              
              <div className="relative z-10">
                <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 backdrop-blur-sm mb-8">
                  <Sparkles className="w-4 h-4 mr-2 text-green-400" />
                  <span className="text-green-200 text-sm font-medium">Ready to Transform Your Workflow?</span>
                </div>
                
                <h2 className="text-3xl lg:text-4xl font-black mb-4">
                  <span className="block text-white mb-1">JOIN THE</span>
                  <span className="block bg-gradient-to-r from-green-400 to-cyan-400 bg-clip-text text-transparent">AI REVOLUTION</span>
                </h2>
                
                <p className="text-lg text-white mb-8 max-w-2xl mx-auto leading-relaxed">
                  Be among the first to experience the future of AI-powered development. 
                  Get early access and exclusive updates.
                </p>
                
                {/* Enhanced Email Form */}
                <div className="max-w-md mx-auto">
                  <form onSubmit={handleEmailSignup} className="space-y-6">
                    <div className="relative">
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email address"
                        required
                        className="w-full px-6 py-4 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all backdrop-blur-sm text-center"
                      />
                    </div>
                    
                    <button
                      type="submit"
                      className="w-full bg-gradient-to-r from-green-600 to-cyan-600 hover:from-green-700 hover:to-cyan-700 text-white font-bold py-4 px-8 rounded-2xl shadow-xl hover:shadow-green-500/25 transition-all duration-300 transform hover:scale-105 relative overflow-hidden group"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-cyan-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                      <span className="relative z-10 flex items-center justify-center">
                        <Mail className="w-5 h-5 mr-2" />
                        Get Early Access
                      </span>
                    </button>
                  </form>

                  {/* Trust Indicators */}
                  <div className="grid grid-cols-3 gap-6 mt-8 pt-8 border-t border-white/10">
                    <div className="text-center">
                      <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center mx-auto mb-2">
                        <Shield className="w-5 h-5 text-white" />
                      </div>
                      <div className="text-sm text-white">Privacy Protected</div>
                    </div>
                    
                    <div className="text-center">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl flex items-center justify-center mx-auto mb-2">
                        <Zap className="w-5 h-5 text-white" />
                      </div>
                      <div className="text-sm text-white">Instant Access</div>
                    </div>
                    
                    <div className="text-center">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mx-auto mb-2">
                        <Star className="w-5 h-5 text-white" />
                      </div>
                      <div className="text-sm text-white">Premium Features</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* Enhanced Custom Animations */}
      <style jsx>{`
        @keyframes grid-drift {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
        
        @keyframes diagonal-drift {
          0% { transform: translate(0, 0) rotate(0deg); }
          100% { transform: translate(80px, 80px) rotate(360deg); }
        }
        
        @keyframes geometric-float {
          0%, 100% { 
            transform: translate(0, 0) rotate(0deg) scale(1); 
            opacity: 0.3; 
          }
          25% { 
            transform: translate(20px, -20px) rotate(90deg) scale(1.1); 
            opacity: 0.5; 
          }
          50% { 
            transform: translate(-15px, -40px) rotate(180deg) scale(0.9); 
            opacity: 0.4; 
          }
          75% { 
            transform: translate(-30px, -10px) rotate(270deg) scale(1.05); 
            opacity: 0.6; 
          }
        }
        
        @keyframes pulse-slow {
          0%, 100% { 
            opacity: 0.3; 
            transform: scale(1); 
          }
          50% { 
            opacity: 0.6; 
            transform: scale(1.05); 
          }
        }
        
        .animate-pulse-slow {
          animation: pulse-slow 6s ease-in-out infinite;
        }
        
        @keyframes float {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          25% { transform: translate(10px, -10px) rotate(90deg); }
          50% { transform: translate(-10px, -20px) rotate(180deg); }
          75% { transform: translate(-20px, -10px) rotate(270deg); }
        }
      `}</style>
    </div>
  );
};

export default LandingPage;