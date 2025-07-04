export default function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight OPTIONS requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Check the specific endpoint
  const { url } = req;
  
  if (url.includes('/api/dashboard/agents')) {
    // Mock agents data
    const agentsData = {
      success: true,
      message: "Agents are operational",
      data: {
        total_agents: 6,
        active_agents: 6,
        agent_types: [
          { name: "Theory Agent", status: "active", performance: 98.5 },
          { name: "Experimental Agent", status: "active", performance: 97.2 },
          { name: "Analysis Agent", status: "active", performance: 99.1 },
          { name: "Literature Agent", status: "active", performance: 96.8 },
          { name: "Safety Agent", status: "active", performance: 99.9 },
          { name: "Meta-Research Agent", status: "active", performance: 98.3 }
        ]
      }
    };
    return res.status(200).json(agentsData);
  }
  
  if (url.includes('/api/dashboard/safety')) {
    // Mock safety data
    const safetyData = {
      success: true,
      message: "All safety protocols active",
      data: {
        overall_status: "secure",
        protocols_active: 12,
        security_level: "high",
        last_audit: new Date().toISOString(),
        alerts: [],
        monitoring: {
          data_integrity: "verified",
          access_control: "active",
          anomaly_detection: "running"
        }
      }
    };
    return res.status(200).json(safetyData);
  }

  if (url.includes('/api/dashboard/testing/run-suite')) {
    // Only allow POST for test runs
    if (req.method !== 'POST') {
      return res.status(405).json({ 
        success: false, 
        error: 'Method not allowed. Use POST.' 
      });
    }
    
    // Mock test run
    const testData = {
      success: true,
      test_id: `test_${Date.now()}`,
      message: "Test suite started",
      status: "running"
    };
    return res.status(200).json(testData);
  }

  if (url.includes('/api/dashboard/workflows')) {
    // Mock workflows data matching the frontend interface
    const workflowsData = [
      {
        id: "wf_mock_001",
        title: "Quantum Entanglement Simulation (Mock)",
        status: "executing",
        progress: 75.2,
        current_step: "Running quantum state simulation",
        created_at: new Date(Date.now() - 3600000).toISOString(),
        updated_at: new Date().toISOString(),
        estimated_completion: new Date(Date.now() + 3600000).toISOString(),
        assigned_agents: ["theory_agent", "analysis_agent"],
        physics_domain: "quantum",
        research_question: "How does decoherence affect multi-particle entanglement?",
        cost_used: 157.45,
        max_cost: 500.0
      },
      {
        id: "wf_mock_002", 
        title: "Particle Collision Analysis (Mock)",
        status: "completed",
        progress: 100,
        current_step: "Results published",
        created_at: new Date(Date.now() - 7200000).toISOString(),
        updated_at: new Date(Date.now() - 300000).toISOString(),
        estimated_completion: new Date(Date.now() - 300000).toISOString(),
        assigned_agents: ["experimental_agent", "analysis_agent"],
        physics_domain: "particle_physics",
        research_question: "What novel particles are produced in high-energy collisions?",
        cost_used: 890.12,
        max_cost: 1000.0
      }
    ];
    return res.status(200).json(workflowsData);
  }

  // Default health check
  const healthData = {
    success: true,
    message: "Dashboard API is healthy",
    timestamp: new Date().toISOString(),
    version: "1.0.0"
  };

  res.status(200).json(healthData);
} 