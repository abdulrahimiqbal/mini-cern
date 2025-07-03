"""
Safety Oversight Monitor - Real-time Safety Management
Provides continuous safety monitoring and emergency protocols for autonomous research
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4
import json

from core.research_project import ResearchProject, ResearchState
from workflow.workflow_engine import AutomatedResearchCycle, WorkflowState
from agents.agent_types import AgentType, AgentCapability

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk levels for safety assessment"""
    MINIMAL = "minimal"      # 0-20% risk
    LOW = "low"             # 21-40% risk
    MODERATE = "moderate"   # 41-60% risk
    HIGH = "high"          # 61-80% risk
    CRITICAL = "critical"   # 81-100% risk

class SafetyStatus(Enum):
    """Overall safety status"""
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class ViolationType(Enum):
    """Types of safety violations"""
    RESOURCE_LIMIT = "resource_limit"
    TIME_LIMIT = "time_limit"
    AGENT_MALFUNCTION = "agent_malfunction"
    DATA_CORRUPTION = "data_corruption"
    PROTOCOL_VIOLATION = "protocol_violation"
    ETHICAL_VIOLATION = "ethical_violation"
    SECURITY_BREACH = "security_breach"
    SYSTEM_OVERLOAD = "system_overload"

@dataclass
class SafetyViolation:
    """Represents a safety violation"""
    violation_id: str
    violation_type: ViolationType
    risk_level: RiskLevel
    source: str  # What triggered the violation
    description: str
    detected_at: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    auto_resolved: bool = False
    resolution_actions: List[str] = field(default_factory=list)
    resolved_at: Optional[datetime] = None

@dataclass
class SafetyRule:
    """Safety rule definition"""
    rule_id: str
    rule_name: str
    description: str
    rule_type: str  # resource, time, protocol, etc.
    conditions: Dict[str, Any]
    action: str  # warn, pause, stop, emergency
    enabled: bool = True

@dataclass
class EmergencyProtocol:
    """Emergency response protocol"""
    protocol_id: str
    protocol_name: str
    trigger_conditions: List[str]
    emergency_actions: List[str]
    notification_targets: List[str]
    auto_execute: bool = True

class SafetyMonitor:
    """
    Real-time Safety Oversight Monitor
    
    Provides:
    - Continuous monitoring of research workflows
    - Real-time safety assessment
    - Automatic emergency intervention
    - Compliance validation
    - Risk assessment and mitigation
    """
    
    def __init__(self):
        # Monitoring state
        self.is_monitoring = False
        self.monitored_cycles: Dict[str, AutomatedResearchCycle] = {}
        self.monitored_projects: Dict[str, ResearchProject] = {}
        
        # Safety tracking
        self.active_violations: Dict[str, SafetyViolation] = {}
        self.violation_history: List[SafetyViolation] = []
        self.system_safety_status = SafetyStatus.SAFE
        
        # Safety rules and protocols
        self.safety_rules: Dict[str, SafetyRule] = {}
        self.emergency_protocols: Dict[str, EmergencyProtocol] = {}
        
        # Monitoring configuration
        self.monitoring_interval_seconds = 5
        self.risk_assessment_interval_seconds = 30
        self.violation_retention_hours = 168  # 7 days
        
        # Thresholds
        self.resource_thresholds = {
            "cpu_percent": 85.0,
            "memory_percent": 80.0,
            "disk_percent": 90.0,
            "network_mbps": 100.0
        }
        
        self.time_thresholds = {
            "step_timeout_multiplier": 3.0,  # 3x estimated duration
            "cycle_timeout_hours": 24.0,
            "agent_response_timeout_minutes": 10.0
        }
        
        # Event handlers
        self.safety_event_handlers: Dict[str, List[Callable]] = {
            "violation_detected": [],
            "emergency_triggered": [],
            "safety_status_changed": [],
            "system_recovered": []
        }
        
        # Statistics
        self.safety_stats = {
            "violations_detected": 0,
            "emergencies_triggered": 0,
            "auto_resolutions": 0,
            "uptime_hours": 0.0,
            "mean_time_to_resolution_minutes": 0.0
        }
        
        # Background tasks
        self._monitor_task: Optional[asyncio.Task] = None
        self._assessment_task: Optional[asyncio.Task] = None
        
        # Initialize default safety rules and protocols
        self._initialize_safety_rules()
        self._initialize_emergency_protocols()
    
    def _initialize_safety_rules(self):
        """Initialize default safety rules"""
        
        # Resource usage rules
        self.safety_rules["cpu_usage_limit"] = SafetyRule(
            rule_id="cpu_usage_limit",
            rule_name="CPU Usage Limit",
            description="Monitor CPU usage and trigger warnings at high levels",
            rule_type="resource",
            conditions={"cpu_percent": {"max": 85}},
            action="warn"
        )
        
        self.safety_rules["memory_usage_limit"] = SafetyRule(
            rule_id="memory_usage_limit", 
            rule_name="Memory Usage Limit",
            description="Monitor memory usage and trigger emergency at critical levels",
            rule_type="resource",
            conditions={"memory_percent": {"max": 90}},
            action="emergency"
        )
        
        # Time-based rules
        self.safety_rules["step_timeout"] = SafetyRule(
            rule_id="step_timeout",
            rule_name="Workflow Step Timeout",
            description="Detect workflow steps that exceed expected duration",
            rule_type="time",
            conditions={"duration_multiplier": {"max": 3.0}},
            action="pause"
        )
        
        self.safety_rules["cycle_timeout"] = SafetyRule(
            rule_id="cycle_timeout",
            rule_name="Research Cycle Timeout", 
            description="Detect research cycles that run too long",
            rule_type="time",
            conditions={"hours": {"max": 24}},
            action="stop"
        )
        
        # Agent behavior rules
        self.safety_rules["agent_response_timeout"] = SafetyRule(
            rule_id="agent_response_timeout",
            rule_name="Agent Response Timeout",
            description="Detect unresponsive agents",
            rule_type="agent",
            conditions={"response_time_minutes": {"max": 10}},
            action="warn"
        )
        
        # Protocol compliance rules
        self.safety_rules["safety_protocol_compliance"] = SafetyRule(
            rule_id="safety_protocol_compliance",
            rule_name="Safety Protocol Compliance",
            description="Ensure all experiments follow safety protocols",
            rule_type="protocol",
            conditions={"safety_approval": {"required": True}},
            action="stop"
        )
        
        logger.info(f"Initialized {len(self.safety_rules)} safety rules")
    
    def _initialize_emergency_protocols(self):
        """Initialize emergency response protocols"""
        
        # System overload protocol
        self.emergency_protocols["system_overload"] = EmergencyProtocol(
            protocol_id="system_overload",
            protocol_name="System Overload Emergency Response",
            trigger_conditions=["high_cpu_usage", "high_memory_usage", "resource_exhaustion"],
            emergency_actions=[
                "pause_all_non_critical_cycles",
                "notify_administrators",
                "initiate_graceful_shutdown",
                "save_current_state"
            ],
            notification_targets=["admin@research-institute.ai", "safety@research-institute.ai"],
            auto_execute=True
        )
        
        # Agent malfunction protocol
        self.emergency_protocols["agent_malfunction"] = EmergencyProtocol(
            protocol_id="agent_malfunction",
            protocol_name="Agent Malfunction Response",
            trigger_conditions=["agent_unresponsive", "agent_error_cascade", "agent_safety_violation"],
            emergency_actions=[
                "isolate_malfunctioning_agent",
                "pause_affected_workflows",
                "reassign_critical_tasks",
                "initiate_agent_recovery"
            ],
            notification_targets=["agent-team@research-institute.ai"],
            auto_execute=True
        )
        
        # Data integrity protocol
        self.emergency_protocols["data_integrity"] = EmergencyProtocol(
            protocol_id="data_integrity",
            protocol_name="Data Integrity Emergency Response",
            trigger_conditions=["data_corruption_detected", "security_breach", "unauthorized_access"],
            emergency_actions=[
                "stop_all_data_operations",
                "backup_current_state",
                "isolate_affected_systems",
                "initiate_forensic_analysis"
            ],
            notification_targets=["security@research-institute.ai", "data-team@research-institute.ai"],
            auto_execute=False  # Requires human approval
        )
        
        logger.info(f"Initialized {len(self.emergency_protocols)} emergency protocols")
    
    async def start_monitoring(self) -> None:
        """Start the safety monitoring system"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        self._assessment_task = asyncio.create_task(self._risk_assessment_loop())
        
        logger.info("Safety monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop the safety monitoring system"""
        self.is_monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
        if self._assessment_task:
            self._assessment_task.cancel()
        
        logger.info("Safety monitoring stopped")
    
    async def register_cycle(self, cycle: AutomatedResearchCycle) -> None:
        """Register a research cycle for monitoring"""
        self.monitored_cycles[cycle.cycle_id] = cycle
        logger.info(f"Registered cycle {cycle.cycle_id} for safety monitoring")
    
    async def unregister_cycle(self, cycle_id: str) -> None:
        """Unregister a research cycle from monitoring"""
        if cycle_id in self.monitored_cycles:
            del self.monitored_cycles[cycle_id]
            logger.info(f"Unregistered cycle {cycle_id} from safety monitoring")
    
    async def register_project(self, project: ResearchProject) -> None:
        """Register a research project for monitoring"""
        self.monitored_projects[project.id] = project
        logger.info(f"Registered project {project.id} for safety monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Main safety monitoring loop"""
        while self.is_monitoring:
            try:
                await self._check_safety_violations()
                await asyncio.sleep(self.monitoring_interval_seconds)
            except Exception as e:
                logger.error(f"Error in safety monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _risk_assessment_loop(self) -> None:
        """Periodic risk assessment loop"""
        while self.is_monitoring:
            try:
                await self._assess_system_risk()
                await asyncio.sleep(self.risk_assessment_interval_seconds)
            except Exception as e:
                logger.error(f"Error in risk assessment loop: {e}")
                await asyncio.sleep(10)
    
    async def _check_safety_violations(self) -> None:
        """Check for safety violations across all monitored systems"""
        # Check cycle safety
        for cycle_id, cycle in self.monitored_cycles.items():
            await self._check_cycle_safety(cycle)
        
        # Check project safety
        for project_id, project in self.monitored_projects.items():
            await self._check_project_safety(project)
        
        # Check system-wide safety
        await self._check_system_safety()
    
    async def _check_cycle_safety(self, cycle: AutomatedResearchCycle) -> None:
        """Check safety of a specific research cycle"""
        try:
            # Check time-based violations
            if cycle.started_at:
                runtime = datetime.utcnow() - cycle.started_at
                max_runtime_hours = self.time_thresholds["cycle_timeout_hours"]
                
                if runtime.total_seconds() / 3600 > max_runtime_hours:
                    await self._report_violation(
                        ViolationType.TIME_LIMIT,
                        RiskLevel.HIGH,
                        f"cycle_{cycle.cycle_id}",
                        f"Cycle {cycle.cycle_id} exceeded maximum runtime ({runtime.total_seconds() / 3600:.1f} hours)",
                        {"cycle_id": cycle.cycle_id, "runtime_hours": runtime.total_seconds() / 3600}
                    )
            
            # Check workflow state safety
            if cycle.state == WorkflowState.FAILED:
                await self._report_violation(
                    ViolationType.PROTOCOL_VIOLATION,
                    RiskLevel.MODERATE,
                    f"cycle_{cycle.cycle_id}",
                    f"Cycle {cycle.cycle_id} entered failed state",
                    {"cycle_id": cycle.cycle_id, "state": cycle.state.value}
                )
            
            # Check intervention flags
            if cycle.intervention_required:
                await self._report_violation(
                    ViolationType.AGENT_MALFUNCTION,
                    RiskLevel.HIGH,
                    f"cycle_{cycle.cycle_id}",
                    f"Cycle {cycle.cycle_id} requires human intervention",
                    {"cycle_id": cycle.cycle_id, "intervention_required": True}
                )
            
        except Exception as e:
            logger.error(f"Error checking cycle safety for {cycle.cycle_id}: {e}")
    
    async def _check_project_safety(self, project: ResearchProject) -> None:
        """Check safety of a specific research project"""
        try:
            # Check budget violations
            if hasattr(project, 'current_cost_usd') and hasattr(project, 'max_cost_usd'):
                if project.current_cost_usd > project.max_cost_usd:
                    await self._report_violation(
                        ViolationType.RESOURCE_LIMIT,
                        RiskLevel.MODERATE,
                        f"project_{project.id}",
                        f"Project {project.id} exceeded budget ({project.current_cost_usd} > {project.max_cost_usd})",
                        {"project_id": project.id, "budget_exceeded": True}
                    )
            
            # Check project state safety
            if project.state == ResearchState.FAILED:
                await self._report_violation(
                    ViolationType.PROTOCOL_VIOLATION,
                    RiskLevel.MODERATE,
                    f"project_{project.id}",
                    f"Project {project.id} entered failed state",
                    {"project_id": project.id, "state": project.state.value}
                )
            
        except Exception as e:
            logger.error(f"Error checking project safety for {project.id}: {e}")
    
    async def _check_system_safety(self) -> None:
        """Check system-wide safety conditions"""
        try:
            # Simulate system resource monitoring
            system_status = await self._get_system_status()
            
            # Check CPU usage
            cpu_percent = system_status.get("cpu_percent", 0)
            if cpu_percent > self.resource_thresholds["cpu_percent"]:
                await self._report_violation(
                    ViolationType.SYSTEM_OVERLOAD,
                    RiskLevel.HIGH if cpu_percent > 95 else RiskLevel.MODERATE,
                    "system_monitor",
                    f"High CPU usage detected: {cpu_percent}%",
                    {"cpu_percent": cpu_percent}
                )
            
            # Check memory usage
            memory_percent = system_status.get("memory_percent", 0)
            if memory_percent > self.resource_thresholds["memory_percent"]:
                await self._report_violation(
                    ViolationType.SYSTEM_OVERLOAD,
                    RiskLevel.CRITICAL if memory_percent > 95 else RiskLevel.HIGH,
                    "system_monitor",
                    f"High memory usage detected: {memory_percent}%",
                    {"memory_percent": memory_percent}
                )
            
        except Exception as e:
            logger.error(f"Error checking system safety: {e}")
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status (simulated)"""
        # In real implementation, would get actual system metrics
        import random
        return {
            "cpu_percent": random.uniform(20, 90),
            "memory_percent": random.uniform(30, 85),
            "disk_percent": random.uniform(40, 80),
            "network_mbps": random.uniform(10, 50),
            "active_connections": random.randint(50, 200)
        }
    
    async def _report_violation(self, violation_type: ViolationType, risk_level: RiskLevel,
                              source: str, description: str, context: Dict[str, Any] = None) -> None:
        """Report a safety violation"""
        violation_id = str(uuid4())
        
        violation = SafetyViolation(
            violation_id=violation_id,
            violation_type=violation_type,
            risk_level=risk_level,
            source=source,
            description=description,
            detected_at=datetime.utcnow(),
            context=context or {}
        )
        
        self.active_violations[violation_id] = violation
        self.violation_history.append(violation)
        self.safety_stats["violations_detected"] += 1
        
        logger.warning(f"Safety violation detected: {description} (Risk: {risk_level.value})")
        
        # Trigger automated response
        await self._handle_violation(violation)
        
        # Trigger event handlers
        await self._trigger_safety_event("violation_detected", violation)
    
    async def _handle_violation(self, violation: SafetyViolation) -> None:
        """Handle a safety violation with appropriate response"""
        try:
            # Find applicable safety rule
            applicable_rule = None
            for rule in self.safety_rules.values():
                if self._violation_matches_rule(violation, rule):
                    applicable_rule = rule
                    break
            
            if not applicable_rule:
                logger.warning(f"No applicable rule found for violation {violation.violation_id}")
                return
            
            # Execute rule action
            action = applicable_rule.action
            actions_taken = []
            
            if action == "warn":
                actions_taken.append("warning_issued")
                logger.warning(f"Safety warning: {violation.description}")
            
            elif action == "pause":
                actions_taken.extend(await self._pause_affected_operations(violation))
            
            elif action == "stop":
                actions_taken.extend(await self._stop_affected_operations(violation))
            
            elif action == "emergency":
                actions_taken.extend(await self._trigger_emergency_protocol(violation))
            
            violation.resolution_actions = actions_taken
            
            # Check if violation is auto-resolvable
            if await self._can_auto_resolve(violation):
                await self._auto_resolve_violation(violation)
            
        except Exception as e:
            logger.error(f"Error handling violation {violation.violation_id}: {e}")
    
    def _violation_matches_rule(self, violation: SafetyViolation, rule: SafetyRule) -> bool:
        """Check if a violation matches a safety rule"""
        # Simplified matching - in real implementation would be more sophisticated
        type_mapping = {
            ViolationType.RESOURCE_LIMIT: "resource",
            ViolationType.TIME_LIMIT: "time",
            ViolationType.AGENT_MALFUNCTION: "agent",
            ViolationType.PROTOCOL_VIOLATION: "protocol",
            ViolationType.SYSTEM_OVERLOAD: "resource"
        }
        
        return type_mapping.get(violation.violation_type) == rule.rule_type
    
    async def _pause_affected_operations(self, violation: SafetyViolation) -> List[str]:
        """Pause operations affected by a violation"""
        actions = []
        
        if "cycle_" in violation.source:
            cycle_id = violation.source.replace("cycle_", "")
            if cycle_id in self.monitored_cycles:
                cycle = self.monitored_cycles[cycle_id]
                cycle.state = WorkflowState.PAUSED
                actions.append(f"paused_cycle_{cycle_id}")
        
        if "project_" in violation.source:
            project_id = violation.source.replace("project_", "")
            if project_id in self.monitored_projects:
                project = self.monitored_projects[project_id]
                project.update_state(ResearchState.PAUSED, f"Safety pause: {violation.description}")
                actions.append(f"paused_project_{project_id}")
        
        return actions
    
    async def _stop_affected_operations(self, violation: SafetyViolation) -> List[str]:
        """Stop operations affected by a violation"""
        actions = []
        
        if "cycle_" in violation.source:
            cycle_id = violation.source.replace("cycle_", "")
            if cycle_id in self.monitored_cycles:
                cycle = self.monitored_cycles[cycle_id]
                cycle.state = WorkflowState.FAILED
                actions.append(f"stopped_cycle_{cycle_id}")
        
        if "project_" in violation.source:
            project_id = violation.source.replace("project_", "")
            if project_id in self.monitored_projects:
                project = self.monitored_projects[project_id]
                project.update_state(ResearchState.FAILED, f"Safety stop: {violation.description}")
                actions.append(f"stopped_project_{project_id}")
        
        return actions
    
    async def _trigger_emergency_protocol(self, violation: SafetyViolation) -> List[str]:
        """Trigger emergency protocols for critical violations"""
        actions = []
        
        # Find applicable emergency protocols
        applicable_protocols = []
        for protocol in self.emergency_protocols.values():
            if self._violation_triggers_protocol(violation, protocol):
                applicable_protocols.append(protocol)
        
        for protocol in applicable_protocols:
            if protocol.auto_execute:
                await self._execute_emergency_protocol(protocol, violation)
                actions.append(f"executed_emergency_protocol_{protocol.protocol_id}")
                self.safety_stats["emergencies_triggered"] += 1
        
        # Update system safety status
        self.system_safety_status = SafetyStatus.EMERGENCY
        await self._trigger_safety_event("emergency_triggered", {"violation": violation, "protocols": applicable_protocols})
        
        return actions
    
    def _violation_triggers_protocol(self, violation: SafetyViolation, protocol: EmergencyProtocol) -> bool:
        """Check if a violation triggers an emergency protocol"""
        # Simplified trigger matching
        trigger_mapping = {
            ViolationType.SYSTEM_OVERLOAD: ["high_cpu_usage", "high_memory_usage", "resource_exhaustion"],
            ViolationType.AGENT_MALFUNCTION: ["agent_unresponsive", "agent_error_cascade", "agent_safety_violation"],
            ViolationType.DATA_CORRUPTION: ["data_corruption_detected"],
            ViolationType.SECURITY_BREACH: ["security_breach", "unauthorized_access"]
        }
        
        violation_triggers = trigger_mapping.get(violation.violation_type, [])
        return any(trigger in protocol.trigger_conditions for trigger in violation_triggers)
    
    async def _execute_emergency_protocol(self, protocol: EmergencyProtocol, violation: SafetyViolation) -> None:
        """Execute an emergency protocol"""
        logger.critical(f"Executing emergency protocol: {protocol.protocol_name}")
        
        for action in protocol.emergency_actions:
            await self._execute_emergency_action(action, violation)
        
        # Send notifications (simulated)
        for target in protocol.notification_targets:
            await self._send_emergency_notification(target, protocol, violation)
    
    async def _execute_emergency_action(self, action: str, violation: SafetyViolation) -> None:
        """Execute a specific emergency action"""
        if action == "pause_all_non_critical_cycles":
            for cycle in self.monitored_cycles.values():
                if cycle.state == WorkflowState.EXECUTING:
                    cycle.state = WorkflowState.PAUSED
        
        elif action == "stop_all_data_operations":
            # Simulate stopping data operations
            logger.critical("Stopping all data operations")
        
        elif action == "backup_current_state":
            # Simulate state backup
            logger.info("Backing up current system state")
        
        elif action == "isolate_malfunctioning_agent":
            # Simulate agent isolation
            if "cycle_" in violation.source:
                logger.info(f"Isolating agent for {violation.source}")
        
        # Add more emergency actions as needed
        logger.info(f"Executed emergency action: {action}")
    
    async def _send_emergency_notification(self, target: str, protocol: EmergencyProtocol, violation: SafetyViolation) -> None:
        """Send emergency notification (simulated)"""
        message = {
            "alert": "EMERGENCY PROTOCOL TRIGGERED",
            "protocol": protocol.protocol_name,
            "violation": violation.description,
            "risk_level": violation.risk_level.value,
            "timestamp": violation.detected_at.isoformat(),
            "actions_taken": violation.resolution_actions
        }
        
        # In real implementation, would send actual notifications
        logger.critical(f"Emergency notification to {target}: {json.dumps(message, indent=2)}")
    
    async def _can_auto_resolve(self, violation: SafetyViolation) -> bool:
        """Check if a violation can be automatically resolved"""
        # Define auto-resolvable violation types
        auto_resolvable = {
            ViolationType.TIME_LIMIT,
            ViolationType.RESOURCE_LIMIT
        }
        
        return violation.violation_type in auto_resolvable
    
    async def _auto_resolve_violation(self, violation: SafetyViolation) -> None:
        """Automatically resolve a violation"""
        violation.auto_resolved = True
        violation.resolved_at = datetime.utcnow()
        
        # Remove from active violations
        if violation.violation_id in self.active_violations:
            del self.active_violations[violation.violation_id]
        
        self.safety_stats["auto_resolutions"] += 1
        logger.info(f"Auto-resolved violation {violation.violation_id}: {violation.description}")
    
    async def _assess_system_risk(self) -> None:
        """Assess overall system risk level"""
        try:
            # Calculate risk based on active violations
            risk_scores = []
            
            for violation in self.active_violations.values():
                risk_mapping = {
                    RiskLevel.MINIMAL: 0.1,
                    RiskLevel.LOW: 0.3,
                    RiskLevel.MODERATE: 0.5,
                    RiskLevel.HIGH: 0.8,
                    RiskLevel.CRITICAL: 1.0
                }
                risk_scores.append(risk_mapping[violation.risk_level])
            
            # Calculate overall risk
            if not risk_scores:
                overall_risk = RiskLevel.MINIMAL
                new_status = SafetyStatus.SAFE
            else:
                avg_risk = sum(risk_scores) / len(risk_scores)
                max_risk = max(risk_scores)
                
                # Use maximum risk for safety status
                if max_risk >= 0.8:
                    overall_risk = RiskLevel.CRITICAL
                    new_status = SafetyStatus.EMERGENCY
                elif max_risk >= 0.6:
                    overall_risk = RiskLevel.HIGH
                    new_status = SafetyStatus.CRITICAL
                elif max_risk >= 0.4:
                    overall_risk = RiskLevel.MODERATE
                    new_status = SafetyStatus.WARNING
                else:
                    overall_risk = RiskLevel.LOW
                    new_status = SafetyStatus.SAFE
            
            # Update safety status if changed
            if new_status != self.system_safety_status:
                old_status = self.system_safety_status
                self.system_safety_status = new_status
                await self._trigger_safety_event("safety_status_changed", {
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "overall_risk": overall_risk.value
                })
                
                logger.info(f"System safety status changed: {old_status.value} → {new_status.value}")
        
        except Exception as e:
            logger.error(f"Error assessing system risk: {e}")
    
    async def _trigger_safety_event(self, event_type: str, data: Any) -> None:
        """Trigger safety event handlers"""
        handlers = self.safety_event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in safety event handler for {event_type}: {e}")
    
    def register_safety_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register a safety event handler"""
        if event_type not in self.safety_event_handlers:
            self.safety_event_handlers[event_type] = []
        self.safety_event_handlers[event_type].append(handler)
    
    async def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status"""
        return {
            "system_safety_status": self.system_safety_status.value,
            "active_violations": len(self.active_violations),
            "total_violations": len(self.violation_history),
            "monitored_cycles": len(self.monitored_cycles),
            "monitored_projects": len(self.monitored_projects),
            "safety_rules": len(self.safety_rules),
            "emergency_protocols": len(self.emergency_protocols),
            "statistics": self.safety_stats
        }
    
    async def get_violation_details(self, violation_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific violation"""
        violation = self.active_violations.get(violation_id)
        if not violation:
            # Check history
            for hist_violation in self.violation_history:
                if hist_violation.violation_id == violation_id:
                    violation = hist_violation
                    break
        
        if not violation:
            return None
        
        return {
            "violation_id": violation.violation_id,
            "violation_type": violation.violation_type.value,
            "risk_level": violation.risk_level.value,
            "source": violation.source,
            "description": violation.description,
            "detected_at": violation.detected_at.isoformat(),
            "resolved_at": violation.resolved_at.isoformat() if violation.resolved_at else None,
            "auto_resolved": violation.auto_resolved,
            "resolution_actions": violation.resolution_actions,
            "context": violation.context
        }
    
    async def resolve_violation(self, violation_id: str, resolution_note: str = "") -> bool:
        """Manually resolve a violation"""
        if violation_id not in self.active_violations:
            return False
        
        violation = self.active_violations[violation_id]
        violation.resolved_at = datetime.utcnow()
        violation.resolution_actions.append(f"manually_resolved: {resolution_note}")
        
        del self.active_violations[violation_id]
        
        logger.info(f"Manually resolved violation {violation_id}: {resolution_note}")
        return True 