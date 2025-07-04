import axios from 'axios'
import type { SystemOverview, WorkflowStatus, ApiResponse } from '../types'

// Use production API if in production, otherwise localhost
const API_BASE = process.env.NODE_ENV === 'production' 
  ? '' // Use relative URLs in production (same domain)
  : 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const apiService = {
  // Health check
  async health(): Promise<ApiResponse> {
    const response = await api.get('/api/health')
    return response.data
  },

  // Dashboard overview
  async getSystemOverview(): Promise<SystemOverview> {
    const response = await api.get('/api/dashboard/overview')
    return response.data
  },

  // Workflows
  async getWorkflows(): Promise<WorkflowStatus[]> {
    const response = await api.get('/api/dashboard/workflows')
    return response.data
  },

  async startWorkflow(workflowData: any): Promise<ApiResponse> {
    const response = await api.post('/api/dashboard/workflows/start', workflowData)
    return response.data
  },

  async stopWorkflow(workflowId: string): Promise<ApiResponse> {
    const response = await api.post(`/api/dashboard/workflows/${workflowId}/stop`)
    return response.data
  },

  // Testing
  async runTestSuite(testSuite?: string): Promise<{ test_id: string }> {
    const response = await api.post('/api/dashboard/testing/run-suite', {
      test_suite: testSuite || 'e2e_demo'
    })
    return response.data
  },

  // Agents
  async getAgents(): Promise<ApiResponse> {
    const response = await api.get('/api/dashboard/agents')
    return response.data
  },

  // Safety
  async getSafetyStatus(): Promise<ApiResponse> {
    const response = await api.get('/api/dashboard/safety')
    return response.data
  },

  // Research (Phase 6)
  async getResearchProjects(): Promise<any> {
    const response = await api.get('/api/research/projects')
    return response.data
  },

  async createResearchProject(projectData: any): Promise<ApiResponse> {
    const response = await api.post('/api/research/create-project', projectData)
    return response.data
  },

  async startResearchProject(projectId: string): Promise<ApiResponse> {
    const response = await api.post('/api/research/start-project', { project_id: projectId })
    return response.data
  },
}

export default apiService 