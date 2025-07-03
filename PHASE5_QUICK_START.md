# Phase 5 Quick Start Guide: Dashboard for Test Workflow Execution

## Immediate Priority: Test Workflow Dashboard

Since you want to run test workflows through the dashboard, here's the recommended implementation order:

### 1. Core Infrastructure (3-4 days)
**Goal**: Basic dashboard that can communicate with existing Phase 4 system

```bash
# Create dashboard structure
mkdir -p dashboard/{frontend,backend,shared}
mkdir -p dashboard/frontend/src/{components,pages,services,store,utils,types}
```

**Key Components:**
- FastAPI dashboard API extension
- WebSocket handler for real-time updates
- React frontend with basic routing
- Connection to existing Phase 4 components

### 2. E2E Test Runner Interface (2-3 days)
**Goal**: Run existing test workflows from web interface

**Features:**
- Execute `test_e2e_demo.py` from dashboard
- Real-time test progress updates
- Test result visualization
- Test log streaming

### 3. System Status Monitor (2-3 days)
**Goal**: Monitor Phase 4 components while tests run

**Features:**
- Component health indicators
- Live performance metrics
- Active workflow visualization
- Safety status monitoring

### 4. Workflow Control Interface (3-4 days)
**Goal**: Start, monitor, and control research workflows

**Features:**
- Create new research projects
- Start automated research cycles
- Monitor workflow progress
- Emergency stop functionality

## Recommended Tech Stack for Quick Implementation

### Frontend (React + TypeScript)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "@chakra-ui/react": "^2.8.0",
    "socket.io-client": "^4.7.0",
    "react-router-dom": "^6.15.0",
    "axios": "^1.5.0",
    "recharts": "^2.8.0"
  }
}
```

### Backend Extensions
```python
# Additional dependencies for dashboard
fastapi-socketio==0.0.10
python-socketio==5.8.0
psutil==5.9.5  # For system metrics
```

## Implementation Steps

### Step 1: Backend API Extension (Day 1-2)
1. **Create `dashboard/backend/dashboard_api.py`**
   - Add dashboard-specific FastAPI routes
   - Integrate with existing Phase 4 components
   - Add system metrics collection

2. **Create `dashboard/backend/websocket_handler.py`**
   - Real-time event broadcasting
   - Test progress updates
   - System status updates

### Step 2: Frontend Setup (Day 2-3)
1. **Initialize React project**
   ```bash
   cd dashboard/frontend
   npx create-react-app . --template typescript
   ```

2. **Setup basic layout and routing**
   - Dashboard header with navigation
   - Test runner page
   - System monitor page
   - Workflow management page

### Step 3: Test Runner Integration (Day 3-4)
1. **Test Execution Interface**
   - Button to run E2E test suite
   - Real-time progress bar
   - Test result display
   - Log streaming

2. **Connect to existing test infrastructure**
   - Execute `test_e2e_demo.py` subprocess
   - Stream test output to frontend
   - Parse test results for visualization

### Step 4: System Monitoring (Day 4-5)
1. **Component Status Cards**
   - Workflow Engine status
   - Task Scheduler status
   - Safety Monitor status
   - Quality System status

2. **Real-time Metrics**
   - CPU and memory usage
   - Active tasks count
   - Agent status
   - Performance indicators

## File Structure for Quick Start
```
dashboard/
├── backend/
│   ├── __init__.py
│   ├── dashboard_api.py      # FastAPI dashboard routes
│   ├── websocket_handler.py  # Real-time updates
│   ├── test_runner.py        # E2E test execution
│   └── metrics_collector.py  # System metrics
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TestRunner.tsx
│   │   │   ├── SystemMonitor.tsx
│   │   │   └── WorkflowControl.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Testing.tsx
│   │   │   └── Workflows.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   └── App.tsx
│   └── package.json
└── shared/
    ├── events.py           # WebSocket event definitions
    └── schemas.py          # Shared data models
```

## MVP Features (Week 1 Target)

### Test Runner Dashboard
- ✅ **Execute E2E Tests**: Run `test_e2e_demo.py` from web interface
- ✅ **Real-time Progress**: Live updates during test execution
- ✅ **Results Display**: Show test results with pass/fail status
- ✅ **Log Streaming**: Live test output and error logs

### System Monitor
- ✅ **Component Health**: Status indicators for all Phase 4 components
- ✅ **Basic Metrics**: CPU, memory, active tasks
- ✅ **Connection Status**: WebSocket connection health

### Workflow Control (Basic)
- ✅ **Start Research Cycle**: Create and start new research projects
- ✅ **Monitor Progress**: Real-time workflow step completion
- ✅ **Stop/Pause**: Emergency controls for running workflows

## Development Workflow

### Day 1: Backend Foundation
```bash
# 1. Create dashboard backend structure
# 2. Implement basic FastAPI dashboard API
# 3. Add WebSocket handler for real-time updates
# 4. Test integration with Phase 4 components
```

### Day 2: Test Runner Backend
```bash
# 1. Create test execution service
# 2. Add endpoints for starting/monitoring tests
# 3. Implement test result parsing
# 4. Add WebSocket events for test progress
```

### Day 3: Frontend Setup
```bash
# 1. Initialize React TypeScript project
# 2. Setup Chakra UI and routing
# 3. Create basic layout and navigation
# 4. Implement WebSocket connection
```

### Day 4: Test Runner UI
```bash
# 1. Create TestRunner component
# 2. Add test execution controls
# 3. Implement real-time progress display
# 4. Add test result visualization
```

### Day 5: System Monitor UI
```bash
# 1. Create SystemMonitor component
# 2. Add component status cards
# 3. Implement real-time metrics display
# 4. Add basic workflow visualization
```

## Success Metrics

### Week 1 Goals
- [ ] Dashboard loads and connects to backend ✅
- [ ] Can execute E2E test suite from web interface ✅
- [ ] Real-time test progress updates working ✅
- [ ] System component status monitoring ✅
- [ ] Basic workflow start/stop functionality ✅

### Performance Targets
- Dashboard loads in <3 seconds
- Real-time updates with <2 second delay
- Test execution starts within 5 seconds of button click
- System metrics update every 5 seconds

## Ready to Start?

The plan is optimized for getting you a working test workflow dashboard as quickly as possible. The foundation will support adding more advanced features later.

**Next Step**: Should I start implementing the backend dashboard API (`dashboard/backend/dashboard_api.py`) that integrates with your existing Phase 4 system?

This will give you:
1. API endpoints to control test execution
2. WebSocket for real-time updates
3. Integration with existing workflow engine, safety monitor, and quality system
4. Foundation for the React frontend

Let me know if you'd like to begin with this approach or if you'd prefer to focus on any specific component first!
