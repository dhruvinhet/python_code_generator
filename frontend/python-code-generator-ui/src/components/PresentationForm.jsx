import { useState } from 'react'
import { FileText, Loader2, Sparkles, Wand2, Download, RotateCcw } from 'lucide-react'
import { useDarkMode } from '../context/DarkModeContext'

export function PresentationForm({ onSubmit, isLoading, onFormChange, isComplete, onDownload, lastProjectId }) {
  const { isDark } = useDarkMode()
  const [formData, setFormData] = useState({
    topic: '',
    description: '',
    num_slides: 5,
    style: 'professional'
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!formData.topic.trim()) return
    onSubmit(formData)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'num_slides' ? parseInt(value, 10) : value
    }))
    // Call onFormChange to reset preview when form changes
    if (onFormChange) {
      onFormChange()
    }
  }

  return (
    <div className="card group">
      <div className="flex items-center space-x-4 mb-8">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl blur opacity-75 group-hover:opacity-100 transition-opacity"></div>
          <div className="relative p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
            <Wand2 className="h-6 w-6 text-white" />
          </div>
        </div>
        <div>
          <h2 className="text-xl font-bold gradient-text">Create New Presentation</h2>
          <p className="text-gray-600 font-medium">Transform your ideas into stunning presentations with AI magic</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-3">
          <label htmlFor="topic" className="block text-sm font-semibold text-gray-700">
            <span className="flex items-center gap-2">
              {/* <Sparkles className="h-4 w-4 text-purple-500" /> */}
              Presentation Topic *
            </span>
          </label>
          <input
            type="text"
            id="topic"
            name="topic"
            value={formData.topic}
            onChange={handleChange}
            placeholder="e.g., The Future of Artificial Intelligence in Healthcare"
            className="input-field text-gray-800 placeholder-gray-500"
            required
          />
          <p className="text-xs text-gray-500 font-medium pl-6">
            Enter a compelling topic that sparks curiosity
          </p>
        </div>

        {/* <div className="space-y-3">
          <label htmlFor="description" className="block text-sm font-semibold text-gray-700">
            Additional Context (Optional)
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Share any specific aspects, target audience, or key points you'd like to emphasize..."
            rows={4}
            className="input-field resize-none text-gray-800 placeholder-gray-500"
          />
          <p className="text-xs text-gray-500 font-medium">
            🎯 Help our AI understand your vision better
          </p>
        </div> */}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <label htmlFor="num_slides" className="block text-sm font-semibold text-gray-700">
              Number of Slides
            </label>
            <select
              id="num_slides"
              name="num_slides"
              value={formData.num_slides}
              onChange={handleChange}
              className="input-field text-gray-800"
            >
              <option value={3}>3 slides - Quick & Focused</option>
              <option value={5}>5 slides - Balanced Overview</option>
              <option value={7}>7 slides - Detailed Deep-dive</option>
              <option value={10}>10 slides - Comprehensive</option>
            </select>
          </div>

          <div className="space-y-3">
            <label htmlFor="style" className="block text-sm font-semibold text-gray-700">
              Presentation Style
            </label>
            <select
              id="style"
              name="style"
              value={formData.style}
              onChange={handleChange}
              className="input-field text-gray-800"
            >
              <option value="professional">🏢 Professional</option>
              <option value="academic">🎓 Academic</option>
              <option value="creative">🎨 Creative</option>
              <option value="business">💼 Business</option>
            </select>
          </div>
        </div>

        <div className="pt-4">
          {isComplete && lastProjectId ? (
            <div className="space-y-4">
              {/* Download Button */}
              <button
                type="button"
                onClick={() => onDownload && onDownload(lastProjectId)}
                className="btn-primary w-full flex items-center justify-center space-x-3 text-lg font-semibold bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700"
              >
                <Download className="h-5 w-5" />
                <span>Download Presentation</span>
                <Sparkles className="h-5 w-5" />
              </button>
              
              {/* Generate Again Button */}
              <button
                type="submit"
                disabled={isLoading || !formData.topic.trim()}
                className="btn-primary w-full flex items-center justify-center space-x-3 text-lg font-semibold bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700"
              >
                <RotateCcw className="h-5 w-5" />
                <span>Generate New Presentation</span>
                <Sparkles className="h-5 w-5" />
              </button>
            </div>
          ) : (
            <button
              type="submit"
              disabled={isLoading || !formData.topic.trim()}
              className="btn-primary w-full flex items-center justify-center space-x-3 text-lg font-semibold"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Creating Your Presentation...</span>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </>
              ) : (
                <>
                  <Wand2 className="h-5 w-5" />
                  <span>Generate Presentation</span>
                  <Sparkles className="h-5 w-5" />
                </>
              )}
            </button>
          )}
        </div>
      </form>
    </div>
  )
}
