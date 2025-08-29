import axios from 'axios'

const BASE_URL = 'http://localhost:5000'

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // Generate presentation
  generatePresentation: (data) => apiClient.post('/api/ppt/presentations', data),
  
  // Get themes
  getThemes: () => apiClient.get('/api/ppt/themes'),
  
  // Get projects
  getProjects: () => apiClient.get('/api/ppt/projects'),
  
  // Get project status
  getProjectStatus: (projectId) => apiClient.get(`/api/ppt/projects/${projectId}/status`),
  
  // Delete project
  deleteProject: (projectId) => apiClient.delete(`/api/ppt/projects/${projectId}`),
  
  // Download PDF
  downloadPDF: (projectId) => apiClient.get(`/api/ppt/presentations/${projectId}/download/pdf`, {
    responseType: 'blob'
  }),
  
  // Get API status
  getStatus: () => apiClient.get('/'),
}
