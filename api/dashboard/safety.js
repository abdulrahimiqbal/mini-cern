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