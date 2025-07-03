"""
Dashboard Test Runner - Execute E2E tests from web interface
"""

import asyncio
import subprocess
import logging
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from dashboard.shared.events import create_test_progress_event


logger = logging.getLogger(__name__)


class DashboardTestRunner:
    """Execute and monitor test suites from dashboard"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.running_tests: Dict[str, Dict[str, Any]] = {}
        logger.info("Dashboard test runner initialized")
    
    async def run_test_suite(
        self,
        test_id: str,
        test_suite: str = "e2e_demo",
        test_scenarios: Optional[List[str]] = None,
        parameters: Dict[str, Any] = None
    ):
        """Run a test suite and stream results"""
        try:
            logger.info(f"Starting test suite {test_suite} with ID {test_id}")
            
            # Track test execution
            self.running_tests[test_id] = {
                "test_suite": test_suite,
                "status": "running",
                "start_time": datetime.now(),
                "progress": 0.0,
                "current_phase": "initialization",
                "results": {}
            }
            
            # Send test started event
            await self._send_test_event(
                test_id, "Test Suite Started", 0.0, "initialization"
            )
            
            # Determine test file to run
            test_file = self._get_test_file(test_suite)
            if not test_file:
                raise ValueError(f"Unknown test suite: {test_suite}")
            
            # Execute test in subprocess
            await self._execute_test_subprocess(test_id, test_file)
            
        except Exception as e:
            logger.error(f"Error running test suite {test_id}: {e}")
            if test_id in self.running_tests:
                self.running_tests[test_id]["status"] = "failed"
                self.running_tests[test_id]["error"] = str(e)
            
            await self._send_test_event(
                test_id, "Test Suite Failed", 0.0, "error", {"error": str(e)}
            )
    
    def _get_test_file(self, test_suite: str) -> Optional[str]:
        """Get test file path for test suite"""
        test_files = {
            "e2e_demo": "test_e2e_demo.py",
            "phase4_standalone": "test_phase4_standalone.py",
            "phase4_mock": "test_phase4_mock.py",
            "phase4": "test_phase4.py"
        }
        return test_files.get(test_suite)
    
    async def _execute_test_subprocess(self, test_id: str, test_file: str):
        """Execute test file in subprocess"""
        try:
            # Update progress
            self.running_tests[test_id]["current_phase"] = "executing"
            self.running_tests[test_id]["progress"] = 10.0
            await self._send_test_event(
                test_id, "Test Execution", 10.0, "executing"
            )
            
            # Build command
            cmd = ["python", "-m", "pytest", test_file, "-v", "--tb=short"]
            
            # Start subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=os.getcwd()
            )
            
            # Stream output
            output_lines = []
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                line_str = line.decode('utf-8').strip()
                output_lines.append(line_str)
                
                # Parse progress from output
                progress = self._parse_test_progress(line_str, output_lines)
                if progress > self.running_tests[test_id]["progress"]:
                    self.running_tests[test_id]["progress"] = progress
                    await self._send_test_event(
                        test_id, "Test Progress", progress, "executing",
                        {"current_output": line_str}
                    )
            
            # Wait for completion
            return_code = await process.wait()
            
            # Update final status
            if return_code == 0:
                self.running_tests[test_id]["status"] = "passed"
                self.running_tests[test_id]["progress"] = 100.0
                await self._send_test_event(
                    test_id, "Test Suite Completed", 100.0, "completed",
                    {"return_code": return_code, "output": output_lines}
                )
            else:
                self.running_tests[test_id]["status"] = "failed"
                await self._send_test_event(
                    test_id, "Test Suite Failed", 0.0, "failed",
                    {"return_code": return_code, "output": output_lines}
                )
            
            self.running_tests[test_id]["completion_time"] = datetime.now()
            self.running_tests[test_id]["results"] = {
                "return_code": return_code,
                "output_lines": len(output_lines),
                "success": return_code == 0
            }
            
            logger.info(f"Test {test_id} completed with return code {return_code}")
            
        except Exception as e:
            logger.error(f"Error executing test subprocess: {e}")
            self.running_tests[test_id]["status"] = "failed"
            self.running_tests[test_id]["error"] = str(e)
            await self._send_test_event(
                test_id, "Test Execution Error", 0.0, "error", {"error": str(e)}
            )
    
    def _parse_test_progress(self, line: str, all_lines: List[str]) -> float:
        """Parse test progress from output line"""
        try:
            # Simple progress estimation based on output patterns
            if "PASSED" in line or "FAILED" in line:
                # Count completed tests
                completed = sum(1 for l in all_lines if "PASSED" in l or "FAILED" in l)
                # Estimate total tests (rough approximation)
                total_estimated = max(completed + 1, 10)
                return min((completed / total_estimated) * 90, 90.0)
            
            elif "test session starts" in line.lower():
                return 5.0
            elif "collecting" in line.lower():
                return 15.0
            elif "collected" in line.lower():
                return 25.0
            
            return self.running_tests.get(self.test_id, {}).get("progress", 0.0)
            
        except Exception:
            return 0.0
    
    async def _send_test_event(
        self,
        test_id: str,
        test_name: str,
        progress: float,
        phase: str,
        results: Optional[Dict[str, Any]] = None
    ):
        """Send test progress event via WebSocket"""
        try:
            if self.websocket_manager:
                event = create_test_progress_event(
                    test_id, test_name, progress, phase, results
                )
                await self.websocket_manager.broadcast(event.dict())
                
        except Exception as e:
            logger.error(f"Error sending test event: {e}")
    
    async def get_test_status(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get status of running test"""
        return self.running_tests.get(test_id)
    
    async def get_all_tests(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tests"""
        return self.running_tests.copy()
    
    async def stop_test(self, test_id: str) -> bool:
        """Stop a running test"""
        try:
            if test_id in self.running_tests:
                self.running_tests[test_id]["status"] = "stopped"
                self.running_tests[test_id]["completion_time"] = datetime.now()
                
                await self._send_test_event(
                    test_id, "Test Stopped", 0.0, "stopped"
                )
                
                logger.info(f"Stopped test {test_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error stopping test {test_id}: {e}")
            return False
