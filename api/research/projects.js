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

  try {
    // Return list of autonomous research projects
    const projects = {
      success: true,
      active_projects: [
        {
          project_id: "rp_1751556789123",
          title: "Research: Quantum Computing Error Correction...",
          research_question: "How can machine learning improve quantum error correction rates?", 
          domain: "quantum_physics",
          status: "executing",
          progress: 45.5,
          current_stage: "hypothesis_generation",
          budget_total: 75000,
          budget_used: 34250,
          tasks_completed: 2,
          total_tasks: 6,
          active_agents: ["theory_agent", "analysis_agent"],
          started_at: "2024-12-30T10:30:00Z",
          estimated_completion: "2025-01-13T10:30:00Z",
          priority: "high"
        },
        {
          project_id: "rp_1751556789124", 
          title: "Research: Dark Matter Detection Methods...",
          research_question: "What novel detection methods could improve dark matter observation sensitivity?",
          domain: "particle_physics",
          status: "planning",
          progress: 0,
          current_stage: "question_analysis",
          budget_total: 100000,
          budget_used: 0,
          tasks_completed: 0,
          total_tasks: 7,
          active_agents: [],
          created_at: "2024-12-30T11:45:00Z",
          priority: "medium"
        }
      ],
      completed_projects: [
        {
          project_id: "rp_1751556789125",
          title: "Research: Neural Network Optimization...",
          research_question: "How can biological neural network structures improve artificial neural network performance?",
          domain: "artificial_intelligence", 
          status: "completed",
          progress: 100,
          budget_total: 50000,
          budget_used: 47850,
          tasks_completed: 6,
          total_tasks: 6,
          completed_at: "2024-12-29T16:20:00Z",
          findings_count: 8,
          final_report_available: true,
          priority: "high"
        }
      ],
      statistics: {
        total_projects: 3,
        active_projects: 2,
        completed_projects: 1,
        total_budget_allocated: 225000,
        total_budget_used: 82100,
        average_completion_time: "2.3 weeks",
        success_rate: 100,
        active_agents: {
          theory_agent: "active - Quantum Computing research",
          experimental_agent: "available", 
          literature_agent: "available",
          analysis_agent: "active - Quantum Computing research",
          safety_agent: "available",
          meta_agent: "available"
        }
      },
      capabilities: {
        autonomous_research: true,
        multi_agent_coordination: true,
        real_time_monitoring: true,
        adaptive_planning: true,
        cost_optimization: true,
        safety_validation: true,
        peer_review: true,
        auto_publication: false // Coming in Phase 6.3
      }
    };

    res.status(200).json(projects);
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: 'Failed to retrieve research projects',
      details: error.message 
    });
  }
} 