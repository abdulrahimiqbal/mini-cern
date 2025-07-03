"""
Main Dashboard Server - Launch point for the web dashboard
"""

import asyncio
import uvicorn
import logging
from dashboard.backend.dashboard_api import app
from dashboard.backend.websocket_handler import WebSocketManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point for dashboard server"""
    logger.info("Starting Science Research Institute Dashboard Server...")
    
    # Configuration
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,  # Set to True for development
        access_log=True
    )
    
    # Create and run server
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Dashboard server stopped by user")
    except Exception as e:
        logger.error(f"Dashboard server error: {e}")
        raise
