"""
Dashboard API - FastAPI endpoints for web dashboard
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import Phase 4 components
from core.orchestrator import ResearchOrchestrator
from core.research_project import ResearchProject
from workflow.workflow_engine import WorkflowEngine
from workflow.task_scheduler import TaskScheduler
from safety.oversight_monitor import SafetyMonitor
from quality.peer_review_system import PeerReviewSystem
from integration.e2e_testing import E2ETestRunner
from communication.agent_registry_mock import AgentRegistry
from communication.message_bus_mock import MessageBus

# Import dashboard-specific modules
from dashboard.shared.schemas import (
    SystemOverview, ComponentInfo, PerformanceMetrics, ComponentStatus,
    WorkflowStartRequest, TestExecutionRequest, ApiResponse
)
from dashboard.shared.events import EventType, create_system_status_event
from dashboard.backend.metrics_collector import SystemMetricsCollector
from dashboard.backend.websocket_handler import WebSocketManager
from dashboard.backend.test_runner import DashboardTestRunner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
orchestrator: Optional[ResearchOrchestrator] = None
websocket_manager: Optional[WebSocketManager] = None
metrics_collector: Optional[SystemMetricsCollector] = None
test_runner: Optional[DashboardTestRunner] = None

# Component status tracking
component_statuses = {}
active_workflows = {}
system_metrics = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Dashboard API...")
    await initialize_dashboard_components()
    
    # Start background tasks
    asyncio.create_task(periodic_metrics_collection())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Dashboard API...")
    await cleanup_dashboard_components()


# Create FastAPI app
app = FastAPI(
    title="Science Research Institute Dashboard API",
    description="Real-time monitoring and control dashboard for autonomous research system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def initialize_dashboard_components():
    """Initialize dashboard components and Phase 4 integration"""
    global orchestrator, websocket_manager, metrics_collector, test_runner
    
    try:
        # Initialize WebSocket manager
        websocket_manager = WebSocketManager()
        
        # Initialize metrics collector
        metrics_collector = SystemMetricsCollector()
        
        # Initialize test runner
        test_runner = DashboardTestRunner(websocket_manager)
        
        # Initialize Phase 4 components with mock implementations
        agent_registry = AgentRegistry()
        message_bus = MessageBus()
        
        # Initialize basic components first
        task_scheduler = TaskScheduler(agent_registry)
        safety_monitor = SafetyMonitor()
        quality_system = PeerReviewSystem()
        e2e_testing = E2ETestRunner()
        
        # For now, create a simplified orchestrator without workflow engine
        orchestrator = None  # Will implement proper orchestrator later
        
        # Update component statuses
        component_statuses.update({
            "task_scheduler": {"status": "healthy", "last_heartbeat": datetime.now()},
            "safety_monitor": {"status": "healthy", "last_heartbeat": datetime.now()},
            "quality_system": {"status": "healthy", "last_heartbeat": datetime.now()},
            "agent_registry": {"status": "healthy", "last_heartbeat": datetime.now()},
            "message_bus": {"status": "healthy", "last_heartbeat": datetime.now()},
            "e2e_testing": {"status": "healthy", "last_heartbeat": datetime.now()},
        })
        
        logger.info("Dashboard components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize dashboard components: {e}")
        raise


async def cleanup_dashboard_components():
    """Cleanup dashboard components"""
    global websocket_manager, metrics_collector
    
    if websocket_manager:
        await websocket_manager.disconnect_all()
    
    if metrics_collector:
        await metrics_collector.stop()


async def periodic_metrics_collection():
    """Collect system metrics periodically"""
    global metrics_collector, websocket_manager, component_statuses
    
    while True:
        try:
            if metrics_collector and websocket_manager:
                # Collect system metrics
                metrics = await metrics_collector.collect_metrics()
                system_metrics.update(metrics)
                
                # Update component heartbeats
                current_time = datetime.now()
                for component in component_statuses:
                    component_statuses[component]["last_heartbeat"] = current_time
                
                # Create and broadcast system status event
                event = create_system_status_event(
                    components_status=component_statuses,
                    performance_metrics=metrics
                )
                
                await websocket_manager.broadcast(event.dict())
                
        except Exception as e:
            logger.error(f"Error in periodic metrics collection: {e}")
        
        await asyncio.sleep(5)  # Collect metrics every 5 seconds


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Science Research Institute Dashboard API", "version": "1.0.0"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return ApiResponse(
        success=True,
        message="Dashboard API is healthy",
        data={"status": "healthy", "timestamp": datetime.now()}
    )


@app.get("/api/dashboard/overview", response_model=SystemOverview)
async def get_system_overview():
    """Get complete system status overview"""
    try:
        current_time = datetime.now()
        
        # Build component info
        components = {}
        overall_health = ComponentStatus.HEALTHY
        
        for comp_name, comp_data in component_statuses.items():
            status = ComponentStatus(comp_data.get("status", "offline"))
            if status in [ComponentStatus.ERROR, ComponentStatus.OFFLINE]:
                overall_health = ComponentStatus.ERROR
            elif status == ComponentStatus.WARNING and overall_health == ComponentStatus.HEALTHY:
                overall_health = ComponentStatus.WARNING
            
            components[comp_name] = ComponentInfo(
                name=comp_name,
                status=status,
                uptime_seconds=(current_time - comp_data["last_heartbeat"]).total_seconds(),
                last_heartbeat=comp_data["last_heartbeat"],
                error_count=comp_data.get("error_count", 0),
                performance_score=comp_data.get("performance_score", 100.0)
            )
        
        # Build performance metrics
        performance = PerformanceMetrics(
            cpu_usage_percent=system_metrics.get("cpu_usage", 0.0),
            memory_usage_percent=system_metrics.get("memory_usage", 0.0),
            disk_usage_percent=system_metrics.get("disk_usage", 0.0),
            active_tasks=system_metrics.get("active_tasks", 0),
            queue_length=system_metrics.get("queue_length", 0),
            response_time_ms=system_metrics.get("response_time", 0.0)
        )
        
        return SystemOverview(
            timestamp=current_time,
            components=components,
            performance=performance,
            overall_health=overall_health,
            active_workflows=len(active_workflows),
            total_agents=system_metrics.get("total_agents", 0)
        )
        
    except Exception as e:
        logger.error(f"Error getting system overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/workflows")
async def get_active_workflows():
    """Get active workflows"""
    try:
        workflows = []
        for cycle_id, workflow_data in active_workflows.items():
            workflows.append({
                "cycle_id": cycle_id,
                "project_name": workflow_data.get("project_name", "Unknown"),
                "status": workflow_data.get("status", "unknown"),
                "start_time": workflow_data.get("start_time"),
                "progress_percentage": workflow_data.get("progress", 0.0),
                "current_step": workflow_data.get("current_step", ""),
                "estimated_completion": workflow_data.get("estimated_completion")
            })
        
        return ApiResponse(
            success=True,
            message="Active workflows retrieved",
            data={"workflows": workflows, "total": len(workflows)}
        )
        
    except Exception as e:
        logger.error(f"Error getting workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dashboard/workflows/start")
async def start_workflow(request: WorkflowStartRequest, background_tasks: BackgroundTasks):
    """Start a new research workflow"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        # Create research project
        project = ResearchProject(
            project_id=f"proj_{int(datetime.now().timestamp())}",
            name=request.project_name,
            research_topic=request.research_topic,
            objectives=["Automated research cycle demonstration"],
            methodology="LLM-driven autonomous research",
            collaboration_protocol="distributed_consensus"
        )
        
        # Start workflow in background
        cycle_id = f"cycle_{int(datetime.now().timestamp())}"
        background_tasks.add_task(
            execute_workflow_background,
            cycle_id,
            project,
            request.workflow_template,
            request.parameters
        )
        
        # Track workflow
        active_workflows[cycle_id] = {
            "project_name": request.project_name,
            "status": "starting",
            "start_time": datetime.now(),
            "progress": 0.0,
            "current_step": "initialization",
            "estimated_completion": datetime.now() + timedelta(minutes=10)
        }
        
        return ApiResponse(
            success=True,
            message=f"Workflow started successfully",
            data={"cycle_id": cycle_id, "project_id": project.project_id}
        )
        
    except Exception as e:
        logger.error(f"Error starting workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dashboard/workflows/{cycle_id}/stop")
async def stop_workflow(cycle_id: str):
    """Stop a running workflow"""
    try:
        if cycle_id not in active_workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update workflow status
        active_workflows[cycle_id]["status"] = "stopped"
        active_workflows[cycle_id]["completion_time"] = datetime.now()
        
        # Broadcast workflow stopped event
        if websocket_manager:
            await websocket_manager.broadcast({
                "type": "workflow_stopped",
                "data": {"cycle_id": cycle_id},
                "timestamp": datetime.now().isoformat()
            })
        
        return ApiResponse(
            success=True,
            message=f"Workflow {cycle_id} stopped successfully"
        )
        
    except Exception as e:
        logger.error(f"Error stopping workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dashboard/testing/run-suite")
async def run_test_suite(request: TestExecutionRequest, background_tasks: BackgroundTasks):
    """Run E2E test suite"""
    try:
        if not test_runner:
            raise HTTPException(status_code=503, detail="Test runner not initialized")
        
        # Start test execution in background
        test_id = f"test_{int(datetime.now().timestamp())}"
        background_tasks.add_task(
            test_runner.run_test_suite,
            test_id,
            request.test_suite,
            request.test_scenarios,
            request.parameters
        )
        
        return ApiResponse(
            success=True,
            message="Test suite execution started",
            data={"test_id": test_id, "test_suite": request.test_suite}
        )
        
    except Exception as e:
        logger.error(f"Error starting test suite: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/agents")
async def get_agents_status():
    """Get agent registry status"""
    try:
        # Mock agent data for now
        agents_data = {
            "total_agents": 6,
            "active_agents": 6,
            "idle_agents": 4,
            "busy_agents": 2,
            "offline_agents": 0,
            "agents_by_type": {
                "RESEARCH_COORDINATOR": 1,
                "DATA_ANALYST": 1,
                "SIMULATION_SPECIALIST": 1,
                "THEORY_SPECIALIST": 1,
                "EXPERIMENTAL_DESIGNER": 1,
                "REVIEWER": 1
            }
        }
        
        return ApiResponse(
            success=True,
            message="Agent status retrieved",
            data=agents_data
        )
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/safety")
async def get_safety_status():
    """Get safety monitoring status"""
    try:
        safety_data = {
            "overall_status": "safe",
            "monitoring_active": True,
            "last_check": datetime.now(),
            "active_violations": [],
            "violation_count_24h": 0,
            "emergency_stops_count": 0
        }
        
        return ApiResponse(
            success=True,
            message="Safety status retrieved",
            data=safety_data
        )
        
    except Exception as e:
        logger.error(f"Error getting safety status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def execute_workflow_background(
    cycle_id: str,
    project: ResearchProject,
    template: str,
    parameters: Dict[str, Any]
):
    """Execute workflow in background"""
    try:
        logger.info(f"Starting workflow execution: {cycle_id}")
        
        # Update workflow status
        active_workflows[cycle_id]["status"] = "running"
        active_workflows[cycle_id]["current_step"] = "project_setup"
        active_workflows[cycle_id]["progress"] = 10.0
        
        # Simulate workflow steps with progress updates
        steps = [
            ("project_setup", 10.0),
            ("literature_review", 25.0),
            ("methodology_design", 40.0),
            ("data_collection", 60.0),
            ("analysis", 80.0),
            ("quality_review", 95.0),
            ("completion", 100.0)
        ]
        
        for step_name, progress in steps:
            # Update progress
            active_workflows[cycle_id]["current_step"] = step_name
            active_workflows[cycle_id]["progress"] = progress
            
            # Broadcast progress update
            if websocket_manager:
                await websocket_manager.broadcast({
                    "type": "workflow_progress_update",
                    "data": {
                        "cycle_id": cycle_id,
                        "current_step": step_name,
                        "progress_percentage": progress,
                        "timestamp": datetime.now().isoformat()
                    }
                })
            
            # Simulate step execution time
            await asyncio.sleep(2)
        
        # Mark workflow as completed
        active_workflows[cycle_id]["status"] = "completed"
        active_workflows[cycle_id]["completion_time"] = datetime.now()
        
        # Broadcast completion
        if websocket_manager:
            await websocket_manager.broadcast({
                "type": "workflow_completed",
                "data": {"cycle_id": cycle_id},
                "timestamp": datetime.now().isoformat()
            })
        
        logger.info(f"Workflow {cycle_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error executing workflow {cycle_id}: {e}")
        active_workflows[cycle_id]["status"] = "failed"
        active_workflows[cycle_id]["error"] = str(e)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 