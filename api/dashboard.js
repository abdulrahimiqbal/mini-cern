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

  // Parse the URL to determine the endpoint
  const { pathname } = new URL(req.url, `http://${req.headers.host}`);
  
  // Handle different endpoints
  if (pathname === '/api/dashboard' || pathname === '/api/dashboard/overview') {
    handleOverview(req, res);
  } else if (pathname === '/api/dashboard/workflows') {
    handleWorkflows(req, res);
  } else if (pathname === '/api/dashboard/workflows/start') {
    handleWorkflowStart(req, res);
  } else if (pathname.match(/\/api\/dashboard\/workflows\/\w+\/stop/)) {
    handleWorkflowStop(req, res);
  } else if (pathname === '/api/dashboard/testing/run-suite') {
    handleTestSuite(req, res);
  } else if (pathname === '/api/dashboard/agents') {
    handleAgents(req, res);
  } else if (pathname === '/api/dashboard/safety') {
    handleSafety(req, res);
  } else {
    handleOverview(req, res); // Default to overview
  }
}

function handleOverview(req, res) {
  // Generate realistic demo data matching the TypeScript interface
  const systemOverview = {
    components: [
      {
        name: "task_scheduler",
        status: "healthy",
        performance: 98.5,
        last_check: new Date().toISOString(),
        details: "Processing tasks efficiently"
      },
      {
        name: "safety_monitor", 
        status: "healthy",
        performance: 99.2,
        last_check: new Date().toISOString(),
        details: "All safety protocols active"
      },
      {
        name: "quality_system",
        status: "healthy", 
        performance: 97.8,
        last_check: new Date().toISOString(),
        details: "Quality checks passing"
      },
      {
        name: "agent_registry",
        status: "healthy",
        performance: 99.1,
        last_check: new Date().toISOString(),
        details: "6 agents registered and active"
      },
      {
        name: "message_bus",
        status: "healthy",
        performance: 98.9,
        last_check: new Date().toISOString(),
        details: "Message routing optimal"
      },
      {
        name: "e2e_testing",
        status: "healthy",
        performance: 96.7,
        last_check: new Date().toISOString(),
        details: "Test suites operational"
      }
    ],
    metrics: {
      cpu_percent: Math.floor(Math.random() * 30) + 20, // 20-50%
      memory_percent: Math.floor(Math.random() * 20) + 70, // 70-90%
      disk_percent: Math.floor(Math.random() * 10) + 5, // 5-15%
      active_agents: 6,
      response_time_ms: Math.floor(Math.random() * 30) + 15 // 15-45ms
    },
    active_workflows: Math.floor(Math.random() * 3) + 1,
    total_tests_run: Math.floor(Math.random() * 50) + 150,
    system_uptime: "2h 45m 12s",
    timestamp: new Date().toISOString()
  };

  res.status(200).json(systemOverview);
}

function handleWorkflows(req, res) {
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const workflows = [
    {
      id: "wf_001",
      title: "Particle Physics Analysis",
      status: "running",
      progress: 67,
      agent: "Theory Agent",
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      domain: "particle_physics",
      priority: "high",
      budget: 50000,
      cost_used: 23400
    },
    {
      id: "wf_002", 
      title: "Quantum Computing Research",
      status: "completed",
      progress: 100,
      agent: "Experimental Agent",
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
      domain: "quantum_physics",
      priority: "medium",
      budget: 75000,
      cost_used: 72100
    }
  ];

  res.status(200).json(workflows);
}

function handleWorkflowStart(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const workflowData = req.body;
    
    // Generate a new workflow ID
    const workflowId = `wf_${Date.now()}`;
    
    // Simulate workflow creation
    const newWorkflow = {
      success: true,
      message: "Workflow started successfully",
      workflow_id: workflowId,
      status: "starting",
      estimated_cost: Math.floor(Math.random() * 10000) + 5000,
      estimated_duration: "2-4 hours"
    };

    res.status(200).json(newWorkflow);
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: 'Failed to start workflow',
      details: error.message 
    });
  }
}

function handleWorkflowStop(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const workflowId = req.url.split('/').slice(-2)[0]; // Extract workflow ID
  
  res.status(200).json({
    success: true,
    message: `Workflow ${workflowId} stopped successfully`,
    workflow_id: workflowId,
    status: "stopped"
  });
}

function handleTestSuite(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const testId = `test_${Date.now()}`;
  
  res.status(200).json({
    success: true,
    test_id: testId,
    message: "Test suite started successfully",
    estimated_duration: "5-10 minutes"
  });
}

function handleAgents(req, res) {
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const agents = {
    success: true,
    agents: [
      { name: "Theory Agent", status: "active", current_project: "Particle Physics Analysis" },
      { name: "Experimental Agent", status: "active", current_project: "Quantum Computing Research" },
      { name: "Analysis Agent", status: "idle", current_project: null },
      { name: "Literature Agent", status: "active", current_project: "Research Review" },
      { name: "Safety Agent", status: "monitoring", current_project: "System Safety" },
      { name: "Meta Agent", status: "coordinating", current_project: "Agent Coordination" }
    ],
    total_agents: 6,
    active_agents: 5
  };

  res.status(200).json(agents);
}

function handleSafety(req, res) {
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const safety = {
    success: true,
    status: "all_clear",
    violations: 0,
    last_check: new Date().toISOString(),
    monitoring_active: true,
    safety_protocols: [
      { name: "Data Privacy", status: "active", compliance: 100 },
      { name: "Resource Limits", status: "active", compliance: 98 },
      { name: "Ethical Guidelines", status: "active", compliance: 100 },
      { name: "Security Protocols", status: "active", compliance: 99 }
    ]
  };

  res.status(200).json(safety);
} 