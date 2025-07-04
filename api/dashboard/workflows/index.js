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
      status: "executing",
      progress: 67.5,
      current_step: "Data analysis and pattern recognition",
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      updated_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 minutes ago
      estimated_completion: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), // 4 hours from now
      assigned_agents: ["Theory Agent", "Analysis Agent", "Literature Agent"],
      physics_domain: "particle_physics",
      research_question: "What are the implications of recent particle collision data for the Standard Model?",
      cost_used: 23400,
      max_cost: 50000
    },
    {
      id: "wf_002", 
      title: "Quantum Computing Research",
      status: "completed",
      progress: 100,
      current_step: "Final report generation",
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
      updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      estimated_completion: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // completed 2 hours ago
      assigned_agents: ["Experimental Agent", "Meta Agent"],
      physics_domain: "quantum_physics",
      research_question: "How can quantum error correction be improved for near-term quantum computers?",
      cost_used: 72100,
      max_cost: 75000
    },
    {
      id: "wf_003",
      title: "Gravitational Wave Detection Optimization",
      status: "planning",
      progress: 12.3,
      current_step: "Literature review and hypothesis formation",
      created_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(), // 45 minutes ago
      updated_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(), // 15 minutes ago
      estimated_completion: new Date(Date.now() + 18 * 60 * 60 * 1000).toISOString(), // 18 hours from now
      assigned_agents: ["Theory Agent", "Safety Agent"],
      physics_domain: "astrophysics",
      research_question: "Can machine learning improve sensitivity of gravitational wave detectors?",
      cost_used: 1250,
      max_cost: 35000
    }
  ];

  res.status(200).json(workflows);
} 