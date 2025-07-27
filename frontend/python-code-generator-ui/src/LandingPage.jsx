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
  Twitter
} from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');

  const handleFeatureClick = (feature) => {
    if (feature === 'codecrafter') {
      navigate('/generator');
    } else {
      // For other features, show coming soon (you can implement modals or navigate to coming soon pages)
      alert(`${feature} is coming soon! 🚀`);
    }
  };

  const handleEmailSignup = (e) => {
    e.preventDefault();
    // Handle email signup
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
      color: 'from-blue-500 to-indigo-600'
    },
    {
      id: 'smartslides',
      name: 'SmartSlides',
      icon: Presentation,
      description: 'Create stunning PowerPoint presentations with intelligent design',
      available: false,
      color: 'from-green-500 to-emerald-600'
    },
    {
      id: 'datawash',
      name: 'DataWash',
      icon: Database,
      description: 'Clean and preprocess your data with automated AI workflows',
      available: false,
      color: 'from-purple-500 to-violet-600'
    },
    {
      id: 'blogbot',
      name: 'BlogBot',
      icon: PenTool,
      description: 'Write engaging blog content with AI-powered research and writing',
      available: false,
      color: 'from-orange-500 to-red-600'
    },
    {
      id: 'examforge',
      name: 'ExamForge',
      icon: GraduationCap,
      description: 'Generate comprehensive quizzes and exams using advanced RAG',
      available: false,
      color: 'from-pink-500 to-rose-600'
    }
  ];

  return (
    <div className="min-h-screen bg-white relative overflow-hidden">
      {/* Animated Neural Network Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-r from-blue-100 to-indigo-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
        <div className="absolute top-40 right-20 w-80 h-80 bg-gradient-to-r from-purple-100 to-pink-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse animation-delay-2000"></div>
        <div className="absolute bottom-40 left-40 w-72 h-72 bg-gradient-to-r from-green-100 to-blue-100 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse animation-delay-4000"></div>
      </div>

      {/* Subtle Grid Pattern */}
      <div 
        className="absolute inset-0 opacity-5"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%236366f1' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}
      ></div>

      {/* Navigation */}
      <nav className="relative z-10 border-b border-gray-100 bg-white/80 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                Synexor AI
              </span>
            </div>
            <div className="flex items-center space-x-6">
              <a href="#features" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">Features</a>
              <a href="#how-it-works" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">How It Works</a>
              <a href="#about" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">About</a>
              <button className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-6 py-2 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-800 transition-all shadow-lg hover:shadow-xl">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="relative z-10">
        {/* Hero Section */}
        <section className="py-20 lg:py-32">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center max-w-5xl mx-auto">
              <div className="mb-8">
                <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-blue-50 text-blue-700 border border-blue-200">
                  <Zap className="w-4 h-4 mr-2" />
                  Powered by Multi-Agent AI System
                </span>
              </div>
              
              <h1 className="text-5xl lg:text-7xl font-bold mb-8 leading-tight">
                <span className="bg-gradient-to-r from-gray-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent">
                  Build Smarter.
                </span>
                <br />
                <span className="bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
                  Faster. Limitlessly.
                </span>
              </h1>
              
              <p className="text-xl lg:text-2xl text-gray-600 mb-12 leading-relaxed max-w-4xl mx-auto">
                All-in-One AI Suite for Developers, Creators & Analysts.
                <br />
                <span className="text-lg text-gray-500">Transform ideas into reality with our intelligent multi-agent workforce.</span>
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
                <button 
                  onClick={() => handleFeatureClick('codecrafter')}
                  className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-8 py-4 rounded-2xl font-semibold text-lg flex items-center gap-3 hover:from-blue-700 hover:to-indigo-800 transition-all shadow-xl hover:shadow-2xl transform hover:-translate-y-1"
                >
                  Launch Synexor One
                  <ArrowRight className="w-5 h-5" />
                </button>
                <button className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-2xl font-semibold text-lg flex items-center gap-3 hover:border-gray-400 hover:bg-gray-50 transition-all">
                  <Play className="w-5 h-5" />
                  Watch Demo
                </button>
              </div>

              {/* Live Demo Console */}
              <div className="max-w-4xl mx-auto">
                <div className="bg-gray-900 rounded-2xl shadow-2xl overflow-hidden">
                  <div className="bg-gray-800 px-6 py-4 flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-gray-400 text-sm ml-4 font-mono">Synexor AI Console</span>
                  </div>
                  <div className="p-6 font-mono text-sm">
                    <div className="text-green-400 mb-2">$ synexor create --prompt "Build a todo app with authentication"</div>
                    <div className="text-gray-300 mb-2">🤖 Planning Agent: Analyzing requirements...</div>
                    <div className="text-blue-400 mb-2">📋 Planning Agent: Created project architecture</div>
                    <div className="text-yellow-400 mb-2">⚡ Developer Agent: Generating backend API...</div>
                    <div className="text-yellow-400 mb-2">🎨 Developer Agent: Creating frontend components...</div>
                    <div className="text-purple-400 mb-2">🧪 Tester Agent: Running unit tests...</div>
                    <div className="text-purple-400 mb-2">✅ Tester Agent: All tests passed</div>
                    <div className="text-green-400 mb-4">🚀 Project generated successfully!</div>
                    <div className="text-cyan-400">Ready to deploy your application 🎉</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-4xl lg:text-5xl font-bold mb-6 text-gray-900">
                Five Powerful AI Tools
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Everything you need to accelerate your creative and technical workflows, 
                powered by intelligent multi-agent systems.
              </p>
            </div>

            <div className="grid lg:grid-cols-3 gap-8 mb-12">
              {features.slice(0, 3).map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div 
                    key={feature.id}
                    onClick={() => handleFeatureClick(feature.id)}
                    className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer border border-gray-100 hover:border-gray-200 transform hover:-translate-y-2"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-2xl font-bold text-gray-900">{feature.name}</h3>
                      {!feature.available && (
                        <span className="bg-gradient-to-r from-orange-400 to-pink-500 text-white text-xs px-3 py-1 rounded-full font-semibold">
                          Coming Soon
                        </span>
                      )}
                      {feature.available && (
                        <span className="bg-gradient-to-r from-green-400 to-emerald-500 text-white text-xs px-3 py-1 rounded-full font-semibold">
                          Available
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 mb-6 leading-relaxed">
                      {feature.description}
                    </p>
                    <div className="flex items-center text-blue-600 font-semibold group-hover:text-blue-700">
                      <span>{feature.available ? 'Launch Tool' : 'Get Notified'}</span>
                      <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="grid lg:grid-cols-2 gap-8 max-w-4xl mx-auto">
              {features.slice(3).map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div 
                    key={feature.id}
                    onClick={() => handleFeatureClick(feature.id)}
                    className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer border border-gray-100 hover:border-gray-200 transform hover:-translate-y-2"
                    style={{ animationDelay: `${(index + 3) * 0.1}s` }}
                  >
                    <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-2xl font-bold text-gray-900">{feature.name}</h3>
                      {!feature.available && (
                        <span className="bg-gradient-to-r from-orange-400 to-pink-500 text-white text-xs px-3 py-1 rounded-full font-semibold">
                          Coming Soon
                        </span>
                      )}
                      {feature.available && (
                        <span className="bg-gradient-to-r from-green-400 to-emerald-500 text-white text-xs px-3 py-1 rounded-full font-semibold">
                          Available
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 mb-6 leading-relaxed">
                      {feature.description}
                    </p>
                    <div className="flex items-center text-blue-600 font-semibold group-hover:text-blue-700">
                      <span>{feature.available ? 'Launch Tool' : 'Get Notified'}</span>
                      <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="py-20">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-4xl lg:text-5xl font-bold mb-6 text-gray-900">
                How Our Multi-Agent System Works
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                From prompt to production - watch our AI agents collaborate 
                to deliver exactly what you need.
              </p>
            </div>

            <div className="grid lg:grid-cols-4 gap-8 mb-16">
              {[
                {
                  step: "01",
                  title: "Planning Agent",
                  description: "Analyzes your prompt and creates a detailed project architecture",
                  icon: Brain,
                  color: "from-blue-500 to-indigo-600"
                },
                {
                  step: "02", 
                  title: "Developer Agent",
                  description: "Generates clean, production-ready code following best practices",
                  icon: Code,
                  color: "from-green-500 to-emerald-600"
                },
                {
                  step: "03",
                  title: "Tester Agent", 
                  description: "Runs comprehensive tests and fixes any bugs automatically",
                  icon: Shield,
                  color: "from-purple-500 to-violet-600"
                },
                {
                  step: "04",
                  title: "Delivery",
                  description: "Provides verified, ready-to-use output with export options",
                  icon: Download,
                  color: "from-orange-500 to-red-600"
                }
              ].map((step, index) => {
                const Icon = step.icon;
                return (
                  <div key={step.step} className="text-center relative">
                    <div className={`w-20 h-20 bg-gradient-to-br ${step.color} rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl`}>
                      <Icon className="w-10 h-10 text-white" />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-bold">
                      {step.step}
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-4">{step.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{step.description}</p>
                    {index < 3 && (
                      <div className="hidden lg:block absolute top-10 left-full w-full">
                        <ArrowRight className="w-6 h-6 text-gray-300 mx-auto" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Why Choose Us Section */}
        <section className="py-20 bg-gradient-to-br from-blue-50 to-indigo-100">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-16">
              <h2 className="text-4xl lg:text-5xl font-bold mb-6 text-gray-900">
                Why Synexor AI?
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Experience the future of AI-powered productivity with features 
                designed for professionals and creators.
              </p>
            </div>

            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div className="space-y-8">
                {[
                  "Multi-agent orchestration for complex tasks",
                  "Natural language prompt interface", 
                  "Automated testing and bug fixing",
                  "Production-ready output every time",
                  "Export to multiple formats",
                  "Continuous learning and improvement"
                ].map((feature, index) => (
                  <div key={index} className="flex items-center space-x-4">
                    <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                    <span className="text-lg text-gray-700 font-medium">{feature}</span>
                  </div>
                ))}
              </div>
              
              <div className="bg-white rounded-2xl p-8 shadow-xl">
                <div className="text-center">
                  <Star className="w-16 h-16 text-yellow-500 mx-auto mb-6" />
                  <blockquote className="text-lg text-gray-700 mb-6 italic">
                    "Synexor AI has revolutionized how we approach development. 
                    What used to take days now takes minutes, and the quality 
                    is consistently exceptional."
                  </blockquote>
                  <div className="text-gray-900 font-semibold">Sarah Chen</div>
                  <div className="text-gray-500">Lead Developer, TechCorp</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Email Signup Section */}
        <section className="py-20">
          <div className="max-w-4xl mx-auto px-6 text-center">
            <h2 className="text-4xl lg:text-5xl font-bold mb-6 text-gray-900">
              Ready to Transform Your Workflow?
            </h2>
            <p className="text-xl text-gray-600 mb-12">
              Join thousands of professionals already using Synexor AI. 
              Get early access to new features and exclusive updates.
            </p>
            
            <form onSubmit={handleEmailSignup} className="flex flex-col sm:flex-row gap-4 max-w-lg mx-auto">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email address"
                className="flex-1 px-6 py-4 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none text-lg"
                required
              />
              <button
                type="submit"
                className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-indigo-800 transition-all shadow-lg hover:shadow-xl flex items-center gap-2"
              >
                <Mail className="w-5 h-5" />
                Get Early Access
              </button>
            </form>
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer id="about" className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-4 gap-8 mb-12">
            <div className="lg:col-span-2">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold">Synexor AI</span>
              </div>
              <p className="text-gray-400 text-lg leading-relaxed mb-6">
                Empowering creators, developers, and analysts with intelligent 
                AI tools that understand context and deliver exceptional results.
              </p>
              <div className="flex space-x-4">
                <Github className="w-6 h-6 text-gray-400 hover:text-white cursor-pointer transition-colors" />
                <Linkedin className="w-6 h-6 text-gray-400 hover:text-white cursor-pointer transition-colors" />
                <Twitter className="w-6 h-6 text-gray-400 hover:text-white cursor-pointer transition-colors" />
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-6">Products</h3>
              <div className="space-y-3">
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">CodeCrafter</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">SmartSlides</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">DataWash</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">BlogBot</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">ExamForge</a>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-6">Company</h3>
              <div className="space-y-3">
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">About</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Blog</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Contact</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Privacy Policy</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Terms of Service</a>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8 flex flex-col sm:flex-row justify-between items-center">
            <p className="text-gray-400 mb-4 sm:mb-0">
              © 2025 Synexor AI. All rights reserved.
            </p>
            <p className="text-gray-400">
              Built with ❤️ for the future of work
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;