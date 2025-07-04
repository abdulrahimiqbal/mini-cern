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