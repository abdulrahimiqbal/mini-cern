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