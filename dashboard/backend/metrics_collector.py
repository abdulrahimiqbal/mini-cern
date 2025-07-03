"""
System Metrics Collector for Dashboard
"""

import asyncio
import psutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class SystemMetricsCollector:
    """Collects system performance metrics"""
    
    def __init__(self):
        self.is_running = False
        self.last_network_stats = None
        logger.info("System metrics collector initialized")
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            metrics = {}
            
            # CPU usage
            metrics["cpu_usage"] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics["memory_usage"] = memory.percent
            metrics["memory_total_gb"] = memory.total / (1024**3)
            metrics["memory_used_gb"] = memory.used / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            metrics["disk_usage"] = (disk.used / disk.total) * 100
            metrics["disk_total_gb"] = disk.total / (1024**3)
            metrics["disk_used_gb"] = disk.used / (1024**3)
            
            # Network I/O
            network = psutil.net_io_counters()
            if self.last_network_stats:
                metrics["network_bytes_sent_delta"] = network.bytes_sent - self.last_network_stats.bytes_sent
                metrics["network_bytes_recv_delta"] = network.bytes_recv - self.last_network_stats.bytes_recv
            else:
                metrics["network_bytes_sent_delta"] = 0
                metrics["network_bytes_recv_delta"] = 0
            
            self.last_network_stats = network
            metrics["network_bytes_sent"] = network.bytes_sent
            metrics["network_bytes_recv"] = network.bytes_recv
            
            # Process count
            metrics["process_count"] = len(psutil.pids())
            
            # Load average (Unix-like systems)
            try:
                load_avg = psutil.getloadavg()
                metrics["load_1min"] = load_avg[0]
                metrics["load_5min"] = load_avg[1]
                metrics["load_15min"] = load_avg[2]
            except AttributeError:
                # Windows doesn't have load average
                metrics["load_1min"] = 0.0
                metrics["load_5min"] = 0.0
                metrics["load_15min"] = 0.0
            
            # Simulated application metrics
            metrics["active_tasks"] = 0
            metrics["queue_length"] = 0
            metrics["response_time"] = 50.0  # milliseconds
            metrics["total_agents"] = 6
            metrics["error_count"] = 0
            
            # Timestamp
            metrics["timestamp"] = datetime.now().isoformat()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def start(self):
        """Start periodic metrics collection"""
        self.is_running = True
        logger.info("Started system metrics collection")
    
    async def stop(self):
        """Stop metrics collection"""
        self.is_running = False
        logger.info("Stopped system metrics collection")
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get static system information"""
        try:
            info = {}
            
            # System info
            info["platform"] = psutil.LINUX if hasattr(psutil, 'LINUX') else "unknown"
            info["cpu_count"] = psutil.cpu_count()
            info["cpu_count_logical"] = psutil.cpu_count(logical=True)
            
            # Memory info
            memory = psutil.virtual_memory()
            info["memory_total_gb"] = memory.total / (1024**3)
            
            # Disk info
            disk = psutil.disk_usage('/')
            info["disk_total_gb"] = disk.total / (1024**3)
            
            # Boot time
            info["boot_time"] = datetime.fromtimestamp(psutil.boot_time()).isoformat()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}
