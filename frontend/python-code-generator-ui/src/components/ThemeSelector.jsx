import { Palette, Check, Crown, Star } from 'lucide-react'

export function ThemeSelector({ themes, selectedTheme, onThemeChange }) {
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

      <div className="space-y-4">
        {themes.map((theme) => (
          <div
            key={theme.name}
            onClick={() => onThemeChange(theme.name)}
            className={`theme-card p-5 rounded-2xl border-2 cursor-pointer ${
              selectedTheme === theme.name
                ? 'selected'
                : 'border-white/30 hover:border-white/50'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <div
                      className="w-8 h-8 rounded-xl border-2 border-white shadow-lg"
                      style={{ 
                        background: `linear-gradient(135deg, ${theme.primary_color || '#667eea'} 0%, ${theme.secondary_color || '#764ba2'} 100%)` 
                      }}
                    />
                    {selectedTheme === theme.name && (
                      <div className="absolute -top-1 -right-1">
                        <Crown className="h-4 w-4 text-yellow-500" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="font-bold text-gray-800">{theme.display_name}</h3>
                      {theme.name === 'corporate_blue' && (
                        <Star className="h-4 w-4 text-yellow-500" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 font-medium">{theme.description}</p>
                  </div>
                </div>
              </div>
              {selectedTheme === theme.name && (
                <div className="ml-4">
                  <div className="p-2 bg-gradient-to-r from-green-400 to-blue-500 rounded-full">
                    <Check className="h-4 w-4 text-white" />
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {themes.length === 0 && (
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
