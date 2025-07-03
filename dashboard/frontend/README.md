# Science Research Institute - Dashboard Frontend

## Overview

This is the React TypeScript frontend for the Science Research Institute dashboard. It provides a modern web interface to monitor, control, and interact with the AI-driven physics research system.

## Features

### 🎛️ **Dashboard**
- Real-time system overview
- Component health monitoring
- Performance metrics (CPU, memory, response time)
- Agent status tracking

### 🧪 **Test Runner**
- Execute E2E test suites from the web interface
- Real-time test progress tracking
- Live test logs streaming
- Test results visualization

### 🔄 **Workflow Management**
- Create and manage research workflows
- Monitor workflow progress
- Start/pause/resume workflow controls
- Workflow status tracking

### 📊 **System Monitoring**
- Detailed component health status
- Real-time performance metrics
- Agent registry monitoring
- Safety system status

## Technology Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Chakra UI** - Modern component library
- **Socket.io Client** - Real-time WebSocket communication
- **Axios** - HTTP client for API calls

## Setup Instructions

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Open browser:**
   Navigate to `http://localhost:5173`

### Backend Connection

The frontend connects to the backend API at `http://localhost:8000`. Make sure the backend server is running:

```bash
# From the project root
python3 dashboard_server.py
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/
│   └── Layout.tsx          # Main layout with navigation
├── pages/
│   ├── Dashboard.tsx       # System overview dashboard
│   ├── Testing.tsx         # E2E test runner interface
│   ├── Workflows.tsx       # Workflow management
│   └── Monitoring.tsx      # Detailed system monitoring
├── services/
│   ├── api.ts             # API service layer
│   └── websocket.ts       # WebSocket service
├── types/
│   └── index.ts           # TypeScript type definitions
├── App.tsx                # Main app component
└── main.tsx              # React entry point
```

## API Integration

The frontend integrates with the following backend endpoints:

### REST API
- `GET /api/health` - Health check
- `GET /api/dashboard/overview` - System overview
- `GET /api/dashboard/workflows` - Workflow list
- `POST /api/dashboard/workflows/start` - Start workflow
- `POST /api/dashboard/testing/run-suite` - Run tests
- `GET /api/dashboard/agents` - Agent status
- `GET /api/dashboard/safety` - Safety status

### WebSocket Events
- `system_metrics` - Real-time system metrics
- `component_status` - Component health updates
- `test_progress` - Test execution progress
- `workflow_update` - Workflow status changes

## Real-time Features

The dashboard uses WebSocket connections for real-time updates:

- **Live Metrics**: CPU, memory, and performance data
- **Test Progress**: Real-time test execution updates
- **Component Health**: Instant health status changes
- **Workflow Updates**: Live workflow progress tracking

## Development

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `App.tsx`
3. Add navigation item in `Layout.tsx`

### API Integration

Use the `apiService` from `src/services/api.ts`:

```typescript
import apiService from '../services/api'

// Example usage
const data = await apiService.getSystemOverview()
```

### WebSocket Integration

Use the `websocketService` from `src/services/websocket.ts`:

```typescript
import websocketService from '../services/websocket'

// Subscribe to events
websocketService.subscribe('system_metrics', (event) => {
  console.log('Metrics update:', event.data)
})
```

## Deployment

### Production Build

```bash
npm run build
```

This creates a `dist/` folder with production-ready files.

### Deployment Options

1. **Static Hosting**: Deploy `dist/` folder to any static host
2. **Docker**: Use the included Dockerfile
3. **CDN**: Upload to CDN for global distribution

## Troubleshooting

### Common Issues

**Frontend won't start:**
- Check Node.js version (18+)
- Clear node_modules: `rm -rf node_modules && npm install`

**API connection fails:**
- Ensure backend is running on `localhost:8000`
- Check CORS settings in backend
- Verify network connectivity

**WebSocket not connecting:**
- Check backend WebSocket support
- Verify port 8000 is accessible
- Check browser console for errors

**Build fails:**
- Check TypeScript errors: `npm run lint`
- Clear cache: `npm run build -- --force`

## Contributing

1. Follow TypeScript best practices
2. Use Chakra UI components consistently
3. Add proper error handling
4. Update type definitions as needed
5. Test WebSocket integration thoroughly

## License

Part of the Science Research Institute project. See main project LICENSE.
