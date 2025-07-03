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

  // Mock dashboard data for demo
  const dashboardData = {
    success: true,
    system_health: {
      status: "healthy",
      uptime: "2h 45m",
      last_check: new Date().toISOString()
    },
    components: {
      task_scheduler: { status: "healthy", performance: 98.5 },
      safety_monitor: { status: "healthy", performance: 99.2 },
      quality_system: { status: "healthy", performance: 97.8 },
      agent_registry: { status: "healthy", performance: 99.1 },
      message_bus: { status: "healthy", performance: 98.9 },
      e2e_testing: { status: "healthy", performance: 96.7 }
    },
    metrics: {
      cpu_usage: Math.floor(Math.random() * 30) + 20, // 20-50%
      memory_usage: Math.floor(Math.random() * 20) + 70, // 70-90%
      disk_usage: Math.floor(Math.random() * 10) + 5, // 5-15%
      response_time: Math.floor(Math.random() * 30) + 15 // 15-45ms
    },
    agents: {
      active_count: 6,
      available_types: [
        "Theory Agent",
        "Experimental Agent", 
        "Analysis Agent",
        "Literature Agent",
        "Safety Agent",
        "Meta-Research Agent"
      ]
    },
    workflows: {
      active: Math.floor(Math.random() * 3) + 1,
      completed_today: Math.floor(Math.random() * 8) + 2,
      success_rate: 94.2
    }
  };

  res.status(200).json(dashboardData);
} 