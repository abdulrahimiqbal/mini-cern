export interface ComponentStatus {
  name: string
  status: 'healthy' | 'warning' | 'error' | 'offline'
  performance: number
  last_check: string
  details?: string
}

export interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  disk_percent: number
  active_agents: number
  response_time_ms: number
}

export interface SystemOverview {
  components: ComponentStatus[]
  metrics: SystemMetrics
  active_workflows: number
  total_tests_run: number
  system_uptime: string
  timestamp: string
}

export interface TestResult {
  test_id: string
  status: 'running' | 'completed' | 'failed'
  progress: number
  results?: {
    total: number
    passed: number
    failed: number
    duration: number
  }
  logs: string[]
  started_at: string
  completed_at?: string
}

export interface WorkflowStatus {
  id: string
  title: string
  status: string
  progress: number
  current_step: string
  created_at: string
  updated_at: string
  estimated_completion: string
  assigned_agents: string[]
  physics_domain: string
  research_question: string
  cost_used: number
  max_cost: number
}

export interface WebSocketEvent {
  type: 'component_status' | 'test_progress' | 'workflow_update' | 'system_metrics'
  data: any
  timestamp: string
}

export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  error?: string
} 