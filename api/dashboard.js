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