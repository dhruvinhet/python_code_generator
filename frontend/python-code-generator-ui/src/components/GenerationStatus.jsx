import { useState, useEffect } from 'react'
import { CheckCircle, Clock, AlertCircle, Loader2, Zap, Sparkles, Download, X } from 'lucide-react'
import { api } from '../services/api'

export function GenerationStatus({ projectId, onComplete, onDownload }) {
  const [status, setStatus] = useState('generating')
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('Initializing AI systems...')
  const [isDownloading, setIsDownloading] = useState(false)

  const handleDownload = async () => {
    if (!projectId || isDownloading) return
    
    setIsDownloading(true)
    try {
      const response = await api.downloadPDF(projectId)
      
      // Create blob and download
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `presentation_${projectId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      if (onDownload) {
        onDownload(projectId)
      }
    } catch (error) {
      console.error('Failed to download PDF:', error)
      alert('Failed to download PDF. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  useEffect(() => {
    if (!projectId) return

    const checkStatus = async () => {
      try {
        const response = await api.getProjectStatus(projectId)
        const data = response.data
        
        if (data.status === 'completed') {
          setStatus('completed')
          setProgress(100)
          setCurrentStep('✨ Your presentation is ready!')
          setTimeout(() => onComplete(projectId), 10000) // Changed from 2000 to 10000 (10 seconds)
        } else if (data.status === 'error') {
          setStatus('error')
          setCurrentStep('❌ Something went wrong during generation')
        } else {
          setStatus('generating')
          // Simulate progress for better UX
          setProgress(prev => Math.min(prev + 5, 90))
          
          // Set current step based on status
          if (data.current_step) {
            setCurrentStep(data.current_step)
          } else {
            const steps = [
              '🔍 Researching your topic across the web...',
              '🧠 AI is analyzing and organizing information...',
              '✍️ Crafting compelling content for each slide...',
              '🎨 Designing beautiful visual layouts...',
              '⚡ Generating your final presentation...'
            ]
            const stepIndex = Math.floor(progress / 20)
            setCurrentStep(steps[stepIndex] || '🚀 Working on something amazing...')
          }
        }
      } catch (error) {
        console.error('Error checking status:', error)
        setStatus('error')
        setCurrentStep('🔌 Connection lost - please check your internet')
      }
    }

    const interval = setInterval(checkStatus, 2000)
    checkStatus() // Initial check

    return () => clearInterval(interval)
  }, [projectId, progress, onComplete])

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-8 w-8 text-green-500" />
      case 'error':
        return <AlertCircle className="h-8 w-8 text-red-500" />
      default:
        return <Loader2 className="h-8 w-8 text-purple-600 animate-spin" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'status-card border-green-200 bg-gradient-to-r from-green-50 to-emerald-50'
      case 'error':
        return 'status-card border-red-200 bg-gradient-to-r from-red-50 to-pink-50'
      default:
        return 'status-card border-purple-200 bg-gradient-to-r from-purple-50 to-indigo-50'
    }
  }

  return (
    <div className={`${getStatusColor()} rounded-2xl p-6 border-2`}>
      <div className="flex items-center space-x-6">
        <div className="relative">
          {getStatusIcon()}
          {status === 'generating' && (
            <div className="absolute -inset-2 rounded-full border-2 border-purple-200 animate-ping"></div>
          )}
        </div>
        
        <div className="flex-1">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xl font-bold text-gray-800">
              {status === 'completed' ? '🎊 Generation Complete!' : 
               status === 'error' ? '😔 Generation Failed' : 
               '🎯 Creating Your Presentation...'}
            </h3>
            {status === 'generating' && (
              <div className="flex items-center space-x-2">
                <Zap className="h-5 w-5 text-yellow-500 animate-pulse" />
                <span className="text-lg font-bold text-purple-600">{progress}%</span>
              </div>
            )}
          </div>
          
          <p className="text-gray-700 font-medium mb-4 text-lg">{currentStep}</p>
          
          {status === 'generating' && (
            <div className="relative">
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div 
                  className="progress-bar h-3 transition-all duration-500 relative"
                  style={{ width: `${progress}%` }}
                >
                  <div className="absolute inset-0 bg-white/30 animate-pulse"></div>
                </div>
              </div>
              <div className="flex justify-between mt-2 text-sm text-gray-600">
                <span>Processing...</span>
                <span>Almost there!</span>
              </div>
            </div>
          )}
          
          {status === 'completed' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-green-600 font-semibold">
                  <Sparkles className="h-5 w-5 animate-pulse" />
                  <p>Your presentation is ready!</p>
                </div>
                <button
                  onClick={() => onComplete(projectId)}
                  className="text-gray-400 hover:text-gray-600 p-1"
                  title="Dismiss this notification"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleDownload}
                  disabled={isDownloading}
                  className="btn-primary flex items-center space-x-2 bg-green-600 hover:bg-green-700 disabled:opacity-50"
                >
                  <Download className={`h-4 w-4 ${isDownloading ? 'animate-spin' : ''}`} />
                  <span>{isDownloading ? 'Downloading...' : 'Download PDF'}</span>
                </button>
                
                <p className="text-gray-600 text-sm">
                  You can also find it in the Manage tab
                </p>
              </div>
            </div>
          )}
          
          {status === 'error' && (
            <div className="bg-red-100 border border-red-200 rounded-lg p-4">
              <p className="text-red-700 font-medium">
                Don't worry! Please try again in a moment. Our AI sometimes needs a coffee break ☕
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
