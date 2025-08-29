import { useState } from 'react'
import { FileText, Download, Trash2, RefreshCw, Calendar, Layers } from 'lucide-react'

export function PresentationList({ presentations, onDelete, onDownload, onRefresh }) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async () => {
    setIsRefreshing(true)
    await onRefresh()
    setTimeout(() => setIsRefreshing(false), 500)
  }

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Unknown'
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-green-100 rounded-lg">
            <Layers className="h-5 w-5 text-green-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Your Presentations</h2>
            <p className="text-sm text-gray-600">Manage and download your generated presentations</p>
          </div>
        </div>
        
        <button
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="btn-secondary flex items-center space-x-2"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {presentations.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No presentations yet</h3>
          <p className="text-sm">Create your first presentation using the Generate tab</p>
        </div>
      ) : (
        <div className="space-y-4">
          {presentations.map((presentation) => (
            <div
              key={presentation.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors duration-200"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    <h3 className="font-medium text-gray-900 truncate">
                      {presentation.topic || presentation.title || `Presentation ${presentation.id}`}
                    </h3>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(presentation.created_at || presentation.timestamp)}</span>
                    </div>
                    
                    {presentation.num_slides && (
                      <div className="flex items-center space-x-1">
                        <Layers className="h-4 w-4" />
                        <span>{presentation.num_slides} slides</span>
                      </div>
                    )}
                    
                    {presentation.theme && (
                      <div className="flex items-center space-x-1">
                        <div 
                          className="w-3 h-3 rounded-full border"
                          style={{ backgroundColor: presentation.theme_color || '#3b82f6' }}
                        />
                        <span className="capitalize">{presentation.theme.replace('_', ' ')}</span>
                      </div>
                    )}
                  </div>
                  
                  {presentation.description && (
                    <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                      {presentation.description}
                    </p>
                  )}
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => onDownload(presentation.id)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                    title="Download PDF"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                  
                  <button
                    onClick={() => onDelete(presentation.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
                    title="Delete presentation"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
