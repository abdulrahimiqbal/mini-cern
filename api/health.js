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

  // Health check response
  res.status(200).json({
    success: true,
    message: "Mini CERN API is healthy",
    timestamp: new Date().toISOString(),
    status: "operational",
    version: "1.0.0",
    github: "https://github.com/abdulrahimiqbal/mini-cern"
  });
} 