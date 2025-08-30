import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Code, 
  Presentation, 
  Database, 
  PenTool, 
  GraduationCap,
  Brain,
  Sparkles,
  Zap,
  ArrowRight,
  Star,
  Orbit,
  Cpu,
  Network,
  Bot,
  X,
  Lightbulb,
  Rocket,
  Globe,
  Users
} from 'lucide-react';
import './SolarSystem.css';

const SolarSystem = () => {
  const navigate = useNavigate();
  const [hoveredPlanet, setHoveredPlanet] = useState(null);
  const [isRotating, setIsRotating] = useState(true);
  const [showAgentic, setShowAgentic] = useState(false);
  const [planetRotations, setPlanetRotations] = useState({});

  // Generate static star positions once
  const staticStars = React.useMemo(() => {
    return [...Array(100)].map((_, i) => ({
      id: i,
      left: Math.random() * 100,
      top: Math.random() * 100,
      size: i % 4 === 0 ? 'w-2 h-2' : i % 4 === 1 ? 'w-1 h-1' : i % 4 === 2 ? 'w-0.5 h-0.5' : 'w-1.5 h-1.5',
      opacity: Math.random() > 0.7 ? 'opacity-80' : Math.random() > 0.4 ? 'opacity-60' : 'opacity-40'
    }));
  }, []);

  // Generate static bright stars positions once
  const staticBrightStars = React.useMemo(() => {
    return [...Array(15)].map((_, i) => ({
      id: i,
      left: Math.random() * 100,
      top: Math.random() * 100
    }));
  }, []);

  // Generate static dust cloud positions once
  const staticDustClouds = React.useMemo(() => {
    return [...Array(5)].map((_, i) => ({
      id: i,
      left: 20 + (i * 15),
      top: 10 + (i * 15),
      width: 60 + (i * 20),
      height: 40 + (i * 15),
      color: ['#374151', '#1F2937', '#111827', '#4B5563', '#6B7280'][i % 5]
    }));
  }, []);

  const handleFeatureClick = (feature) => {
    if (feature === 'codecrafter') {
      navigate('/generator');
    } else if (feature === 'blogbot') {
      navigate('/blog');
    } else if (feature === 'datawash') {
      navigate('/data');
    } else if (feature === 'smartslides') {
      navigate('/slide');
    } else {
      alert(`${feature} is coming soon! 🚀`);
    }
  };

  const planets = [
    {
      id: 'codecrafter',
      name: 'CodeCrafter',
      icon: Code,
      description: 'Generate production-ready code with AI-powered multi-agent system. Build complete applications from simple prompts.',
      features: ['Multi-Agent Architecture', 'Production Ready', 'Full Stack Support', 'Auto Documentation'],
      available: true,
      color: 'from-blue-500 to-indigo-600',
      glowColor: 'blue',
      orbitRadius: 190,
      size: 60,
      speed: 20,
      delay: 0
    },
    {
      id: 'smartslides',
      name: 'SmartSlides',
      icon: Presentation,
      description: 'Create stunning PowerPoint presentations with intelligent design and automated content generation.',
      features: ['AI Design', 'Smart Templates', 'Auto Content', 'Export Options'],
      available: true,
      color: 'from-green-500 to-emerald-600',
      glowColor: 'green',
      orbitRadius: 250,
      size: 55,
      speed: 25,
      delay: 72
    },
    {
      id: 'datawash',
      name: 'DataWash',
      icon: Database,
      description: 'Clean and preprocess your data with automated AI workflows and intelligent data transformation.',
      features: ['Data Cleaning', 'Auto Processing', 'Smart Analytics', 'Export Ready'],
      available: true,
      color: 'from-purple-500 to-violet-600',
      glowColor: 'purple',
      orbitRadius: 310,
      size: 58,
      speed: 30,
      delay: 144
    },
    {
      id: 'blogbot',
      name: 'BlogBot',
      icon: PenTool,
      description: 'Write engaging blog content with AI-powered research, writing assistance, and SEO optimization.',
      features: ['Content Research', 'SEO Optimization', 'Multi-Format', 'Publishing Ready'],
      available: true,
      color: 'from-orange-500 to-red-600',
      glowColor: 'orange',
      orbitRadius: 370,
      size: 56,
      speed: 35,
      delay: 216
    },
    {
      id: 'examforge',
      name: 'ExamForge',
      icon: GraduationCap,
      description: 'Generate comprehensive quizzes and exams using advanced RAG technology and intelligent question generation.',
      features: ['Smart Questions', 'RAG Technology', 'Auto Grading', 'Analytics Dashboard'],
      available: false,
      color: 'from-pink-500 to-rose-600',
      glowColor: 'pink',
      orbitRadius: 430,
      size: 54,
      speed: 40,
      delay: 288
    }
  ];

  // Initialize random starting positions for planets
  useEffect(() => {
    const initialRotations = {};
    planets.forEach(planet => {
      initialRotations[planet.id] = Math.random() * 360;
    });
    setPlanetRotations(initialRotations);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // planets is stable, so we can exclude it from deps

  useEffect(() => {
    // Simply set rotation state - CSS will handle pausing
    setIsRotating(!hoveredPlanet);
  }, [hoveredPlanet]);

  const hoveredPlanetDetails = planets.find(p => p.id === hoveredPlanet);

  return (
    <div className="relative w-full h-[900px] flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black">
      {/* Static Galaxy Background */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Static Base Galaxy Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-800"></div>
        
        {/* Static Nebula Effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-gray-900/20 via-black/30 to-gray-800/15"></div>
        <div className="absolute inset-0 bg-gradient-to-br from-gray-800/15 via-gray-900/10 to-black/20"></div>
        
        {/* Static Stars - Different Sizes */}
        {staticStars.map((star) => (
          <div
            key={`star-${star.id}`}
            className="absolute"
            style={{
              left: `${star.left}%`,
              top: `${star.top}%`,
            }}
          >
            <Star 
              className={`${star.size} text-white ${star.opacity}`} 
            />
          </div>
        ))}
        
        {/* Static Bright Stars with Fixed Rays */}
        {staticBrightStars.map((star) => (
          <div
            key={`bright-star-${star.id}`}
            className="absolute"
            style={{
              left: `${star.left}%`,
              top: `${star.top}%`,
            }}
          >
            <div className="relative">
              <div className="w-2 h-2 bg-white rounded-full opacity-90"></div>
              {/* Static cross-shaped star rays */}
              <div className="absolute top-1/2 left-1/2 w-6 h-0.5 bg-white/40 transform -translate-x-1/2 -translate-y-1/2"></div>
              <div className="absolute top-1/2 left-1/2 w-0.5 h-6 bg-white/40 transform -translate-x-1/2 -translate-y-1/2"></div>
            </div>
          </div>
        ))}
        
        {/* Static Galaxy Spiral - Very Subtle */}
        <div className="absolute inset-0 opacity-3">
          <div className="w-full h-full bg-gradient-conic from-gray-600 via-gray-800 to-gray-900"></div>
        </div>
        
        {/* Static Cosmic Dust - No Animation */}
        {staticDustClouds.map((dust) => (
          <div
            key={`dust-${dust.id}`}
            className="absolute rounded-full opacity-5"
            style={{
              left: `${dust.left}%`,
              top: `${dust.top}%`,
              width: `${dust.width}px`,
              height: `${dust.height}px`,
              background: `radial-gradient(ellipse, ${dust.color}15 0%, transparent 70%)`,
            }}
          ></div>
        ))}
      </div>

      {/* Agentic AI Modal */}
      {showAgentic && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-gradient-to-br from-gray-900 via-black to-gray-900 rounded-2xl p-6 max-w-5xl w-full max-h-[90vh] border border-white/20 shadow-2xl relative overflow-y-auto agentic-modal">
            <button
              onClick={() => setShowAgentic(false)}
              className="absolute top-4 right-4 text-white hover:text-red-400 transition-colors z-10"
            >
              <X className="w-6 h-6" />
            </button>
            
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 via-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-2xl">
                <Brain className="w-8 h-8 text-white animate-pulse" />
              </div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent mb-2">
                Agentic AI
              </h2>
              <p className="text-gray-300 text-lg">The Future of Intelligent Automation</p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="bg-black/40 p-4 rounded-xl border border-white/10">
                  <div className="flex items-center gap-3 mb-3">
                    <Cpu className="w-5 h-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-white">Autonomous Intelligence</h3>
                  </div>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    Agentic AI represents a paradigm shift where AI systems can autonomously plan, 
                    execute, and adapt to achieve complex goals without constant human intervention.
                  </p>
                </div>

                <div className="bg-black/40 p-4 rounded-xl border border-white/10">
                  <div className="flex items-center gap-3 mb-3">
                    <Network className="w-5 h-5 text-green-400" />
                    <h3 className="text-lg font-semibold text-white">Multi-Agent Orchestration</h3>
                  </div>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    Our platform leverages multiple specialized AI agents that collaborate, 
                    each bringing unique capabilities to solve complex, multi-faceted problems.
                  </p>
                </div>

                <div className="bg-black/40 p-4 rounded-xl border border-white/10">
                  <div className="flex items-center gap-3 mb-3">
                    <Lightbulb className="w-5 h-5 text-yellow-400" />
                    <h3 className="text-lg font-semibold text-white">Creative Problem Solving</h3>
                  </div>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    Beyond simple task execution, our agents demonstrate creativity, reasoning, 
                    and the ability to break down complex challenges into manageable solutions.
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-black/40 p-4 rounded-xl border border-white/10">
                  <div className="flex items-center gap-3 mb-3">
                    <Rocket className="w-5 h-5 text-purple-400" />
                    <h3 className="text-lg font-semibold text-white">Transformative Applications</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      <span className="text-gray-300 text-sm">Code generation and software development</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      <span className="text-gray-300 text-sm">Content creation and presentation design</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                      <span className="text-gray-300 text-sm">Data analysis and processing automation</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                      <span className="text-gray-300 text-sm">Educational content and assessment</span>
                    </div>
                  </div>
                </div>

                <div className="bg-black/40 p-4 rounded-xl border border-white/10">
                  <div className="flex items-center gap-3 mb-3">
                    <Globe className="w-5 h-5 text-cyan-400" />
                    <h3 className="text-lg font-semibold text-white">The Vision</h3>
                  </div>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    We're building towards a future where AI agents work alongside humans as 
                    creative partners, amplifying human potential and democratizing access to 
                    advanced capabilities across all domains.
                  </p>
                </div>

                <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 p-4 rounded-xl border border-white/20">
                  <div className="flex items-center gap-3 mb-3">
                    <Users className="w-5 h-5 text-pink-400" />
                    <h3 className="text-lg font-semibold text-white">Join the Revolution</h3>
                  </div>
                  <p className="text-gray-300 text-sm leading-relaxed mb-4">
                    Experience the power of agentic AI through our specialized tools. 
                    Each planet in our system represents a different facet of this technology.
                  </p>
                  <button
                    onClick={() => setShowAgentic(false)}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 px-4 rounded-lg font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2"
                  >
                    <span>Explore Our Tools</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Solar System Container */}
      <div className="relative">
        {/* Central Sun - Agentic AI */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-20">
          <div 
            className="relative group cursor-pointer"
            onClick={() => setShowAgentic(true)}
          >
            {/* Enhanced Sun Glow Effects */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 opacity-30 animate-pulse scale-[200%] blur-2xl"></div>
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 opacity-40 animate-pulse scale-150 blur-xl"></div>
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-300 via-blue-400 to-indigo-500 opacity-20 animate-pulse scale-125 blur-lg"></div>
            
            {/* Main Sun Body */}
            <div className="relative w-40 h-40 rounded-full bg-gradient-to-br from-yellow-300 via-orange-400 to-red-500 shadow-2xl flex items-center justify-center border-4 border-white/30 backdrop-blur-sm group-hover:border-white/60 transition-all duration-500 group-hover:scale-110">
              {/* Multiple Inner Glow Layers */}
              <div className="absolute inset-3 rounded-full bg-gradient-to-br from-yellow-200 via-orange-300 to-red-400 opacity-90 animate-pulse"></div>
              <div className="absolute inset-6 rounded-full bg-gradient-to-br from-yellow-100 via-orange-200 to-red-300 opacity-70 animate-pulse" style={{ animationDelay: '0.5s' }}></div>
              
              {/* Central Content */}
              <div className="relative z-10 text-center group-hover:scale-110 transition-transform duration-500">
                <Brain className="w-12 h-12 text-white mx-auto mb-2 animate-pulse drop-shadow-lg" />
                <div className="text-white font-bold text-lg tracking-wider drop-shadow-lg">AGENTIC</div>
                <div className="text-white font-bold text-sm tracking-widest opacity-90 drop-shadow-lg">AI</div>
                <div className="text-white/80 text-xs mt-1 opacity-0 group-hover:opacity-100 transition-opacity duration-500">Click to Learn</div>
              </div>

              {/* Multiple Rotating Energy Rings */}
              <div className="absolute inset-0 rounded-full border-2 border-dashed border-white/40 animate-spin" style={{ animationDuration: '15s' }}></div>
              <div className="absolute inset-2 rounded-full border border-dotted border-yellow-300/50 animate-spin" style={{ animationDuration: '12s', animationDirection: 'reverse' }}></div>
              <div className="absolute inset-4 rounded-full border border-solid border-orange-300/30 animate-spin" style={{ animationDuration: '10s' }}></div>
            </div>

            {/* Enhanced Energy Particles */}
            {[...Array(12)].map((_, i) => (
              <div
                key={i}
                className={`absolute w-2 h-2 ${
                  i % 3 === 0 ? 'bg-yellow-300' : i % 3 === 1 ? 'bg-orange-400' : 'bg-red-400'
                } rounded-full animate-ping`}
                style={{
                  top: '50%',
                  left: '50%',
                  transform: `translate(-50%, -50%) rotate(${i * 30}deg) translateY(-120px)`,
                  animationDelay: `${i * 0.15}s`,
                  animationDuration: '2s'
                }}
              ></div>
            ))}

            {/* Floating Sparkles */}
            {[...Array(8)].map((_, i) => (
              <Sparkles
                key={`sparkle-${i}`}
                className="absolute w-3 h-3 text-yellow-200 animate-pulse opacity-70"
                style={{
                  top: '50%',
                  left: '50%',
                  transform: `translate(-50%, -50%) rotate(${i * 45}deg) translateY(-${90 + (i % 3) * 10}px)`,
                  animationDelay: `${i * 0.3}s`,
                  animationDuration: '3s'
                }}
              />
            ))}
          </div>
        </div>

        {/* Orbit Rings */}
        {planets.map((planet) => (
          <div
            key={`orbit-${planet.id}`}
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/10"
            style={{
              width: `${planet.orbitRadius * 2}px`,
              height: `${planet.orbitRadius * 2}px`
            }}
          ></div>
        ))}

        {/* Planets */}
        {planets.map((planet) => {
          const Icon = planet.icon;
          const startingRotation = planetRotations[planet.id] || 0;
          return (
            <div
              key={planet.id}
              className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 solar-orbit pointer-events-none ${
                !isRotating || hoveredPlanet ? 'paused' : ''
              }`}
              style={{
                width: `${planet.orbitRadius * 2}px`,
                height: `${planet.orbitRadius * 2}px`,
                animationDuration: `${planet.speed}s`,
                transform: `translate(-50%, -50%) rotate(${startingRotation}deg)`,
                transformOrigin: 'center center',
                zIndex: hoveredPlanet === planet.id ? 100 : 10
              }}
            >
              <div
                className={`absolute solar-planet pointer-events-auto ${
                  !isRotating || hoveredPlanet ? 'paused' : ''
                }`}
                style={{
                  top: '-5%',
                  left: '50%',
                  transform: `translate(-50%, -50%) translateY(-${planet.orbitRadius}px)`,
                  animationDuration: `${planet.speed}s`
                }}
                onMouseEnter={() => {
                  setHoveredPlanet(planet.id);
                }}
                onMouseLeave={() => {
                  setHoveredPlanet(null);
                }}
              >
                <div
                  className={`planet-icon relative group cursor-pointer transition-all duration-700 ${
                    hoveredPlanet === planet.id ? 'scale-150 z-50' : 'scale-100 z-10'
                  }`}
                  onClick={() => handleFeatureClick(planet.id)}
                >
                  {/* Enhanced Planet Glow */}
                  <div className={`absolute inset-0 rounded-full opacity-60 blur-xl transition-all duration-500 ${
                    planet.glowColor === 'blue' ? 'bg-blue-500 group-hover:bg-blue-400' :
                    planet.glowColor === 'green' ? 'bg-green-500 group-hover:bg-green-400' :
                    planet.glowColor === 'purple' ? 'bg-purple-500 group-hover:bg-purple-400' :
                    planet.glowColor === 'orange' ? 'bg-orange-500 group-hover:bg-orange-400' :
                    'bg-pink-500 group-hover:bg-pink-400'
                  } group-hover:opacity-90 scale-150 group-hover:scale-200`}></div>

                  {/* Orbit Trail */}
                  <div className={`absolute inset-0 rounded-full border-2 border-dashed opacity-20 animate-spin group-hover:opacity-40 transition-opacity ${
                    planet.glowColor === 'blue' ? 'border-blue-400' :
                    planet.glowColor === 'green' ? 'border-green-400' :
                    planet.glowColor === 'purple' ? 'border-purple-400' :
                    planet.glowColor === 'orange' ? 'border-orange-400' :
                    'border-pink-400'
                  }`} style={{ animationDuration: '8s', scale: '180%' }}></div>

                  {/* Main Planet */}
                  <div 
                    className={`relative rounded-full bg-gradient-to-br ${planet.color} shadow-2xl flex items-center justify-center border-3 border-white/40 backdrop-blur-sm group-hover:border-white/80 transition-all duration-500 group-hover:shadow-2xl`}
                    style={{
                      width: `${planet.size}px`,
                      height: `${planet.size}px`
                    }}
                  >
                    {/* Planet Surface Details */}
                    <div className="absolute inset-1 rounded-full bg-gradient-to-br from-white/10 to-transparent opacity-50"></div>
                    <div className="absolute inset-2 rounded-full bg-gradient-to-tl from-white/20 to-transparent opacity-30"></div>
                    
                    <Icon className="w-7 h-7 text-white group-hover:scale-125 transition-transform duration-500 drop-shadow-lg relative z-10" />
                    
                    {/* Available Badge */}
                    {planet.available && (
                      <div className="absolute -top-2 -right-2 w-5 h-5 bg-green-400 rounded-full animate-pulse border-3 border-white shadow-lg">
                        <div className="absolute inset-0.5 bg-green-300 rounded-full animate-ping"></div>
                      </div>
                    )}

                    {/* Planet Atmosphere */}
                    <div className="absolute inset-0 rounded-full bg-gradient-to-r from-transparent via-white/5 to-transparent animate-pulse opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Expanded Card - Rendered at top level */}
      {hoveredPlanetDetails && (
        <div
          data-planet={hoveredPlanetDetails.id}
          className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 max-h-[90vh] overflow-y-auto bg-black/95 backdrop-blur-xl rounded-2xl p-6 border border-white/30 shadow-2xl z-[200] animate-in slide-in-from-top-4 duration-500"
          onMouseEnter={() => {
            setHoveredPlanet(hoveredPlanetDetails.id);
          }}
          onMouseLeave={() => {
            setHoveredPlanet(null);
          }}
        >
          <div className="text-center mb-4">
            <div
              className={`w-14 h-14 bg-gradient-to-br ${hoveredPlanetDetails.color} rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-2xl border-2 border-white/20`}
            >
              <hoveredPlanetDetails.icon className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">{hoveredPlanetDetails.name}</h3>
            <p className="text-gray-300 text-xs leading-relaxed">{hoveredPlanetDetails.description}</p>
          </div>

          <div className="space-y-2 mb-4">
            {hoveredPlanetDetails.features.map((feature, index) => (
              <div key={index} className="flex items-center gap-2 bg-white/5 p-2 rounded-lg border border-white/10">
                <Sparkles className="w-3 h-3 text-yellow-400 flex-shrink-0" />
                <span className="text-gray-300 text-xs">{feature}</span>
              </div>
            ))}
          </div>

          <button
            className={`w-full py-3 px-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all duration-300 ${
              hoveredPlanetDetails.available
                ? `bg-gradient-to-r ${hoveredPlanetDetails.color} hover:shadow-2xl hover:scale-105 active:scale-95 border border-white/20`
                : 'bg-gray-600 cursor-not-allowed opacity-70 border border-gray-500'
            }`}
            onClick={() => {
              if (hoveredPlanetDetails.available) {
                handleFeatureClick(hoveredPlanetDetails.id);
              }
            }}
          >
            <span className="text-base">{hoveredPlanetDetails.available ? 'Launch Tool' : 'Coming Soon'}</span>
            {hoveredPlanetDetails.available && <ArrowRight className="w-4 h-4" />}
            {!hoveredPlanetDetails.available && <Zap className="w-4 h-4" />}
          </button>

          <div className="text-center mt-3">
            <span
              className={`text-xs px-3 py-1 rounded-full font-medium ${
                hoveredPlanetDetails.available
                  ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                  : 'bg-orange-500/20 text-orange-300 border border-orange-500/30'
              }`}
            >
              {hoveredPlanetDetails.available ? '🚀 Available Now' : '⚡ In Development'}
            </span>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 text-center">
        <div className="bg-black/60 backdrop-blur-lg rounded-xl p-4 border border-white/10">
          <div className="flex items-center gap-2 text-white text-sm mb-2">
            <Orbit className="w-4 h-4 text-blue-400" />
            <span>Hover over any planet to explore</span>
          </div>
          <div className="text-gray-400 text-xs">
            Solar system rotates automatically • Click to launch tools
          </div>
        </div>
      </div>
    </div>
  );
};

export default SolarSystem;
