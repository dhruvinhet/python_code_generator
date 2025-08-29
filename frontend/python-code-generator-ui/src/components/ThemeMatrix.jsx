import { useState } from 'react'
import { Palette, Check, RotateCcw } from 'lucide-react'

export function ThemeMatrix({ themes = [], selectedTheme, onThemeChange, showPreview = false, previewData = null, onNewPresentation }) {
  if (showPreview && previewData) {
    return (
      <div className="card">
        <div className="flex items-center space-x-4 mb-6">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-green-500 to-blue-600 rounded-xl blur opacity-75"></div>
            <div className="relative p-3 bg-gradient-to-r from-green-500 to-blue-600 rounded-xl">
              <Check className="h-6 w-6 text-white" />
            </div>
          </div>
          <div>
            <h2 className="text-xl font-bold gradient-text">Presentation Preview</h2>
            <p className="text-gray-600 font-medium">Your presentation is ready!</p>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
            <h3 className="font-bold text-gray-800 mb-2">{previewData.topic}</h3>
            <p className="text-sm text-gray-600 mb-4">{previewData.description}</p>
            <div className="flex items-center justify-between text-sm text-gray-500">
              <span>{previewData.num_slides} slides</span>
              <span className="capitalize">{previewData.style} style</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                {themes.find(t => t.id === selectedTheme)?.name || selectedTheme}
              </span>
            </div>
          </div>
          
          {onNewPresentation && (
            <button
              onClick={onNewPresentation}
              className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl hover:from-purple-600 hover:to-pink-700 transition-all duration-200 font-medium"
            >
              <RotateCcw className="h-4 w-4" />
              <span>Create New Presentation</span>
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-4 mb-8">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl blur opacity-75"></div>
          <div className="relative p-3 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl">
            <Palette className="h-6 w-6 text-white" />
          </div>
        </div>
        <div>
          <h2 className="text-xl font-bold gradient-text">Choose Your Theme</h2>
          <p className="text-gray-600 font-medium">Select a stunning visual style for your presentation</p>
        </div>
      </div>

      {themes.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {themes.map((theme) => (
            <div
              key={theme.id}
              onClick={() => onThemeChange(theme.id)}
              className={`relative group cursor-pointer transition-all duration-300 hover:scale-105 ${
                selectedTheme === theme.id ? 'ring-2 ring-blue-500 ring-offset-2' : ''
              }`}
            >
              <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-200 hover:shadow-xl transition-shadow h-40 flex flex-col justify-between">
                {/* Theme Name */}
                <div className="text-center mb-4">
                  <h3 className="font-bold text-gray-800 text-sm truncate">{theme.name}</h3>
                </div>
                
                {/* Color Dots - 3 dots showing theme colors */}
                <div className="flex justify-center space-x-3 mb-4">
                  <div 
                    className="w-5 h-5 rounded-full border border-gray-200 shadow-sm"
                    style={{ backgroundColor: theme.colors?.primary || '#667eea' }}
                  />
                  <div 
                    className="w-5 h-5 rounded-full border border-gray-200 shadow-sm"
                    style={{ backgroundColor: theme.colors?.secondary || '#764ba2' }}
                  />
                  <div 
                    className="w-5 h-5 rounded-full border border-gray-200 shadow-sm"
                    style={{ backgroundColor: theme.colors?.accent || '#ffc107' }}
                  />
                </div>

                {/* Theme Description */}
                <div className="flex-1 flex items-center justify-center">
                  <p className="text-xs text-gray-500 text-center leading-relaxed overflow-hidden" 
                     style={{
                       display: '-webkit-box',
                       WebkitLineClamp: 3,
                       WebkitBoxOrient: 'vertical',
                       textOverflow: 'ellipsis'
                     }}>
                    {theme.description}
                  </p>
                </div>
                
                {/* Selected Indicator */}
                {selectedTheme === theme.id && (
                  <div className="absolute -top-2 -right-2">
                    <div className="p-1.5 bg-gradient-to-r from-green-400 to-blue-500 rounded-full shadow-lg">
                      <Check className="h-3 w-3 text-white" />
                    </div>
                  </div>
                )}
                
                {/* Hover Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full blur opacity-20"></div>
            <Palette className="relative h-16 w-16 mx-auto mb-4 text-purple-500" />
          </div>
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Loading Themes...</h3>
          <p className="text-sm text-gray-500">Preparing beautiful themes for your presentation</p>
          <div className="flex justify-center space-x-1 mt-4">
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
          </div>
        </div>
      )}
    </div>
  )
}
