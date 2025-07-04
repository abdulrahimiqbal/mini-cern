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

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const { research_question, domain, budget = 50000, priority = "medium" } = req.body;
    
    if (!research_question || !domain) {
      res.status(400).json({ 
        error: 'Missing required fields',
        required: ['research_question', 'domain']
      });
      return;
    }

    // Generate a new project ID
    const projectId = `rp_${Date.now()}`;
    
    // Create autonomous research project
    const project = {
      success: true,
      message: "Autonomous research project created successfully",
      project_id: projectId,
      title: `Research: ${research_question.substring(0, 50)}...`,
      research_question: research_question,
      domain: domain,
      status: "planning",
      priority: priority,
      budget_total: budget,
      budget_used: 0,
      tasks_created: 6,
      estimated_duration: "2-4 weeks",
      created_at: new Date().toISOString(),
      tasks: [
        {
          title: "Research Question Analysis",
          status: "pending",
          assigned_agent: "theory_agent",
          estimated_cost: 200,
          stage: "question_analysis"
        },
        {
          title: "Literature Review", 
          status: "pending",
          assigned_agent: "literature_agent",
          estimated_cost: 800,
          stage: "literature_review"
        },
        {
          title: "Hypothesis Generation",
          status: "pending", 
          assigned_agent: "theory_agent",
          estimated_cost: 400,
          stage: "hypothesis_generation"
        },
        {
          title: "Experimental Design",
          status: "pending",
          assigned_agent: "experimental_agent", 
          estimated_cost: 600,
          stage: "experimental_design"
        },
        {
          title: "Data Analysis",
          status: "pending",
          assigned_agent: "analysis_agent",
          estimated_cost: 700,
          stage: "data_analysis"
        },
        {
          title: "Report Generation",
          status: "pending",
          assigned_agent: "meta_agent",
          estimated_cost: 500,
          stage: "report_generation"
        }
      ],
      agent_assignments: {
        theory_agent: ["Research Question Analysis", "Hypothesis Generation"],
        literature_agent: ["Literature Review"],
        experimental_agent: ["Experimental Design"],
        analysis_agent: ["Data Analysis"],
        meta_agent: ["Report Generation"]
      }
    };

    res.status(200).json(project);
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: 'Failed to create research project',
      details: error.message 
    });
  }
} 